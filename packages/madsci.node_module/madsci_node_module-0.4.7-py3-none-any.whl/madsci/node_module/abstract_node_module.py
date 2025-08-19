"""Base Node Module helper classes."""

import contextlib
import inspect
import threading
import traceback
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from madsci.client.data_client import DataClient
from madsci.client.event_client import (
    EventClient,
)
from madsci.client.node.abstract_node_client import AbstractNodeClient
from madsci.client.resource_client import ResourceClient
from madsci.common.exceptions import (
    ActionNotImplementedError,
)
from madsci.common.ownership import global_ownership_info
from madsci.common.types.action_types import (
    ActionDefinition,
    ActionRequest,
    ActionResult,
    ActionStatus,
    ArgumentDefinition,
    FileArgumentDefinition,
    LocationArgumentDefinition,
)
from madsci.common.types.admin_command_types import AdminCommandResponse
from madsci.common.types.base_types import Error
from madsci.common.types.context_types import MadsciContext
from madsci.common.types.event_types import Event, EventType
from madsci.common.types.location_types import (
    LocationArgument,
)
from madsci.common.types.node_types import (
    AdminCommands,
    NodeCapabilities,
    NodeClientCapabilities,
    NodeConfig,
    NodeDefinition,
    NodeInfo,
    NodeSetConfigResponse,
    NodeStatus,
)
from madsci.common.utils import (
    is_optional,
    pretty_type_repr,
    repeat_on_interval,
    threaded_daemon,
    to_snake_case,
)
from pydantic import ValidationError
from semver import Version


class AbstractNode:
    """
    Base Node implementation, protocol agnostic, all node class definitions should inherit from or be based on this.

    Note that this class is abstract: it is intended to be inherited from, not used directly.
    """

    node_definition: ClassVar[NodeDefinition] = None
    """The node definition."""
    node_status: ClassVar[NodeStatus] = NodeStatus(
        initializing=True,
    )
    """The status of the node."""
    node_state: ClassVar[dict[str, Any]] = {}
    """The state of the node."""
    action_handlers: ClassVar[dict[str, callable]] = {}
    """The handlers for the actions that the node supports."""
    action_history: ClassVar[dict[str, list[ActionResult]]] = {}
    """The history of the actions that the node has performed."""
    logger: ClassVar[EventClient] = EventClient()
    """The event logger for this node"""
    module_version: ClassVar[str] = "0.0.1"
    """The version of the module. Should match the version in the node definition."""
    supported_capabilities: ClassVar[NodeClientCapabilities] = (
        AbstractNodeClient.supported_capabilities
    )
    """The default supported capabilities of this node module class."""
    config: ClassVar[NodeConfig] = NodeConfig()
    """The node configuration."""
    config_model: ClassVar[type[NodeConfig]] = NodeConfig
    """The node config model class. This is the class that will be used to instantiate self.config."""
    context: ClassVar[MadsciContext] = MadsciContext()
    """The context for the node. This allows the node to access the MADSci context, including the event client and resource client."""
    _action_lock: ClassVar[threading.Lock] = threading.Lock()
    """Ensures only one blocking action can run at a time."""

    def __init__(
        self,
        node_definition: Optional[NodeDefinition] = None,
        node_config: Optional[NodeConfig] = None,
    ) -> "AbstractNode":
        """Initialize the node class."""

        self.config = node_config or self.config
        if not self.config:
            self.config = self.config_model()
        self.node_definition = node_definition
        if self.node_definition is None:
            node_definition_path = getattr(
                self.config, "node_definition", "default.node.yaml"
            )
            if not Path(node_definition_path).exists():
                self.logger.log_warning(
                    f"Node definition file '{node_definition_path}' not found, using default node definition."
                )
                module_name = to_snake_case(self.__class__.__name__)
                node_name = str(Path(node_definition_path).stem)
                self.node_definition = NodeDefinition(
                    node_name=node_name, module_name=module_name
                )
            else:
                self.node_definition = NodeDefinition.from_yaml(node_definition_path)
        global_ownership_info.node_id = self.node_definition.node_id
        self._configure_clients()

        # * Check Node Version
        if (
            Version.parse(self.module_version).compare(
                self.node_definition.module_version
            )
            < 0
        ):
            self.logger.log_warning(
                "The module version in the Node Module's source code does not match the version specified in your Node Definition. Your module may have been updated. We recommend checking to ensure compatibility, and then updating the version in your node definition to match."
            )

        # * Synthesize the node info
        self.node_info = NodeInfo.from_node_def_and_config(
            self.node_definition, self.config
        )

        # * Combine the node definition and classes's capabilities
        self._populate_capabilities()

        # * Add the action decorators to the node (and node info)
        for action_callable in self.__class__.__dict__.values():
            if hasattr(action_callable, "__is_madsci_action__"):
                self._add_action(
                    func=action_callable,
                    action_name=action_callable.__madsci_action_name__,
                    description=action_callable.__madsci_action_description__,
                    blocking=action_callable.__madsci_action_blocking__,
                )

        # * Save the node info and update definition, if possible
        if self.config.update_node_files:
            self._update_node_info_and_definition()

    """------------------------------------------------------------------------------------------------"""
    """Node Lifecycle and Public Methods"""
    """------------------------------------------------------------------------------------------------"""

    def start_node(self) -> None:
        """Called once to start the node."""

        global_ownership_info.node_id = self.node_definition.node_id
        # * Update EventClient with logging parameters
        self._configure_clients()

        # * Log startup info
        self.logger.log_debug(f"{self.node_definition=}")

        # * Kick off the startup logic in a separate thread
        # * This allows implementations to start servers, listeners, etc.
        # * in parrallel
        self._startup()

    def status_handler(self) -> None:
        """Called periodically to update the node status. Should set `self.node_status`"""

    def state_handler(self) -> None:
        """Called periodically to update the node state. Should set `self.node_state`"""

    def startup_handler(self) -> None:
        """Called to (re)initialize the node. Should be used to open connections to devices or initialize any other resources."""

    def shutdown_handler(self) -> None:
        """Called to shut down the node. Should be used to clean up any resources."""

    """------------------------------------------------------------------------------------------------"""
    """Interface Methods"""
    """------------------------------------------------------------------------------------------------"""

    def get_action_history(
        self, action_id: Optional[str] = None
    ) -> dict[str, list[ActionResult]]:
        """Get the action history for the node or a specific action run."""
        if action_id:
            history_entry = self.action_history.get(action_id, None)
            if history_entry is None:
                history_entry = [
                    ActionResult(
                        status=ActionStatus.UNKNOWN,
                        errors=Error(
                            message=f"Action history for action with id '{action_id}' not found",
                            error_type="ActionHistoryNotFound",
                        ),
                    )
                ]
            return {action_id: history_entry}
        return self.action_history

    def run_action(self, action_request: ActionRequest) -> ActionResult:
        """Run an action on the node."""
        self.node_status.running_actions.add(action_request.action_id)
        arg_dict = {}
        self._extend_action_history(action_request.not_started())
        try:
            # * Parse the action arguments and check for required arguments
            arg_dict = self._parse_action_args(action_request)
            self._check_required_args(action_request)
        except Exception as e:
            # * If there was an error in parsing the action arguments, log the error and return a failed action response
            # * but don't set the node to errored
            self.node_status.running_actions.discard(action_request.action_id)
            self._exception_handler(e, set_node_errored=False)
            self._extend_action_history(
                action_request.failed(errors=Error.from_exception(e))
            )
        else:
            if not self.node_status.ready:
                self._extend_action_history(
                    action_request.not_ready(
                        errors=Error(
                            message=f"Node is not ready: {self.node_status.description}",
                            error_type="NodeNotReady",
                        ),
                    )
                )
                self.node_status.running_actions.discard(action_request.action_id)
            else:
                try:
                    # * Run the action in a separate thread
                    self._extend_action_history(action_request.running())
                    self._action_thread(
                        action_request,
                        self.action_handlers.get(action_request.action_name),
                        arg_dict,
                    )
                except Exception as e:
                    # * If there was an error in running the action, log the error and return a failed action response
                    # * and set the node to errored, as the node has failed to run a supposedly valid action request
                    self._exception_handler(e)
                    self._extend_action_history(
                        action_request.failed(errors=Error.from_exception(e))
                    )
                    self.node_status.running_actions.discard(action_request.action_id)

        return self.get_action_result(action_request.action_id)

    def get_action_result(self, action_id: str) -> ActionResult:
        """Get the most up-to-date result of an action on the node."""
        if action_id in self.action_history and len(self.action_history[action_id]) > 0:
            return self.action_history[action_id][-1]
        return ActionResult(
            status=ActionStatus.UNKNOWN,
            errors=Error(
                message=f"Action history for action with id '{action_id}' not found",
                error_type="ActionHistoryNotFound",
            ),
        )

    def get_status(self) -> NodeStatus:
        """Get the status of the node."""
        return self.node_status

    def set_config(self, new_config: dict[str, Any]) -> NodeSetConfigResponse:
        """Set configuration values of the node."""

        try:
            for key, value in new_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    raise ValueError(
                        f"Configuration key '{key}' is not valid for this node."
                    )
            return NodeSetConfigResponse(
                success=True,
            )
        except ValidationError as e:
            return NodeSetConfigResponse(success=True, errors=Error.from_exception(e))

    def run_admin_command(self, admin_command: AdminCommands) -> AdminCommandResponse:
        """Run the specified administrative command on the node."""
        if hasattr(self, admin_command) and callable(
            self.__getattribute__(admin_command),
        ):
            try:
                response = self.__getattribute__(admin_command)()
                if response is None:
                    # * Assume success if no return value
                    response = True
                    return AdminCommandResponse(
                        success=True,
                        errors=[],
                    )
                if isinstance(response, bool):
                    return AdminCommandResponse(
                        success=response,
                        errors=[],
                    )
                if isinstance(response, AdminCommandResponse):
                    return response
                raise ValueError(
                    f"Admin command {admin_command} returned an unexpected value: {response}",
                )
            except Exception as e:
                self._exception_handler(e)
                return AdminCommandResponse(
                    success=False,
                    errors=[Error.from_exception(e)],
                )
        else:
            return AdminCommandResponse(
                success=False,
                errors=[
                    Error(
                        message=f"Admin command {admin_command} not implemented by this node",
                        error_type="AdminCommandNotImplemented",
                    ),
                ],
            )

    def get_info(self) -> NodeInfo:
        """Get information about the node."""
        return self.node_info

    def get_state(self) -> dict[str, Any]:
        """Get the state of the node."""
        return self.node_state

    def get_log(self) -> dict[str, Event]:
        """Return the log of the node"""
        return self.logger.get_log()

    """------------------------------------------------------------------------------------------------"""
    """Admin Commands"""
    """------------------------------------------------------------------------------------------------"""

    def lock(self) -> bool:
        """Admin command to lock the node."""
        self.node_status.locked = True
        self.logger.log_info("Node locked")
        return True

    def unlock(self) -> bool:
        """Admin command to unlock the node."""
        self.node_status.locked = False
        self.logger.log_info("Node unlocked")
        return True

    """------------------------------------------------------------------------------------------------"""
    """Internal and Private Methods"""
    """------------------------------------------------------------------------------------------------"""

    def _configure_clients(self) -> None:
        """Configure the event and resource clients."""
        self.logger = self.event_client = EventClient(
            name=f"node.{self.node_definition.node_name}",
        )
        self.resource_client = ResourceClient(event_client=self.event_client)
        self.data_client = DataClient()

    def _add_action(
        self,
        func: Callable,
        action_name: str,
        description: str,
        blocking: bool = True,
    ) -> None:
        """Add an action to the node module.

        Args:
            func: The function to add as an action handler
            action_name: The name of the action
            description: The description of the action
            blocking: Whether this action blocks other actions while running
        """
        # *Register the action handler
        self.action_handlers[action_name] = func

        action_def = ActionDefinition(
            name=action_name,
            description=description,
            blocking=blocking,
            args=[],
            files=[],
        )
        # *Create basic action definition from function signature
        signature = inspect.signature(func)
        if signature.parameters:
            for parameter_name, parameter_type in get_type_hints(
                func,
                include_extras=True,
            ).items():
                self.logger.log_debug(
                    f"Adding parameter {parameter_name} of type {parameter_type} to action {action_name}",
                )
                if parameter_name == "return":
                    # TODO: Extract the return type and add it to the action definition
                    continue
                if (
                    parameter_name not in action_def.args
                    and parameter_name
                    not in [file.name for file in action_def.files.values()]
                    and parameter_name != "action"
                ):
                    self._parse_action_arg(
                        action_def, signature, parameter_name, parameter_type
                    )
        self.node_info.actions[action_name] = action_def

    def _parse_action_arg(
        self,
        action_def: ActionDefinition,
        signature: inspect.Signature,
        parameter_name: str,
        parameter_type: Any,
    ) -> None:
        """Parses a function argument of an action handler into a MADSci ArgumentDefinition"""
        type_hint = parameter_type
        description = ""
        annotated_as_file = False
        annotated_as_arg = False
        annotated_as_location = False
        # * If the type hint is Optional, extract the inner type
        if is_optional(type_hint):
            type_hint = get_args(type_hint)[0]
            # * If the type hint is an Annotated type, extract the type and description
            # * Description here means the first string metadata in the Annotated type
        if get_origin(type_hint) == Annotated:
            description = next(
                (
                    metadata
                    for metadata in type_hint.__metadata__
                    if isinstance(metadata, str)
                ),
                "",
            )
            annotated_as_file = any(
                isinstance(metadata, FileArgumentDefinition)
                for metadata in type_hint.__metadata__
            )
            annotated_as_location = any(
                isinstance(metadata, LocationArgumentDefinition)
                for metadata in type_hint.__metadata__
            )
            annotated_as_arg = any(
                isinstance(metadata, ArgumentDefinition)
                for metadata in type_hint.__metadata__
            )
            if sum([annotated_as_file, annotated_as_arg, annotated_as_location]) > 1:
                raise ValueError(
                    f"Parameter '{parameter_name}' is annotated as multiple types of argument. This is not allowed.",
                )
            type_hint = get_args(type_hint)[0]
            # * Another Optional check after Annotated type extraction
        if is_optional(type_hint):
            type_hint = get_args(type_hint)[0]
            # * If the type hint is a file type, add it to the files list
        if annotated_as_file or (
            getattr(type_hint, "__name__", None)
            in ["Path", "PurePath", "PosixPath", "WindowsPath"]
            and not annotated_as_arg
        ):
            # * Add a file parameter to the action
            action_def.files[parameter_name] = FileArgumentDefinition(
                name=parameter_name,
                required=True,
                description=description,
            )
        # * Otherwise, add it to the args list
        else:
            parameter_info = signature.parameters[parameter_name]
            # * Add an arg to the action
            default = (
                None
                if parameter_info.default == inspect.Parameter.empty
                else parameter_info.default
            )
            is_required = parameter_info.default == inspect.Parameter.empty

            if annotated_as_location or type_hint is LocationArgument:
                action_def.locations[parameter_name] = LocationArgumentDefinition(
                    name=parameter_name,
                    required=is_required,
                    description=description,
                )
            else:
                action_def.args[parameter_name] = ArgumentDefinition(
                    name=parameter_name,
                    argument_type=pretty_type_repr(type_hint),
                    default=default,
                    required=is_required,
                    description=description,
                )

    def _parse_action_args(
        self,
        action_request: ActionRequest,
    ) -> Union[ActionResult, tuple[callable, dict[str, Any]]]:
        """Parse the arguments for an action request."""
        action_callable = self.action_handlers.get(action_request.action_name, None)
        if action_callable is None:
            raise ActionNotImplementedError(
                f"Action {action_request.action_name} not implemented by this node",
            )
        # * Prepare arguments for the action function.
        # * If the action function has a 'state' or 'action' parameter
        # * we'll pass in our state and action objects.
        arg_dict = {}
        parameters = inspect.signature(action_callable).parameters
        if parameters.__contains__("action"):
            arg_dict["action"] = action_request
        if parameters.__contains__("self"):
            arg_dict["self"] = self
        if list(parameters.values())[-1].kind == inspect.Parameter.VAR_KEYWORD:
            # * Function has **kwargs, so we can pass all action args and files
            arg_dict = {**arg_dict, **action_request.args}
            arg_dict = {
                **arg_dict,
                **{file.filename: file.file for file in action_request.files},
            }
        else:
            # * Pass only explicit arguments, dropping extras
            for arg_name, arg_value in action_request.args.items():
                if arg_name in parameters:
                    arg_dict[arg_name] = arg_value
                else:
                    EventClient().log_warning(
                        f"Ignoring unexpected argument {arg_name}"
                    )
            for file in action_request.files:
                if file in parameters:
                    arg_dict[file] = action_request.files[file]
                else:
                    EventClient().log_warning(f"Ignoring unexpected file {file}")

        # Validate any arguments that expect a LocationArgument

        return self._validate_location_arguments(action_callable, arg_dict)

    def _validate_location_arguments(
        self,
        action_callable: Callable,
        arg_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate and convert any arguments expected as LocationArgument.

        If the action function declares a parameter with type LocationArgument and the
        corresponding value in arg_dict is a dictionary (e.g., from a deserialized JSON payload),
        this function uses Pydantic's model_validate to reconstruct a valid LocationArgument instance.

        Raises:
            ValueError: If the input dictionary fails LocationArgument validation.

        Returns:
            dict[str, Any]: The updated argument dictionary with validated LocationArgument objects.
        """
        type_hints = get_type_hints(action_callable)
        for name, expected_type in type_hints.items():
            if expected_type is LocationArgument and isinstance(
                arg_dict.get(name), dict
            ):
                try:
                    arg_dict[name] = LocationArgument.model_validate(arg_dict[name])
                except ValidationError as e:
                    raise ValueError(
                        f"Invalid LocationArgument for parameter '{name}': {e}"
                    ) from e
        return arg_dict

    @threaded_daemon
    def _action_thread(
        self,
        action_request: ActionRequest,
        action_callable: callable,
        arg_dict: dict[str, Any],
    ) -> None:
        try:
            with (
                self._action_lock
                if self.node_info.actions[action_request.action_name].blocking
                else contextlib.nullcontext()
            ):
                try:
                    if self.node_info.actions[action_request.action_name].blocking:
                        self.node_status.busy = True
                    result = action_callable(**arg_dict)
                except Exception as e:
                    self._exception_handler(e)
                    result = action_request.failed(errors=Error.from_exception(e))
                finally:
                    if self.node_info.actions[action_request.action_name].blocking:
                        self.node_status.busy = False
        finally:
            self.node_status.running_actions.discard(action_request.action_id)
        if isinstance(result, ActionResult):
            # * Make sure the action ID is set correctly on the result
            result.action_id = action_request.action_id
        else:
            try:
                result = ActionResult.model_validate(result)
                result.action_id = action_request.action_id
            except ValidationError:
                result = action_request.unknown(
                    errors=Error(
                        message=f"Action '{action_request.action_name}' returned an unexpected value: {result}. Expected an ActionResult.",
                    ),
                )
        self._extend_action_history(result)

    def _exception_handler(self, e: Exception, set_node_errored: bool = True) -> None:
        """Handle an exception."""
        if set_node_errored:
            self.node_status.errored = True
        madsci_error = Error.from_exception(e)
        self.node_status.errors.append(madsci_error)
        self.logger.log_error(
            Event(event_type=EventType.NODE_ERROR, event_data=madsci_error)
        )
        self.logger.log_error(traceback.format_exc())

    def _update_status(self) -> None:
        """Update the node status."""
        try:
            self.status_handler()
        except Exception as e:
            self._exception_handler(e)

    def _update_state(self) -> None:
        """Update the node state."""
        try:
            self.state_handler()
        except Exception as e:
            self._exception_handler(e)

    def _populate_capabilities(self) -> None:
        """Populate the node capabilities based on the node definition and the supported capabilities of the class."""
        if self.node_info.capabilities is None:
            self.node_info.capabilities = NodeCapabilities()
        for field in self.supported_capabilities.__pydantic_fields__:
            if getattr(self.node_info.capabilities, field) is None:
                setattr(
                    self.node_info.capabilities,
                    field,
                    getattr(self.supported_capabilities, field),
                )

        # * Add the admin commands to the node info
        self.node_info.capabilities.admin_commands = set.union(
            self.node_info.capabilities.admin_commands,
            {
                admin_command.value
                for admin_command in AdminCommands
                if hasattr(self, admin_command.value)
                and callable(self.__getattribute__(admin_command.value))
            },
        )

    def _update_node_info_and_definition(self) -> None:
        """Update the node info and definition files, if possible."""
        try:
            self.node_definition.to_yaml(self.config.node_definition)
            if not self.config.node_info_path:
                self.node_info_path = Path(self.config.node_definition).with_name(
                    f"{self.node_definition.node_name}.info.yaml"
                )
            self.node_info.to_yaml(self.node_info_path, exclude={"config_values"})
        except Exception as e:
            self.logger.log_warning(
                f"Failed to update node info file: {e}",
            )

    def _check_required_args(self, action_request: ActionRequest) -> None:
        """Check that all required arguments are present in the action request."""
        missing_args = [
            arg_name
            for arg_name, arg_def in self.node_info.actions[
                action_request.action_name
            ].args.items()
            if arg_def.required and arg_name not in action_request.args
        ]
        if missing_args:
            raise ValueError(
                f"Missing required arguments for action '{action_request.action_name}': {missing_args}"
            )

    @threaded_daemon
    def _startup(self) -> None:
        """The startup thread for the node."""
        try:
            # * Create a clean status and mark the node as initializing
            self.node_status.initializing = True
            self.node_status.errored = False
            self.node_status.locked = False
            self.node_status.paused = False
            self.node_status.stopped = False
            self.startup_handler()
            # * Start status and state update loops
            repeat_on_interval(
                getattr(self.config, "status_update_interval", 2.0), self._update_status
            )
            repeat_on_interval(
                getattr(self.config, "state_update_interval", 2.0), self._update_state
            )

        except Exception as exception:
            # * Handle any exceptions that occurred during startup
            self._exception_handler(exception)
            self.node_status.errored = True
        else:
            self.logger.log_info(
                Event(
                    event_type=EventType.NODE_START,
                    event_data=self.node_definition.model_dump(mode="json"),
                )
            )
        finally:
            # * Mark the node as no longer initializing
            self.node_status.initializing = False

    def _extend_action_history(self, action_result: ActionResult) -> None:
        """Extend the action history with a new action result."""
        existing_history = self.action_history.get(action_result.action_id, None)
        if existing_history is None:
            self.action_history[action_result.action_id] = [action_result]
        else:
            self.action_history[action_result.action_id].append(action_result)
        self.logger.log_info(
            Event(
                event_type=EventType.ACTION_STATUS_CHANGE,
                event_data=action_result,
            )
        )

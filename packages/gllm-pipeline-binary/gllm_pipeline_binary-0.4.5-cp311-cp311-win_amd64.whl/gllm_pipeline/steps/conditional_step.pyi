from _typeshed import Incomplete
from dataclasses import dataclass
from gllm_core.event.event_emitter import EventEmitter as EventEmitter
from gllm_core.schema import Component
from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from gllm_pipeline.steps.terminator_step import TerminatorStep as TerminatorStep
from gllm_pipeline.utils.async_utils import execute_callable as execute_callable
from gllm_pipeline.utils.has_inputs_mixin import HasInputsMixin as HasInputsMixin
from gllm_pipeline.utils.mermaid import MERMAID_HEADER as MERMAID_HEADER, combine_mermaid_diagrams as combine_mermaid_diagrams, extract_step_diagrams as extract_step_diagrams
from gllm_pipeline.utils.step_execution import execute_sequential_steps as execute_sequential_steps
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langgraph.graph import StateGraph as StateGraph
from langgraph.types import Command
from typing import Any, Callable

ConditionType = Component | Callable[[dict[str, Any]], str]
DEFAULT_BRANCH: str

@dataclass
class ConditionInputs:
    """Container for different types of inputs used in condition evaluation.

    Attributes:
        merged (dict[str, Any]): Complete merged dictionary containing all state, config, and fixed args.
            Used for Callable conditions.
        mapped (dict[str, Any]): Dictionary containing only explicitly mapped inputs.
            Used for Component conditions.
        event_emitter (EventEmitter | None): Event emitter instance for logging.
    """
    merged: dict[str, Any]
    mapped: dict[str, Any]
    event_emitter: EventEmitter | None

class ConditionalStep(BasePipelineStep, HasInputsMixin):
    '''A conditional pipeline step that conditionally executes different branches based on specified conditions.

    This step evaluates one or more conditions and selects a branch to execute based on the result.
    It provides flexibility in defining complex conditional logic within a pipeline.

    A minimal usage requires defining the branches to execute based on a `condition`, which is a callable
    that takes input from the state and returns a string identifying the branch to execute.

    The condition can be a `Component` or a `Callable`. The handling of inputs differs:
    1. If the condition is a `Component`, `input_state_map` and `runtime_config_map` are
      used to map the pipeline\'s state and config to the component\'s inputs.
    2. If the condition is a `Callable`, it receives a merged dictionary of the
      pipeline\'s state and config directly. `input_state_map` and `runtime_config_map`
      are ignored in this case.

    Example:
    ```python
    ConditionalStep(
        name="UseCaseSelection",
        branches={"A": step_a, DEFAULT_BRANCH: step_b},
        condition=lambda x: "A" if "<A>" in x["query"] else "__default__"
    )
    ```
    This will execute `step_a` if the query contains "<A>", and `step_b` otherwise.

    The special key `__default__` (importable as DEFAULT_BRANCH) defines the default branch to execute
    if no other condition matches. If the DEFAULT_BRANCH is not defined and no condition matches,
    the step will raise an error.

    Attributes:
        name (str): A unique identifier for this pipeline step.
        branches (dict[str, BasePipelineStep | list[BasePipelineStep]]): Mapping of condition results to steps.
        condition (list[ConditionType] | None): The condition(s) to evaluate for branch selection.
        input_state_map (dict[str, str] | None): A dictionary mapping the state keys to the component\'s
            input keys. This is only used if the condition is a `Component`. Defaults to None.
        output_state (str | None): Key to store the condition result in the state, if desired.
        condition_aggregator (Callable[[list[Any]], str]): Function to aggregate multiple condition results.
        runtime_config_map (dict[str, str] | None): A dictionary mapping the runtime config keys to the
            component\'s input keys. This is only used if the condition is a `Component`. Defaults to None.
        fixed_args (dict[str, Any] | None): Fixed arguments to be passed to the condition evaluation.
    '''
    branches: Incomplete
    condition: Incomplete
    output_state: Incomplete
    condition_aggregator: Incomplete
    def __init__(self, name: str, branches: dict[str, BasePipelineStep | list[BasePipelineStep]], condition: ConditionType | list[ConditionType] | None = None, input_state_map: dict[str, str] | None = None, output_state: str | None = None, condition_aggregator: Callable[[list[Any]], str] = ..., runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None) -> None:
        '''Initializes a new ConditionalStep.

        Args:
            name (str): A unique identifier for this pipeline step.
            branches (dict[str, BasePipelineStep | list[BasePipelineStep]]): Mapping of condition results to steps to
                execute.
            condition (ConditionType | list[ConditionType] | None, optional): The condition(s) to evaluate for branch
                selection. If a `Callable`, it receives the merged state and config as keyword arguments. If None,
                the condition is evaluated from the state. Defaults to None.
            input_state_map (dict[str, str] | None, optional): A dictionary mapping the state keys to the component\'s
                input keys. This is only used if the condition is a `Component`. Defaults to None.
            output_state (str | None, optional): Key to store the condition result in the state. If None, the
                output is not saved in the state. Defaults to None.
            condition_aggregator (Callable[[list[Any]], str], optional): Function to aggregate multiple condition
                results. Defaults to joining results with a semicolon (";").
            runtime_config_map (dict[str, str] | None, optional): A dictionary mapping the runtime config keys to the
                component\'s input keys. This is only used if the condition is a
                `Component`. Defaults to None.
            fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the condition.
                Defaults to None.
        '''
    def add_to_graph(self, graph: StateGraph, previous_endpoints: list[str]) -> list[str]:
        """Integrates this step into the pipeline's internal structure.

        This method is used by `Pipeline` to manage the pipeline's execution flow.
        It should not be called directly by users.

        This method always creates a condition node that:
        1. Executes the condition and stores its result if output_state is defined
        2. Acts as a pass-through router if no output_state is defined
        3. Connects to the appropriate branch based on condition evaluation

        Args:
            graph (StateGraph): The internal representation of the pipeline structure.
            previous_endpoints (list[str]): The endpoints from previous steps to connect to.

        Returns:
            list[str]: The exit points (endpoints) of all non-terminating branches.
        """
    async def select_path(self, state: dict[str, Any], config: RunnableConfig) -> str:
        """Determines the logical route key based on the evaluated condition(s).

        This method prepares input data, evaluates conditions, aggregates results,
        and determines the logical route key.

        Args:
            state (dict[str, Any]): The current state of the pipeline, containing all data.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            str: The identifier of the selected logical route. Returns DEFAULT_BRANCH if an error occurs
                or if the condition result doesn't match any branch key.
        """
    def get_all_steps(self) -> list[BasePipelineStep]:
        """Gets all steps from all branches.

        Returns:
            list[BasePipelineStep]: A list of all steps in all branches.
        """
    async def execute(self, state: dict[str, Any], config: RunnableConfig) -> Command:
        """Executes the conditional step, determines the route, and returns a Command.

        Args:
            state (dict[str, Any]): The current state of the pipeline.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            Command: A LangGraph Command object with 'goto' for routing and 'update' for state changes.
        """
    async def execute_direct(self, state: dict[str, Any], config: RunnableConfig) -> dict[str, Any] | None:
        """Execute this step directly, handling both branch selection and execution.

        This method is used when the step needs to be executed directly (e.g. in parallel execution).
        It will both select and execute the appropriate branch, unlike execute() which only handles selection.

        Args:
            state (dict[str, Any]): The current state of the pipeline.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            dict[str, Any] | None: Updates to apply to the pipeline state, or None if no updates.
        """
    def get_mermaid_diagram(self) -> str:
        """Create a Mermaid diagram representation of the conditional step.

        Returns:
            str: The complete Mermaid diagram representation of the conditional branches.
        """

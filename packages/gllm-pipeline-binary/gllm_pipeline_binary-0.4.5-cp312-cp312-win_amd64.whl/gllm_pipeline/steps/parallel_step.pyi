from _typeshed import Incomplete
from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext, ValidationError as ValidationError
from gllm_pipeline.utils.has_inputs_mixin import HasInputsMixin as HasInputsMixin
from gllm_pipeline.utils.mermaid import combine_mermaid_diagrams as combine_mermaid_diagrams, extract_step_diagrams as extract_step_diagrams
from gllm_pipeline.utils.step_execution import execute_sequential_steps as execute_sequential_steps
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langgraph.graph import StateGraph as StateGraph
from typing import Any

class ParallelStep(BasePipelineStep, HasInputsMixin):
    """A pipeline step that executes multiple branches in parallel.

    This step wraps multiple branches and executes them concurrently, then merges their results.
    Each branch can be either a single step or a list of steps to be executed sequentially.

    The step supports two execution modes controlled by the `squash` parameter:
    1. Squashed (default): Uses asyncio.gather() to run branches in parallel within a single LangGraph node. Use for:
       a. Better raw performance
       b. Simpler implementation
       c. Less overhead
       d. Less transparent for debugging and tracing
    2. Expanded (squash=False): Creates a native LangGraph structure with multiple parallel paths. Use for:
       a. More native LangGraph integration
       b. More transparent for debugging and tracing

    For memory optimization, you can specify input_states to pass only specific keys to branches.
    This is especially useful when the state is large but branches only need specific parts of it.
    If input_states is None (default), all state keys will be passed.

    Attributes:
        name (str): A unique identifier for this pipeline step.
        branches (list[BasePipelineStep | list[BasePipelineStep]]]): The branches to execute in parallel.
        squash (bool): Whether to squash execution into a single node.
            1. If True, uses asyncio.gather() to run branches in parallel. This will create a single node.
            2. If False, uses native LangGraph structures for parallelism. This will create multiple nodes.
        input_states (list[str] | None): Keys from the state that should be passed to branches.
            If None, all state keys will be passed.
    """
    branches: Incomplete
    squash: Incomplete
    def __init__(self, name: str, branches: list[BasePipelineStep | list[BasePipelineStep]], input_states: list[str] | None = None, squash: bool = True, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None) -> None:
        """Initialize a new ParallelStep.

        Args:
            name (str): A unique identifier for this pipeline step.
            branches (list[BasePipelineStep | list[BasePipelineStep]]):
                The branches to execute in parallel. Each branch can be:
                1. A single step
                2. A list of steps to execute sequentially
            input_states (list[str] | None, optional): Keys from the state to pass to branches.
                If None, all state keys will be passed. Defaults to None.
            squash (bool, optional): Whether to squash execution into a single node.
                1. If True, uses asyncio.gather() to run branches in parallel. This will create a single node.
                2. If False, uses native LangGraph structures for parallelism. This will create multiple nodes.
                Defaults to True.
            runtime_config_map (dict[str, str] | None, optional): Mapping of input keys to runtime config keys.
                Defaults to None.
            fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the component.
                Defaults to None, in which case an empty dictionary is used.
        """
    def add_to_graph(self, graph: StateGraph, previous_endpoints: list[str]) -> list[str]:
        """Add this step to the graph.

        Uses either squashed or expanded approach based on the squash parameter.

        Args:
            graph (StateGraph): The graph to add this step to.
            previous_endpoints (list[str]): The endpoints from previous steps to connect to.

        Returns:
            list[str]: The endpoint(s) of this step.
        """
    async def execute(self, state: dict[str, Any], config: RunnableConfig) -> dict[str, Any] | None:
        """Execute all branches in parallel and merge their results.

        This method is only used for the squashed approach. For the expanded approach,
        the execution is handled by the graph structure.

        Args:
            state (dict[str, Any]): The current state of the pipeline.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            dict[str, Any] | None: The merged results from all parallel branches, or None if no updates were produced.

        Raises:
            asyncio.CancelledError: If execution is cancelled, preserved with added context.
            BaseInvokerError: If an error occurs during LM invocation.
            RuntimeError: For all other exceptions during execution, wrapped with context information.
            TimeoutError: If execution times out, preserved with added context.
            ValidationError: If input validation fails.
        """
    def get_mermaid_diagram(self) -> str:
        """Combines the base diagram and nested step diagrams into a complete visualization.

        If the parallel step is squashed, a custom logic is used to represent the structure.
        If the parallel step is not squashed, the structure is created natively using LangGraph nodes.

        Returns:
            str: Complete Mermaid diagram for this parallel step.
        """

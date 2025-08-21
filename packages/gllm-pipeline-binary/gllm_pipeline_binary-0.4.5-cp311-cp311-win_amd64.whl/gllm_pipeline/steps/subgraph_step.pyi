from _typeshed import Incomplete
from gllm_pipeline.pipeline.pipeline import Pipeline as Pipeline
from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext
from gllm_pipeline.utils.has_inputs_mixin import HasInputsMixin as HasInputsMixin
from gllm_pipeline.utils.mermaid import combine_mermaid_diagrams as combine_mermaid_diagrams, extract_step_diagrams as extract_step_diagrams
from langchain_core.runnables import RunnableConfig as RunnableConfig
from typing import Any

class SubgraphStep(BasePipelineStep, HasInputsMixin):
    """A pipeline step that executes another pipeline as a subgraph.

    This step allows for encapsulation and reuse of pipeline logic by treating another pipeline as a step.
    The subgraph can have its own state schema, and this step handles the mapping between the parent and
    subgraph states.

    Attributes:
        name (str): A unique identifier for this pipeline step.
        subgraph (Pipeline): The pipeline to be executed as a subgraph.
        input_state_map (dict[str, str]): Mapping of subgraph input keys to parent pipeline state keys.
        output_state_map (dict[str, str]): Mapping of parent pipeline state keys to subgraph output keys.
        runtime_config_map (dict[str, str] | None): Mapping of subgraph input keys to runtime configuration keys.
        fixed_args (dict[str, Any] | None): Fixed arguments to be passed to the subgraph.
    """
    subgraph: Incomplete
    output_state_map: Incomplete
    def __init__(self, name: str, subgraph: Pipeline, input_state_map: dict[str, str] | None = None, output_state_map: dict[str, str] | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None) -> None:
        """Initializes a new SubgraphStep.

        Args:
            name (str): A unique identifier for this pipeline step.
            subgraph (Pipeline): The pipeline to be executed as a subgraph.
            input_state_map (dict[str, str]): Mapping of subgraph input keys to parent pipeline state keys.
            output_state_map (dict[str, str]): Mapping of parent pipeline state keys to subgraph output keys.
            runtime_config_map (dict[str, str] | None, optional): Mapping of subgraph input keys to runtime
                configuration keys. Defaults to None, in which case an empty dictionary is used.
            fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the subgraph.
                Defaults to None, in which case an empty dictionary is used.
        """
    async def execute(self, state: dict[str, Any], config: RunnableConfig) -> dict[str, Any]:
        """Executes the subgraph and processes its output.

        This method prepares data, executes the subgraph, and formats the output for integration
        into the parent pipeline state. It only uses keys that are actually present in the state,
        ignoring missing keys to prevent errors.

        Args:
            state (dict[str, Any]): The current state of the pipeline, containing all data.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            dict[str, Any]: The update to the pipeline state after this step's operation.
                This includes new or modified data produced by the subgraph, not the entire state.
                If a requested output key is not present in the subgraph result, its value will be None.

        Raises:
            RuntimeError: If an error occurs during subgraph execution, with details about which step caused the error.
        """
    def get_mermaid_diagram(self) -> str:
        """Create a Mermaid diagram representation of the subgraph.

        Returns:
            str: The complete Mermaid diagram representation of the subgraph.
        """

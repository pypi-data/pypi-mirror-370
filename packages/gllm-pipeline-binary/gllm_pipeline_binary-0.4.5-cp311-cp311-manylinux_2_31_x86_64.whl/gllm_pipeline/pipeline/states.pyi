from gllm_core.event.event_emitter import EventEmitter as EventEmitter
from typing import Any, TypedDict

class RAGState(TypedDict):
    """A TypedDict representing the state of a Retrieval-Augmented Generation (RAG) pipeline.

    This docstring documents the original intention of each of the attributes in the TypedDict.
    However, in practice, the attributes may be modified or extended to suit the specific requirements of the
    application. The TypedDict is used to enforce the structure of the state object.

    Attributes:
        user_query (str): The original query from the user.
        queries (list[str]): A list of queries generated for retrieval.
        retrieval_params (dict[str, Any]): Parameters used for the retrieval process.
        chunks (list): A list of chunks retrieved from the knowledge base.
        history (str): The history of the conversation or interaction.
        context (str): The context information used for generating responses.
        response_synthesis_bundle (dict[str, Any]): Data used for synthesizing the final response.
        response (str): The generated response to the user's query.
        references (str | list[str]): References or sources used in generating the response.
        event_emitter (EventEmitter): An event emitter instance for logging purposes.
    """
    user_query: str
    queries: list[str]
    retrieval_params: dict[str, Any]
    chunks: list
    history: str
    context: str
    response_synthesis_bundle: dict[str, Any]
    response: str
    references: str | list[str]
    event_emitter: EventEmitter

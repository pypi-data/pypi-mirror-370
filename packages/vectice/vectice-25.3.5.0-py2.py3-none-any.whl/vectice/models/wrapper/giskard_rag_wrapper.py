from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Sequence

from giskard.rag import AgentAnswer, KnowledgeBase, QATestset, evaluate, generate_testset  # type: ignore[reportMissingImports]

if TYPE_CHECKING:
    from giskard.rag import RAGReport  # type: ignore[reportMissingImports]
    from pandas import DataFrame

_logger = logging.Logger(__name__)


def giskard_rag_wrapper(
    knowledge_base: KnowledgeBase | DataFrame | None = None,
    chat_engine: Any | None = None,
    answer_function: Any | Sequence[AgentAnswer | str] | None = None,
    qa_testset: QATestset | str | None = None,
    testset_num_questions: int | None = None,
    metrics: list[Any] | None = None,
    agent_description: str | None = None,
) -> RAGReport:
    """Wrapper function to configure and evaluate a Retrieval-Augmented Generation (RAG) agent
    using Giskard's RAG module and Azure's Chat Engine.

    This function sets up the RAG agent by initializing necessary configurations, including
    extracting the index, setting up the knowledge base, and the QA testset. The function
    then evaluates the agent using pre-defined RAGAS metrics.

    Args:
        index_zip_path (str): The file path to the zipped index containing preprocessed data.
        index_extract_dir (str): The directory where the index will be extracted.
        knowledge_base_path (str): The path to the knowledge base for retrieval purposes.
        qa_testset_path (str): The file path to the QA test set used for evaluating the RAG agent.
        custom_answer_fn (Callable | None, optional): Custom function to override the default
            answer function. Defaults to None.

    Returns:
        RAGReport: A report containing the evaluation results of the RAG agent,
        including relevant metrics and performance insights.

    Example:
        report = giskard_rag_wrapper(
            index_zip_path="/path/to/index.zip",
            index_extract_dir="/path/to/extracted/index",
            knowledge_base_path="/path/to/knowledge_base",
            qa_testset_path="/path/to/qa_testset.json",
        )
    """
    from pandas import DataFrame

    if knowledge_base is None and qa_testset is None:
        raise ValueError("knowledge_base or qa_testset must be provided")
    if isinstance(knowledge_base, DataFrame):
        knowledge_base = KnowledgeBase(knowledge_base)

    if isinstance(qa_testset, str):
        giskard_testset = QATestset.load(qa_testset)
    elif isinstance(qa_testset, QATestset):
        giskard_testset = qa_testset
    elif qa_testset is None and knowledge_base is not None:
        giskard_testset = generate_testset(knowledge_base, testset_num_questions, agent_description=agent_description)
    else:
        raise ValueError("Unable to generate qa_testset, please check knowledge_base or qa_testset provided.")

    if answer_function is None and chat_engine is None:
        raise ValueError("The answer function or chat engine must be provided")

    if answer_function is None:
        _logger.info("If the answer_function is not provided. A generic answer function will be used.")
        set_chat_engine(chat_engine)
        answer_function = get_answer_fn

    return evaluate(answer_function, testset=giskard_testset, knowledge_base=knowledge_base, metrics=metrics)


global_chat_engine = None


def set_chat_engine(chat_engine: Any):
    global global_chat_engine
    # Initialize your chat engine here
    global_chat_engine = chat_engine


def answer_fn(question: str, history: Any = None) -> Any:
    try:
        from llama_index.core.base.llms.types import ChatMessage, MessageRole  # type: ignore[reportMissingImports]
    except ImportError:
        raise ImportError("Please pip install llama_index to use the generic answer functionality.")

    global global_chat_engine
    if global_chat_engine is None:
        raise ValueError("Chat engine not initialized. Call initialize_chat_engine() first.")

    if history:
        answer = global_chat_engine.chat(
            question,
            chat_history=[
                ChatMessage(
                    role=MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT,
                    content=msg["content"],
                )
                for msg in history
            ],
        )
    else:
        answer = global_chat_engine.chat(question, chat_history=[])
    return answer


def get_answer_fn(question: str, history: Any = None) -> AgentAnswer:
    """A function representing your RAG agent."""
    # Get the answer and the documents
    agent_output = answer_fn(question, history)

    # Following llama_index syntax, you can get the answer and the retrieved documents
    answer = agent_output.response
    documents = agent_output.source_nodes
    document_nodes = [node.text for node in documents]

    # Instead of returning a simple string, we return the AgentAnswer object which
    # allows us to specify the retrieved context which is used by RAGAS metrics
    return AgentAnswer(message=answer, documents=document_nodes)

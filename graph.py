# graph.py
from langgraph.graph import StateGraph
from typing import TypedDict
from nodes.download_repos import download_repos_node
from nodes.generate_docs import generate_docs_node
from nodes.create_embeddings import create_embeddings_node
from nodes.qa_node import qa_node


class RepoState(TypedDict, total=False):
    status: str
    docs: str
    vectorstore: object
    qa: str


def build_graph():
    graph = StateGraph(RepoState, name="GitHub LangGraph Pipeline")

    # Add nodes
    graph.add_node("download_repos", download_repos_node)
    graph.add_node("generate_docs", generate_docs_node)
    graph.add_node("create_embeddings", create_embeddings_node)
    graph.add_node("qa", qa_node)

    # Connect nodes
    graph.set_entry_point("download_repos")
    graph.add_edge("download_repos", "generate_docs")
    graph.add_edge("generate_docs", "create_embeddings")
    graph.add_edge("create_embeddings", "qa")

    return graph.compile()
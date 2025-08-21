from typing import List
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode


@tool
def rag_search(query: str) -> str:
    """
    Searches the knowledge base for information related to the user's query.
    Use this to answer questions about specific academic topics, concepts, or facts.
    """
    print(f"--- (Tool) Executing RAG Search for: '{query}' ---")
    if "llm" in query.lower():
        return "A Large Language Model (LLM) is a type of AI designed to understand and generate human-like text."
    return f"No specific information found for '{query}'. Try a more general topic."
    
tools = [rag_search]

tool_node = ToolNode(tools)
from typing import Annotated, Dict, List, Any, TypedDict
from langchain_core.messages import BaseMessage
from operator import add


def dict_reducer(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = dict_reducer(merged[key], value)
        else:
            merged[key] = value
    return merged


class AcademicState(TypedDict):
    """
    Master state container for the academic assistance system. [cite: 140-156]
    """
    messages: Annotated[List[BaseMessage], add]
    atlas_message: Annotated[List[BaseMessage], add]
    profile: Annotated[Dict, dict_reducer]
    calendar: Annotated[Dict, dict_reducer]
    tasks: Annotated[Dict, dict_reducer]
    results: Annotated[Dict[str, Any], dict_reducer]
    chat_history: Annotated[List[BaseMessage], add]
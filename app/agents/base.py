from app.services.llm_service import LLMService

class ReActAgent:
    """
    Base class for ReACT-based agents.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
# app/agents/senior.py

from typing import Dict, Literal
# Import the helper function for converting tools
from langchain_core.utils.function_calling import convert_to_openai_tool

from app.graph.state import AcademicState
from app.services.llm_service import LLMService
from app.tools.executor import tools
from app.prompts.prompts import SENIOR_AGENT_PROMPT
from .base import ReActAgent

class SeniorAgent(ReActAgent):
    """A conversational agent that can use tools."""
    
    def __init__(self, llm_service: LLMService):
        super().__init__(llm_service)
        # We can specify the provider here to ensure we get the Groq model
        self.llm = self.llm_service.get_llm(provider="groq")

    async def run(self, state: AcademicState) -> Dict:
        """Invokes the LLM with the current message history and tools."""
        print("--- (Node) Executing Senior Agent ---")
        
        messages = state.get("messages", [])
        tools_as_dicts = [convert_to_openai_tool(t) for t in tools]
        prompt = SENIOR_AGENT_PROMPT.format(
            messages = messages,
            query = messages[-1].content,
            tools = tools_as_dicts
        )
        
        ai_response = await self.llm.ainvoke(prompt, tools=tools_as_dicts)
        print(f"   ↳ AI Response: {ai_response}")
        
        return {"messages": [ai_response]}

def should_continue(state: AcademicState) -> Literal["tools", "__end__"]:
    """Checks the last message in the 'messages' list for tool calls."""
    print("--- (Conditional Edge) Checking for Tool Calls ---")
    
    last_message = state['messages'][-1]
    
    if last_message.tool_calls:
        print("   ↳ Decision: Route to Tool Executor.")
        return "tools"
    else:
        print("   ↳ Decision: End of turn.")
        return "__end__"
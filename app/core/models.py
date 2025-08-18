from pydantic import BaseModel, Field
from typing import Optional, Dict


class AgentAction(BaseModel):
    """Model representing an agent's action decision. """
    action: str = Field(..., description="The specific action to be taken.")
    thought: str = Field(..., description="The reasoning process behind the action choice.")
    tool: Optional[str] = Field(None, description="The specific tool to be used for the action.")
    action_input: Optional[Dict] = Field(None, description="Input parameters for the action.")


class AgentOutput(BaseModel):
    """Model representing the output from an agent's action. """
    observation: str = Field(..., description="The result or observation from executing the action.")
    output: Dict = Field(..., description="Structured output data from the action.")
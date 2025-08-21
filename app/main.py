# app/main.py

import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from IPython.display import Image, display

from app.graph.graph import create_graph
from app.graph.state import AcademicState
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# --- 1. Pydantic Models for API (No changes needed) ---
class InvokeRequest(BaseModel):
    query: str

class InvokeResponse(BaseModel):
    response: str
    full_history: List[Dict[str, Any]]

# --- 2. FastAPI App Initialization (No changes needed) ---
app = FastAPI(
    title="Atlas Multi-Agent System",
    description="An API for interacting with the Atlas academic assistant.",
    version="1.0.0"
)

graph = create_graph()
graph.get_graph().print_ascii()
img = Image(graph.get_graph().draw_mermaid_png())
png_bytes = graph.get_graph().draw_mermaid_png()

# We then write these bytes to a file
with open("my_workflow_graph.png", "wb") as f:
    f.write(png_bytes)
    
print("✅ Success! Graph image saved as 'my_workflow_graph.png' in your root directory.")

config = {"configurable": {"thread_id": "1"}}

def _serialize_messages(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
    """Helper to convert BaseMessage objects to a JSON-serializable format."""
    serialized = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            serialized.append({"type": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                serialized.append({
                    "type": "ai_tool_call", 
                    "content": msg.content,
                    "tool_calls": msg.tool_calls
                })
            else:
                serialized.append({"type": "ai", "content": msg.content})
        else: # Covers SystemMessage, ToolMessage etc.
            serialized.append({"type": "system", "content": msg.content})
    return serialized

# --- 3. API Endpoint (CORRECTED) ---
@app.post("/invoke", response_model=InvokeResponse)
async def invoke_agent(request: InvokeRequest):
    """
    Invokes the multi-agent system with a user query.
    """
    initial_state = AcademicState(
        messages=[HumanMessage(content=request.query)],
        profile={}, calendar={}, tasks={}, results={}, atlas_message=[]
    )

    final_state = await graph.ainvoke(initial_state, config)

    # *** CORRECTED LOGIC ***
    # The response depends on which workflow was executed.

    response_content = "No response generated."
    final_results = final_state.get("results", {})
    messages = final_state.get("messages", [])

    # Check for academic agent outputs first, as they are the primary product
    if "planner_output" in final_results:
        response_content = final_results["planner_output"].get("plan", "Plan generated, but content is empty.")
    elif "notewriter_output" in final_results:
        response_content = final_results["notewriter_output"].get("notes", "Notes generated, but content is empty.")
    elif "advisor_output" in final_results:
        response_content = final_results["advisor_output"].get("advice", "Advice generated, but content is empty.")
    
    # Fallback to the Senior Agent's chat history if no academic output is found
    elif messages:
        last_message = messages[-1]
        if isinstance(last_message, AIMessage):
            response_content = last_message.content

    # The messages from the state might be empty, so we start with the user's message
    # and add the final AI response for a complete record.
    final_history = final_state.get('messages') or [HumanMessage(content=request.query)]
    if not isinstance(final_history[-1], AIMessage):
         final_history.append(AIMessage(content=response_content))
    
    full_history_serialized = _serialize_messages(final_history)

    return InvokeResponse(
        response=response_content,
        full_history=full_history_serialized
    )

# --- 4. Root Endpoint for Health Check (No changes needed) ---
@app.get("/")
def read_root():
    return {"status": "Atlas is running"}
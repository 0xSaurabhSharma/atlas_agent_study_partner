import json
from typing import Dict
from langchain_core.messages import SystemMessage
from app.graph.state import AcademicState
from app.services.llm_service import LLMService
from app.prompts.prompts import COORDINATOR_PROMPT

def parse_coordinator_response(response: str) -> dict:
    """Parses the coordinator's text response to determine the execution plan."""
    required_agents = ["PLANNER"] # Planner is the default
    if "notewriter" in response.lower() or "note" in response.lower():
        required_agents.append("NOTEWRITER")
    if "advisor" in response.lower() or "guidance" in response.lower():
        required_agents.append("ADVISOR")
    return {"required_agents": list(set(required_agents))}

async def coordinator_agent(state: AcademicState, llm_service: LLMService) -> dict:
    """
    The brain of the operation. Decides which specialized agents are needed.
    """
    print("--- (Node) Executing Coordinator Agent ---")
    
    profile = state.get("profile", {})
    context = {
        "student_major": profile.get("personal_info", {}).get("major", "Unknown"),
        "upcoming_events": len(state.get("calendar", {}).get("events", [])),
        "active_tasks": len(state.get("tasks", {}).get("tasks", [])),
    }
    query = state["messages"][-1].content

    prompt = COORDINATOR_PROMPT.format(request=query, context=json.dumps(context, indent=2))
    
    # Get the LLM instance from the service
    llm = llm_service.get_llm()
    # Use .ainvoke() with the original message structure
    response_obj = await llm.ainvoke(prompt)
    # response_obj = await llm.ainvoke([SystemMessage(content=prompt)])
    response_content = response_obj.content
    
    analysis = parse_coordinator_response(response_content)
    analysis['reasoning'] = response_content
    
    print(f"   ↳ Coordinator decided on agents: {analysis['required_agents']}")
    return {"results": {"coordinator_analysis": analysis}}


# ==============================================================================
# ✅ TEST BLOCK (Corrected)
# ==============================================================================
if __name__ == "__main__":
    from pathlib import Path
    import asyncio
    import json
    from app.services.llm_service import LLMService
    from app.services.data_manager import DataManager
    from app.graph.state import AcademicState
    from langchain_core.messages import HumanMessage

    async def main_test():
        """A self-contained async function to test the coordinator agent."""
        
        # --- 1. Setup Environment ---
        print("\n[1. Initializing services and loading data...]")
        llm_service = LLMService()
        data_manager = DataManager()
        
        # Load the dummy JSON data to create a realistic state
        # Assumes this script is run from the root `atlas_project` directory
        data_path = Path("./data")
        with open(data_path / "profile.json", "r") as f: profile_json = f.read()
        with open(data_path / "calendar.json", "r") as f: calendar_json = f.read()
        with open(data_path / "tasks.json", "r") as f: task_json = f.read()
        data_manager.load_data(profile_json, calendar_json, task_json)

        # --- 2. Create a Mock State for the Agent to Use ---
        user_request = "Help me plan my study schedule for next week for my Cognitive Psychology midterm."
        mock_state = AcademicState(
            messages=[HumanMessage(content=user_request)],
            profile=data_manager.get_student_profile("student_123"),
            calendar={"events": data_manager.get_upcoming_events()},
            tasks={"tasks": data_manager.get_active_tasks()},
            results={}
        )
        print("✅ Mock state created.")

        # --- 3. Test the Coordinator Agent ---
        print("\n[2. Testing Coordinator Agent...]")
        
        # Call the async agent function and await its result
        coord_output = await coordinator_agent(mock_state, llm_service)
        
        # Now you can safely use the result
        print("   ↳ Coordinator Output:", json.dumps(coord_output['results']['coordinator_analysis'], indent=2))
        print("\n✅ Coordinator agent test passed!")

    # --- Run the async test ---
    try:
        asyncio.run(main_test())
    except Exception as e:
        print(f"An error occurred during the test: {e}")
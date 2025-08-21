import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.graph.state import AcademicState
from app.services.llm_service import LLMService
from app.prompts.prompts import PROFILE_ANALYZER_PROMPT

async def profile_analyzer_agent(state: AcademicState, llm_service: LLMService) -> dict:
    """
    Analyzes the student profile to extract key learning patterns. 
    """
    print("--- (Node) Executing Profile Analyzer Agent ---")
    profile = state.get("profile", {})
    
    prompt = PROFILE_ANALYZER_PROMPT.format(profile=json.dumps(profile, indent=2))
    
    # *** CORRECTED LOGIC ***
    llm = llm_service.get_llm()
    # Using the original message structure from the reference code
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(profile)}
    ]
    response_obj = await llm.ainvoke(messages)
    
    return {"results": {"profile_analysis": {"analysis": response_obj.content}}}



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
    from app.agents.coordinator import coordinator_agent
    from app.agents.planner import PlannerAgent

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
            atlas_message=[HumanMessage(content=user_request)],
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
        
        
        # Test Profile Analyzer Agent
        print("\n[3. Testing Profile Analyzer Agent...]")
        profile_output = await profile_analyzer_agent(mock_state, llm_service)
        mock_state["results"].update(profile_output["results"])
        print("   ↳ Profile Analyzer Output:", profile_output['results']['profile_analysis']['analysis'][:100] + "...")
        print("\n✅ Profile analyzer agent test passed!")

        # Test Planner Agent
        print("\n[4. Testing Planner Agent...]")
        planner = PlannerAgent(llm_service)
        plan_res = await planner.plan_generator(mock_state)
        print("   ↳ Final Plan Output:", plan_res['results']['planner_output']['plan'][:200] + "...")
        print("\n✅ Planner agent test passed!")




    # --- Run the async test ---
    try:
        asyncio.run(main_test())
    except Exception as e:
        print(f"An error occurred during the test: {e}")
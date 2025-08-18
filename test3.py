# test_step3_agents.py

import asyncio
import json
from pathlib import Path
from langchain_core.messages import HumanMessage

# Import services and state needed for the test
from app.services.llm_service import LLMService
from app.services.data_manager import DataManager
from app.graph.state import AcademicState

# Import the agents to be tested
from app.agents.coordinator import coordinator_agent
from app.agents.profile_analyzer import profile_analyzer_agent
from app.agents.planner import PlannerAgent
from app.agents.notewriter import NoteWriterAgent
from app.agents.advisor import AdvisorAgent

async def main():
    """
    This script tests each agent function in isolation to ensure
    its logic and prompts are working correctly before building the graph.
    """
    print("\n--- Running Step 3: Agent Integration Test ---")

    # --- 1. Setup Environment ---
    print("\n[1. Initializing services and loading data...]")
    llm_service = LLMService()
    data_manager = DataManager()
    
    # Load the dummy JSON data to create a realistic state
    data_path = Path(__file__).parent / "data"
    with open(data_path / "profile.json", "r") as f: profile_json = f.read()
    with open(data_path / "calendar.json", "r") as f: calendar_json = f.read()
    with open(data_path / "tasks.json", "r") as f: task_json = f.read()
    data_manager.load_data(profile_json, calendar_json, task_json)

    # --- 2. Create a Mock State for Agents to Use ---
    user_request = "Help me plan my study schedule for next week for my Cognitive Psychology midterm."
    mock_state = AcademicState(
        messages=[HumanMessage(content=user_request)],
        profile=data_manager.get_student_profile("student_123"),
        calendar={"events": data_manager.get_upcoming_events()},
        tasks={"tasks": data_manager.get_active_tasks()},
        results={}
    )
    print("✅ Mock state created.")

    # --- 3. Test Each Agent Individually ---
    
    # Test Coordinator Agent
    print("\n[2. Testing Coordinator Agent...]")
    coord_output = await coordinator_agent(mock_state, llm_service)
    # Merge the result back into the state for the next agents
    mock_state["results"].update(coord_output["results"])
    print("   ↳ Coordinator Output:", json.dumps(mock_state['results']['coordinator_analysis'], indent=2))

    # Test Profile Analyzer Agent
    print("\n[3. Testing Profile Analyzer Agent...]")
    profile_output = await profile_analyzer_agent(mock_state, llm_service)
    mock_state["results"].update(profile_output["results"])
    print("   ↳ Profile Analyzer Output:", profile_output['results']['profile_analysis']['analysis'][:100] + "...")

    # Test Planner Agent
    print("\n[4. Testing Planner Agent...]")
    planner = PlannerAgent(llm_service)
    plan_res = await planner.plan_generator(mock_state)
    print("   ↳ Final Plan Output:", plan_res['results']['planner_output']['plan'][:200] + "...")

    # Test NoteWriter Agent
    print("\n[5. Testing NoteWriter Agent...]")
    notewriter = NoteWriterAgent(llm_service)
    notes_res = await notewriter.generate_notes(mock_state)
    print("   ↳ Notes Output:", notes_res['results']['notewriter_output']['notes'][:200] + "...")

    # Test Advisor Agent
    print("\n[6. Testing Advisor Agent...]")
    advisor = AdvisorAgent(llm_service)
    advice_res = await advisor.generate_guidance(mock_state)
    print("   ↳ Advice Output:", advice_res['results']['advisor_output']['advice'][:200] + "...")
    
    print("\n✅ All agent tests completed successfully!")

if __name__ == "__main__":
    # This allows us to run the async main function
    asyncio.run(main())
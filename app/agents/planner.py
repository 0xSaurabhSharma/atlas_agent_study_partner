# app/agents/planner.py

import json
from datetime import datetime
from typing import Dict
from langchain_core.messages import SystemMessage, HumanMessage

from app.graph.state import AcademicState
from app.services.llm_service import LLMService
from app.prompts.prompts import PLANNER_PROMPT
from .base import ReActAgent

def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converts datetime to "YYYY-MM-DDTHH:MM:SS" format
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


class PlannerAgent(ReActAgent):
    """Handles scheduling, time management, and study plan generation."""
    
    # The __init__ is now simpler. It just accepts the llm_service.
    # The super().__init__ handles setting self.llm_service = llm_service
    def __init__(self, llm_service: LLMService):
        super().__init__(llm_service)

    async def calendar_analyzer(self, state: AcademicState) -> Dict:
        print("--- (Node) Executing Planner: Calendar Analyzer ---")
        events = state["calendar"].get("events", [])
        prompt = "Analyze these calendar events and identify available time blocks, energy impacts, and conflicts.\nEvents: {events}"
        
        # 1. Get the default LLM from the service
        llm = self.llm_service.get_llm()
        
        # 2. Use the standard .ainvoke() method with proper messages
        response = await llm.ainvoke([
            HumanMessage(content=prompt.format(events=json.dumps(events)))
        ])
        
        return {"results": {"calendar_analysis": {"analysis": response.content}}}

    async def task_analyzer(self, state: AcademicState) -> Dict:
        print("--- (Node) Executing Planner: Task Analyzer ---")
        tasks = state["tasks"].get("tasks", [])
        prompt = "Analyze this task list and create a priority structure considering urgency and complexity.\nTasks: {tasks}"
        
        llm = self.llm_service.get_llm()
        
        tasks_json = json.dumps(tasks, default=json_serializer)
        
        # response = await llm.ainvoke([
        #     HumanMessage(content=prompt.format(tasks=json.dumps(tasks)))
        # ])
            
        response = await llm.ainvoke([
            HumanMessage(content=prompt.format(tasks=tasks_json))
        ])
        
        return {"results": {"task_analysis": {"analysis": response.content}}}

    async def plan_generator(self, state: AcademicState) -> Dict:
        print("--- (Node) Executing Planner: Plan Generator ---")
        
        profile_analysis = state.get("results", {}).get("profile_analysis", {}).get("analysis", "No profile analysis provided.")
        calendar_analysis = state.get("results", {}).get("calendar_analysis", {}).get("analysis", "No calendar analysis provided.")
        task_analysis = state.get("results", {}).get("task_analysis", {}).get("analysis", "No task analysis provided.")
        request = state["messages"][-1].content
        
        prompt = PLANNER_PROMPT.format(
            profile_analysis=profile_analysis,
            calendar_analysis=calendar_analysis,
            task_analysis=task_analysis,
            request=request
        )
        
        llm = self.llm_service.get_llm()
        
        response = await llm.ainvoke([
            SystemMessage(content=prompt),
            HumanMessage(content=request)
        ], config={"configurable": {"temperature": 0.5}}) # Pass config like this
        
        return {"results": {"planner_output": {"plan": response.content}}}
    
    






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
    from app.agents.profile_analyzer import profile_analyzer_agent

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
        
        
        
        # --- 4. Test the Planner Agent's methods sequentially ---
        print("\n[3. Testing Planner Agent Methods...]")
        planner = PlannerAgent(llm_service)
        print("🌼🥺😃🛵")
        # Step 4a: Test Calendar Analyzer
        print("\n   - Testing calendar_analyzer...")
        calendar_res = await planner.calendar_analyzer(mock_state)
        mock_state["results"].update(calendar_res["results"]) # Update state with the result
        print("     ↳ Calendar Analysis Output:", calendar_res['results']['calendar_analysis']['analysis'][:100] + "...")
        print("🌼🥺😃")
        # Step 4b: Test Task Analyzer
        print("\n   - Testing task_analyzer...")
        task_res = await planner.task_analyzer(mock_state)
        mock_state["results"].update(task_res["results"]) # Update state again
        print("     ↳ Task Analysis Output:", task_res['results']['task_analysis']['analysis'][:100] + "...")
        print("🌼🥺")
        # Step 4c: Test Plan Generator (now with the analysis it needs)
        print("\n   - Testing plan_generator...")
        plan_res = await planner.plan_generator(mock_state)
        print("     ↳ Final Plan Output:", plan_res['results']['planner_output']['plan'][:200] + "...")
        print("🌼")
        print("\n✅ Planner agent test passed!")




    # --- Run the async test ---
    try:
        asyncio.run(main_test())
    except Exception as e:
        print(f"An error occurred during the test: {e}")
import json
from app.graph.state import AcademicState
from langchain_core.messages import HumanMessage
from app.services.llm_service import LLMService
from app.agents.base import ReActAgent
from typing import Dict


class AdvisorAgent(ReActAgent):
    """Provides personalized academic guidance and time management advice."""

    # *** CORRECTED LOGIC ***
    def __init__(self, llm_service: LLMService):
        super().__init__(llm_service)

    async def analyze_situation(self, state: AcademicState) -> Dict:
        profile = state["profile"]
        prompt = f"""
        Analyze the student's situation based on their profile and current request to determine the best guidance approach.
        - Profile: {json.dumps(profile)}
        - Request: {state['atlas_message'][-1].content}
        Analyze: Current challenges, learning style compatibility, time/stress management needs.
        """
        # messages = [{"role": "system", "content": prompt}]
        messages = [HumanMessage(content=prompt)]

        llm = self.llm_service.get_llm()
        response_obj = await llm.ainvoke(messages)
        return {"results": {"situation_analysis": {"analysis": response_obj.content}}}

    async def generate_guidance(self, state: AcademicState) -> Dict:
        analysis = state["results"].get("situation_analysis", {})
        prompt = f"""
        Generate personalized academic guidance based on the analysis.
        ANALYSIS: {analysis.get('analysis', 'N/A')}
        FORMAT: Provide actionable steps for schedule optimization, energy management, support strategies, and emergency protocols.
        """
        # messages = [{"role": "system", "content": prompt}]
        messages = [HumanMessage(content=prompt)]

        llm = self.llm_service.get_llm()
        response_obj = await llm.ainvoke(messages)
        return {"results": {"advisor_output": {"advice": response_obj.content}}}


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
    from app.agents.notewriter import NoteWriterAgent
    from app.agents.advisor import AdvisorAgent

    async def main_test():
        """A self-contained async function to test the coordinator agent."""

        # --- 1. Setup Environment ---
        print("\n[1. Initializing services and loading data...]")
        llm_service = LLMService()
        data_manager = DataManager()

        # Load the dummy JSON data to create a realistic state
        # Assumes this script is run from the root `atlas_project` directory
        data_path = Path("./data")
        with open(data_path / "profile.json", "r") as f:
            profile_json = f.read()
        with open(data_path / "calendar.json", "r") as f:
            calendar_json = f.read()
        with open(data_path / "tasks.json", "r") as f:
            task_json = f.read()
        data_manager.load_data(profile_json, calendar_json, task_json)

        # --- 2. Create a Mock State for the Agent to Use ---
        user_request = "Help me plan my study schedule for next week for my Cognitive Psychology midterm."
        mock_state = AcademicState(
            atlas_message=[HumanMessage(content=user_request)],
            profile=data_manager.get_student_profile("student_123"),
            calendar={"events": data_manager.get_upcoming_events()},
            tasks={"tasks": data_manager.get_active_tasks()},
            results={},
        )
        print("✅ Mock state created.")

        # --- 3. Test the Coordinator Agent ---
        print("\n[2. Testing Coordinator Agent...]")

        # Call the async agent function and await its result
        coord_output = await coordinator_agent(mock_state, llm_service)

        # Now you can safely use the result
        print(
            "   ↳ Coordinator Output:",
            json.dumps(coord_output["results"]["coordinator_analysis"], indent=2),
        )
        print("\n✅ Coordinator agent test passed!")

        # Test Profile Analyzer Agent
        print("\n[3. Testing Profile Analyzer Agent...]")
        profile_output = await profile_analyzer_agent(mock_state, llm_service)
        mock_state["results"].update(profile_output["results"])
        print(
            "   ↳ Profile Analyzer Output:",
            profile_output["results"]["profile_analysis"]["analysis"][:100] + "...",
        )
        print("\n✅ Profile analyzer agent test passed!")

        # Test Planner Agent
        print("\n[4. Testing Planner Agent...]")
        planner = PlannerAgent(llm_service)
        plan_res = await planner.plan_generator(mock_state)
        print(
            "   ↳ Final Plan Output:",
            plan_res["results"]["planner_output"]["plan"][:200] + "...",
        )
        print("\n✅ Planner agent test passed!")

        # Test NoteWriter Agent
        print("\n[5. Testing NoteWriter Agent...]")
        notewriter = NoteWriterAgent(llm_service)
        notes_res = await notewriter.generate_notes(mock_state)
        print(
            "   ↳ Notes Output:",
            notes_res["results"]["notewriter_output"]["notes"][:200] + "...",
        )
        print("\n✅ Notewriter agent test passed!")

        # Test Advisor Agent
        print("\n[6. Testing Advisor Agent...]")
        advisor = AdvisorAgent(llm_service)
        style_analysis = advisor.analyze_situation(mock_state)
        print("style..........")
        advice_res = await advisor.generate_guidance(mock_state)
        print(
            "   ↳ Advice Output:",
            advice_res["results"]["advisor_output"]["advice"][:200] + "...",
        )
        print("\n✅ Advisor agent test passed!")

        print("\n✅ All agent tests completed successfully!")

    # --- Run the async test ---
    try:
        asyncio.run(main_test())
    except Exception as e:
        print(f"An error occurred during the test: {e}")

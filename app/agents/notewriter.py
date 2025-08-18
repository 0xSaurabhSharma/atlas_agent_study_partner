import json
from langchain_core.messages import HumanMessage
from app.graph.state import AcademicState
from app.services.llm_service import LLMService
from app.agents.base import ReActAgent
from typing import Dict

class NoteWriterAgent(ReActAgent):
    """Creates personalized study materials and content summaries."""
    
    # *** CORRECTED LOGIC ***
    def __init__(self, llm_service: LLMService):
        super().__init__(llm_service)
    
    async def analyze_learning_style(self, state: AcademicState) -> Dict:
        profile = state["profile"]
        learning_style = profile.get("learning_preferences", {}).get("learning_style", {})
        prompt = f"""
        Analyze content requirements based on the student's learning style and request.
        - Learning Style: {json.dumps(learning_style)}
        - Request: {state['messages'][-1].content}
        Focus on: Key Topics (80/20 principle), Learning Style Adaptations, and Quick Reference Format.
        """
        # prompt = [{"role": "system", "content": prompt}]
        prompt = [HumanMessage(content=prompt)]
        
        llm = self.llm_service.get_llm()
        response_obj = await llm.ainvoke(prompt)
        return {"results": {"learning_analysis": {"analysis": response_obj.content}}}

    async def generate_notes(self, state: AcademicState) -> Dict:
        analysis = state["results"].get("learning_analysis", {})
        prompt = f"""
        Create concise, high-impact study materials based on the analysis.
        ANALYSIS: {analysis.get('analysis', 'N/A')}
        REQUEST: {state['messages'][-1].content}
        FORMAT: **INTENSIVE STUDY GUIDE** with weekly/daily focus areas and core concepts.
        """
        # prompt = [{"role": "system", "content": prompt}]
        prompt = [HumanMessage(content=prompt)]
        
        llm = self.llm_service.get_llm()
        response_obj = await llm.ainvoke(prompt)
        return {"results": {"notewriter_output": {"notes": response_obj.content}}}
    
    
    
    
    
    



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
        
        
        
        # Test NoteWriter Agent
        print("\n[5. Testing NoteWriter Agent...]")
        notewriter = NoteWriterAgent(llm_service)
        print("   ↳ Running learning style analysis...")
        print("🌼")
        analysis_res = await notewriter.analyze_learning_style(mock_state)
        print("🌼")
        notes_res = await notewriter.generate_notes(mock_state)
        print("   ↳ Notes Output:", notes_res['results']['notewriter_output']['notes'][:200] + "...")
        print("\n✅ Notewriter agent test passed!")





    # --- Run the async test ---
    try:
        asyncio.run(main_test())
    except Exception as e:
        print(f"An error occurred during the test: {e}")    
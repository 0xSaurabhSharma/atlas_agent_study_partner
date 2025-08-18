# streamlit_app.py

import streamlit as st
import asyncio
from pathlib import Path
from langchain_core.messages import HumanMessage

# Import the core components from your app
from app.graph.graph import create_graph
from app.graph.state import AcademicState
from app.services.data_manager import DataManager

# --- Page Configuration ---
st.set_page_config(
    page_title="ATLAS Academic Assistant",
    page_icon="🎓",
    layout="wide"
)

# --- Main Application ---
st.title("🎓 ATLAS: Your Personal Academic Assistant")
st.markdown("Enter your academic challenge, and let the agent team create a plan for you.")

# --- Helper Function to Run the Graph ---
async def run_graph(user_request: str, data_manager: DataManager):
    """
    Sets up the initial state and runs the LangGraph workflow,
    streaming the results back to the Streamlit UI.
    """
    graph = create_graph()

    initial_state = AcademicState(
        messages=[HumanMessage(content=user_request)],
        profile=data_manager.get_student_profile("student_123"),
        calendar={"events": data_manager.get_upcoming_events()},
        tasks={"tasks": data_manager.get_active_tasks()},
        results={}
    )

    # Placeholders for real-time updates
    final_plan_placeholder = st.empty()
    progress_expander = st.expander("🤖 Agent Progress...")
    progress_placeholder = progress_expander.empty()
    
    full_log = ""
    final_plan = ""

    async for event in graph.astream(initial_state):
        # The event is a dictionary with the node name as the key
        node_name = list(event.keys())[0]
        node_output = event[node_name]
        
        # Update the progress log
        full_log += f"**Running Node: `{node_name}`**\n\n"
        progress_placeholder.markdown(full_log)

        # Check for the final plan from the planner agent
        if "planner_output" in node_output.get("results", {}):
            final_plan = node_output["results"]["planner_output"].get("plan", "")

    # Display the final, complete plan
    final_plan_placeholder.markdown("--- \n### Your Generated Plan")
    final_plan_placeholder.markdown(final_plan)

# --- Load Data ---
# This runs once when the app starts
@st.cache_resource
def load_data_manager():
    data_manager = DataManager()
    data_path = Path(__file__).parent / "data"
    with open(data_path / "profile.json", "r") as f: profile_json = f.read()
    with open(data_path / "calendar.json", "r") as f: calendar_json = f.read()
    with open(data_path / "tasks.json", "r") as f: task_json = f.read()
    data_manager.load_data(profile_json, calendar_json, task_json)
    return data_manager

try:
    dm = load_data_manager()

    # --- User Input ---
    user_input = st.text_area(
        "What do you need help with?",
        "Help me plan my study schedule for next week for my Cognitive Psychology midterm.",
        height=100
    )

    if st.button("Generate Plan", type="primary"):
        if user_input:
            with st.spinner("🤖 The agent team is working on your request... Please wait."):
                # Run the asynchronous graph function from Streamlit's synchronous context
                asyncio.run(run_graph(user_input, dm))
        else:
            st.warning("Please enter a request.")

except FileNotFoundError:
    st.error(
        "Error: Data files not found. "
        "Please make sure you have `profile.json`, `calendar.json`, and `tasks.json` "
        "in a `data/` folder in your project's root directory."
    )
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
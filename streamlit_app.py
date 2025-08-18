# streamlit_app.py

import streamlit as st
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from langchain_core.messages import HumanMessage

# Import the core components from your app
from app.graph.graph import create_graph
from app.graph.state import AcademicState

# --- Page Configuration ---
st.set_page_config(
    page_title="ATLAS Academic Assistant",
    page_icon="🎓",
    layout="wide"
)

# --- Helper Functions to Parse User Input ---
def parse_text_to_list(text: str) -> list:
    """Splits a multiline text into a list of non-empty strings."""
    return [line.strip() for line in text.split('\n') if line.strip()]

def format_events(lines: list) -> list:
    """Converts lines of text into the calendar event JSON structure."""
    events = []
    now = datetime.now(timezone.utc)
    for line in lines:
        events.append({
            "summary": line,
            "start": {"dateTime": now.isoformat()},
            "end": {"dateTime": now.isoformat()}
        })
    return events

def format_tasks(lines: list) -> list:
    """Converts lines of text into the tasks JSON structure."""
    tasks = []
    for line in lines:
        tasks.append({
            "title": line,
            "due": "2025-09-01T23:59:59Z", # Using a fixed future date for simplicity
            "status": "needsAction"
        })
    return tasks


# --- Main Application ---
st.title("🎓 ATLAS: Your Personal Academic Assistant")
st.markdown("Use the sidebar to enter your academic profile, then describe your challenge below.")

# --- Sidebar for User Input ---
st.sidebar.header("Your Academic Profile")
student_name = st.sidebar.text_input("Name", "Sarah")
major = st.sidebar.text_input("Major", "Psychology")
learning_style = st.sidebar.selectbox(
    "Primary Learning Style",
    ["visual", "kinesthetic", "auditory", "reading/writing"],
    index=0
)
courses_input = st.sidebar.text_area(
    "Current Courses (one per line)",
    "Cognitive Psychology\nStatistics for Behavioral Sciences",
    height=100
)
events_input = st.sidebar.text_area(
    "Upcoming Events this week (one per line)",
    "Neuroscience Club Meeting\nStudy Group for Stats",
    height=100
)
tasks_input = st.sidebar.text_area(
    "Active Tasks/Assignments (one per line)",
    "Chapter 3 Summary\nStatistics Problem Set",
    height=100
)


# --- Helper Function to Run the Graph ---
async def run_graph(user_request: str, initial_state: dict):
    """
    Runs the LangGraph workflow with the dynamically created state.
    """
    graph = create_graph()

    # Placeholders for real-time updates
    final_output_placeholder = st.empty()
    progress_expander = st.expander("🤖 Agent Progress...", expanded=True)
    progress_placeholder = progress_expander.empty()
    
    full_log = ""
    final_outputs = {}

    async for event in graph.astream(initial_state):
        node_name = list(event.keys())[0]
        node_output = event[node_name]
        
        # Update the progress log
        full_log += f"**✅ Agent Executed: `{node_name}`**\n\n"
        progress_placeholder.markdown(full_log)

        # Store the output from each agent node
        if "results" in node_output:
            final_outputs.update(node_output["results"])

    # Display the final, combined outputs
    final_output_placeholder.markdown("--- \n### 💡 Your Generated Plan & Insights")
    
    if "planner_output" in final_outputs:
        st.markdown("#### 📅 Study Plan")
        st.markdown(final_outputs["planner_output"].get("plan", "No plan generated."))
        
    if "notewriter_output" in final_outputs:
        st.markdown("#### 📝 Generated Notes")
        st.markdown(final_outputs["notewriter_output"].get("notes", "No notes generated."))
        
    if "advisor_output" in final_outputs:
        st.markdown("#### 👩‍🏫 Personal Advice")
        st.markdown(final_outputs["advisor_output"].get("advice", "No advice generated."))


# --- User Input & Button to Run ---
user_input = st.text_area(
    "What do you need help with?",
    "I'm feeling overwhelmed. Help me create a study plan for my Cognitive Psychology midterm and summarize the key concepts for my visual learning style.",
    height=150
)

if st.button("Generate Plan", type="primary", use_container_width=True):
    if user_input and student_name and major and courses_input:
        with st.spinner("🤖 The agent team is assembling and working on your request..."):
            # 1. Build the profile, calendar, and task data from sidebar inputs
            profile_data = {
                "id": "student_123",
                "personal_info": {"name": student_name, "major": major},
                "learning_preferences": {"learning_style": {"primary": learning_style}},
                "academic_info": {"current_courses": [{"name": c} for c in parse_text_to_list(courses_input)]}
            }
            
            calendar_data = {"events": format_events(parse_text_to_list(events_input))}
            tasks_data = {"tasks": format_tasks(parse_text_to_list(tasks_input))}

            # 2. Assemble the initial state for the graph
            initial_state = AcademicState(
                messages=[HumanMessage(content=user_input)],
                profile=profile_data,
                calendar=calendar_data,
                tasks=tasks_data,
                results={}
            )

            # 3. Run the graph with the dynamic state
            asyncio.run(run_graph(user_input, initial_state))
    else:
        st.warning("Please fill in your profile details in the sidebar and enter a request.")









# # streamlit_app.py

# import streamlit as st
# import asyncio
# from pathlib import Path
# from langchain_core.messages import HumanMessage

# # Import the core components from your app
# from app.graph.graph import create_graph
# from app.graph.state import AcademicState
# from app.services.data_manager import DataManager

# # --- Page Configuration ---
# st.set_page_config(
#     page_title="ATLAS Academic Assistant",
#     page_icon="🎓",
#     layout="wide"
# )

# # --- Main Application ---
# st.title("🎓 ATLAS: Your Personal Academic Assistant")
# st.markdown("Enter your academic challenge, and let the agent team create a plan for you.")

# # --- Helper Function to Run the Graph ---
# async def run_graph(user_request: str, data_manager: DataManager):
#     """
#     Sets up the initial state and runs the LangGraph workflow,
#     streaming the results back to the Streamlit UI.
#     """
#     graph = create_graph()

#     initial_state = AcademicState(
#         messages=[HumanMessage(content=user_request)],
#         profile=data_manager.get_student_profile("student_123"),
#         calendar={"events": data_manager.get_upcoming_events()},
#         tasks={"tasks": data_manager.get_active_tasks()},
#         results={}
#     )

#     # Placeholders for real-time updates
#     final_plan_placeholder = st.empty()
#     progress_expander = st.expander("🤖 Agent Progress...")
#     progress_placeholder = progress_expander.empty()
    
#     full_log = ""
#     final_plan = ""

#     async for event in graph.astream(initial_state):
#         # The event is a dictionary with the node name as the key
#         node_name = list(event.keys())[0]
#         node_output = event[node_name]
        
#         # Update the progress log
#         full_log += f"**Running Node: `{node_name}`**\n\n"
#         progress_placeholder.markdown(full_log)

#         # Check for the final plan from the planner agent
#         if "planner_output" in node_output.get("results", {}):
#             final_plan = node_output["results"]["planner_output"].get("plan", "")

#     # Display the final, complete plan
#     final_plan_placeholder.markdown("--- \n### Your Generated Plan")
#     final_plan_placeholder.markdown(final_plan)

# # --- Load Data ---
# # This runs once when the app starts
# @st.cache_resource
# def load_data_manager():
#     data_manager = DataManager()
#     data_path = Path(__file__).parent / "data"
#     with open(data_path / "profile.json", "r") as f: profile_json = f.read()
#     with open(data_path / "calendar.json", "r") as f: calendar_json = f.read()
#     with open(data_path / "tasks.json", "r") as f: task_json = f.read()
#     data_manager.load_data(profile_json, calendar_json, task_json)
#     return data_manager

# try:
#     dm = load_data_manager()

#     # --- User Input ---
#     user_input = st.text_area(
#         "What do you need help with?",
#         "Help me plan my study schedule for next week for my Cognitive Psychology midterm.",
#         height=100
#     )

#     if st.button("Generate Plan", type="primary"):
#         if user_input:
#             with st.spinner("🤖 The agent team is working on your request... Please wait."):
#                 # Run the asynchronous graph function from Streamlit's synchronous context
#                 asyncio.run(run_graph(user_input, dm))
#         else:
#             st.warning("Please enter a request.")

# except FileNotFoundError:
#     st.error(
#         "Error: Data files not found. "
#         "Please make sure you have `profile.json`, `calendar.json`, and `tasks.json` "
#         "in a `data/` folder in your project's root directory."
#     )
# except Exception as e:
#     st.error(f"An unexpected error occurred: {e}")
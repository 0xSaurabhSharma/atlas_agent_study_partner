# app/graph/graph.py

from functools import partial
from typing import List

from langgraph.graph import StateGraph, END

# Core components
from app.graph.state import AcademicState
from app.services.llm_service import LLMService

# Import all agent functions and classes
from app.agents.coordinator import coordinator_agent
from app.agents.profile_analyzer import profile_analyzer_agent
from app.agents.planner import PlannerAgent
from app.agents.notewriter import NoteWriterAgent
from app.agents.advisor import AdvisorAgent

# This router function is correct and doesn't need changes.
def agent_router(state: AcademicState) -> List[str]:
    """Routes the workflow to the necessary agents based on the coordinator's decision."""
    results = state.get("results", {})
    coordinator_analysis = results.get("coordinator_analysis", {})
    required_agents = coordinator_analysis.get("required_agents", ["PLANNER"])
    print(f"   ↳ Router: Activating workflows for: {required_agents}")
    return [agent.lower() for agent in required_agents]

# --- Graph Builder ---
def create_graph() -> StateGraph:
    """
    Creates and compiles the main workflow graph for the ATLAS system.
    """
    print("✅ Initializing agents and compiling the graph...")
    
    llm_service = LLMService()
    planner = PlannerAgent(llm_service)
    notewriter = NoteWriterAgent(llm_service)
    advisor = AdvisorAgent(llm_service)

    # *** CORRECTED LOGIC ***
    # Use functools.partial to "pre-fill" the llm_service argument for our agent nodes.
    # This correctly passes the async functions to the graph.
    coordinator_node = partial(coordinator_agent, llm_service=llm_service)
    profile_analyzer_node = partial(profile_analyzer_agent, llm_service=llm_service)

    workflow = StateGraph(AcademicState)

    # Add nodes using the partial functions
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("profile_analyzer", profile_analyzer_node)
    workflow.add_node("planner", planner.plan_generator)
    workflow.add_node("notewriter", notewriter.generate_notes)
    workflow.add_node("advisor", advisor.generate_guidance)

    # --- Edges remain the same ---
    workflow.set_entry_point("coordinator")
    workflow.add_edge("coordinator", "profile_analyzer")

    workflow.add_conditional_edges(
        "profile_analyzer",
        agent_router,
        {
            "planner": "planner",
            "notewriter": "notewriter",
            "advisor": "advisor"
        }
    )

    workflow.add_edge("planner", END)
    workflow.add_edge("notewriter", END)
    workflow.add_edge("advisor", END)
    
    graph = workflow.compile()
    print("✅ Graph compiled successfully.")
    return graph












# from typing import Dict

# from langgraph.graph import StateGraph, END, START

# # Core components
# from app.graph.state import AcademicState
# from app.services.llm_service import LLMService

# # Import all agent classes and standalone agent functions
# from app.agents.coordinator import coordinator_agent
# from app.agents.profile_analyzer import profile_analyzer_agent
# from app.agents.planner import PlannerAgent
# from app.agents.notewriter import NoteWriterAgent
# from app.agents.advisor import AdvisorAgent

# # This simple node acts as a "join" point, waiting for all parallel branches to finish.
# def join_results(state: AcademicState) -> Dict:
#     """A simple node to consolidate results from parallel agent runs before ending."""
#     print("--- (Node) Joining Agent Results ---")
#     print("   ↳ All parallel workflows have completed.")
#     # The state is already updated by the reducers, so we just pass it along.
#     return {}

# # --- Graph Builder ---
# def create_graph() -> StateGraph:
#     """
#     Creates and compiles the main workflow graph for the ATLAS system,
#     implementing a parallel execution architecture.
#     """
#     print("✅ Initializing agents and compiling the graph...")
    
#     # Initialize services and agents which will be used by the nodes
#     llm_service = LLMService()
#     planner = PlannerAgent(llm_service)
#     notewriter = NoteWriterAgent(llm_service)
#     advisor = AdvisorAgent(llm_service)

#     # Define the workflow graph
#     workflow = StateGraph(AcademicState)

#     # --- Add all 10 Nodes to the Graph ---
#     # 1. Core coordination nodes
#     workflow.add_node("coordinator", lambda state: coordinator_agent(state, llm_service))
#     workflow.add_node("profile_analyzer", lambda state: profile_analyzer_agent(state, llm_service))
    
#     # 2. Planner agent's internal step-by-step nodes
#     workflow.add_node("planner_calendar", planner.calendar_analyzer)
#     workflow.add_node("planner_task", planner.task_analyzer)
#     workflow.add_node("planner_generate", planner.plan_generator)

#     # 3. Notewriter agent's internal step-by-step nodes
#     workflow.add_node("notewriter_analyze", notewriter.analyze_learning_style)
#     workflow.add_node("notewriter_generate", notewriter.generate_notes)
    
#     # 4. Advisor agent's internal step-by-step nodes
#     workflow.add_node("advisor_analyze", advisor.analyze_situation)
#     workflow.add_node("advisor_generate", advisor.generate_guidance)

#     # 5. The final "join" node
#     workflow.add_node("joiner", join_results)

#     # --- Add Edges to Define the Workflow ---

#     # 1. Start of the workflow
#     workflow.set_entry_point("coordinator")
#     workflow.add_edge("coordinator", "profile_analyzer")

#     # 2. After profile analysis, branch to all three agent workflows to run in parallel
#     workflow.add_edge("profile_analyzer", "planner_calendar")
#     workflow.add_edge("profile_analyzer", "notewriter_analyze")
#     workflow.add_edge("profile_analyzer", "advisor_analyze")

#     # 3. Define the internal sequence for the Planner Agent workflow
#     workflow.add_edge("planner_calendar", "planner_task")
#     workflow.add_edge("planner_task", "planner_generate")
#     workflow.add_edge("planner_generate", "joiner") # End at the joiner node

#     # 4. Define the internal sequence for the NoteWriter Agent workflow
#     workflow.add_edge("notewriter_analyze", "notewriter_generate")
#     workflow.add_edge("notewriter_generate", "joiner") # End at the joiner node

#     # 5. Define the internal sequence for the Advisor Agent workflow
#     workflow.add_edge("advisor_analyze", "advisor_generate")
#     workflow.add_edge("advisor_generate", "joiner") # End at the joiner node

#     # 6. The joiner node is the last step before ending the graph
#     workflow.add_edge("joiner", END)
    
#     # Compile the graph into a runnable object
#     graph = workflow.compile()
#     print("✅ Graph compiled successfully.")
#     return graph
















# from typing import List

# from langgraph.graph import StateGraph, END

# # Core components
# from app.graph.state import AcademicState
# from app.services.llm_service import LLMService

# # Import all agent functions that will be nodes in our graph
# from app.agents.coordinator import coordinator_agent
# from app.agents.profile_analyzer import profile_analyzer_agent
# from app.agents.planner import PlannerAgent
# from app.agents.notewriter import NoteWriterAgent
# from app.agents.advisor import AdvisorAgent

# # --- Graph Router ---
# def agent_router(state: AcademicState) -> List[str]:
#     """
#     This is the conditional edge. It directs the workflow to the necessary
#     agent sub-graphs based on the coordinator's decision.
#     LangGraph will execute these branches in parallel.
#     """
#     results = state.get("results", {})
#     coordinator_analysis = results.get("coordinator_analysis", {})
#     required_agents = coordinator_analysis.get("required_agents", [])
    
#     # Default to planner if no specific agents are identified
#     if not required_agents:
#         return ["planner"]
        
#     print(f"   ↳ Router: Activating the following agent workflows: {required_agents}")
#     return [agent.lower() for agent in required_agents]

# # --- Graph Builder ---
# def create_graph() -> StateGraph:
#     """
#     Creates and compiles the main workflow graph for the ATLAS system
#     using modern conditional branching for parallel execution.
#     """
#     print("✅ Compiling the agent graph...")
    
#     # Initialize services and agents. These will be used by the nodes.
#     llm_service = LLMService()
#     planner = PlannerAgent(llm_service)
#     notewriter = NoteWriterAgent(llm_service)
#     advisor = AdvisorAgent(llm_service)

#     # Define the workflow graph
#     workflow = StateGraph(AcademicState)

#     # --- Add Nodes ---
#     # Each node is a function or method that takes the state and returns a dictionary to update it.

#     # 1. Core coordination nodes
#     workflow.add_node("coordinator", lambda state: coordinator_agent(state, llm_service))
#     workflow.add_node("profile_analyzer", lambda state: profile_analyzer_agent(state, llm_service))

#     # 2. Specialized agent nodes (these will run in parallel based on the router)
#     workflow.add_node("planner", planner.plan_generator)
#     workflow.add_node("notewriter", notewriter.generate_notes)
#     workflow.add_node("advisor", advisor.generate_guidance)

#     # --- Add Edges ---
#     # This defines the sequence of operations.

#     workflow.set_entry_point("coordinator")
#     workflow.add_edge("coordinator", "profile_analyzer")

#     # The conditional edge allows for parallel execution of agent workflows.
#     # After the profile_analyzer, the agent_router is called. Based on its
#     # return value (e.g., ['planner', 'notewriter']), the graph will run
#     # the corresponding nodes in parallel.
#     workflow.add_conditional_edges(
#         "profile_analyzer",
#         agent_router,
#         {
#             "planner": "planner",
#             "notewriter": "notewriter",
#             "advisor": "advisor"
#         }
#     )

#     # After each specialized agent finishes, the graph ends.
#     workflow.add_edge("planner", END)
#     workflow.add_edge("notewriter", END)
#     workflow.add_edge("advisor", END)
    
#     # Compile the graph into a runnable object
#     graph = workflow.compile()
#     print("✅ Graph compiled successfully.")
#     return graph
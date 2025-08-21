from functools import partial
from typing import List, Dict

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

from app.graph.state import AcademicState
from app.services.llm_service import LLMService

from app.agents.coordinator import coordinator_agent
from app.agents.profile_analyzer import profile_analyzer_agent
from app.agents.planner import PlannerAgent
from app.agents.notewriter import NoteWriterAgent
from app.agents.advisor import AdvisorAgent
from app.agents.senior import SeniorAgent, should_continue
from app.tools.executor import tool_node

def master_router(state: AcademicState) -> str:
    """Reads the initial user message and decides which workflow to route to."""
    print("--- (Router) Executing Master Router ---")
    user_message = state["messages"][-1].content.lower()
    if "plan" in user_message or "schedule" in user_message:
        print("   ↳ Master Router: Routing to Academic Workflow.")
        return "academic_workflow"
    else:
        print("   ↳ Master Router: Routing to Senior Agent.")
        return "senior_agent"

def create_graph() -> StateGraph:
    """Creates and compiles the main workflow graph for the ATLAS system."""
    print("✅ Initializing agents and compiling graph...")

    llm_service = LLMService()
    planner = PlannerAgent(llm_service)
    notewriter = NoteWriterAgent(llm_service)
    advisor = AdvisorAgent(llm_service)
    senior_agent_instance = SeniorAgent(llm_service)
    coordinator_node = partial(coordinator_agent, llm_service=llm_service)
    profile_analyzer_node = partial(profile_analyzer_agent, llm_service=llm_service)

    workflow = StateGraph(AcademicState)

    # --- Add all Worker Nodes ---
    workflow.add_node("senior_agent", senior_agent_instance.run)
    workflow.add_node("tools", tool_node)
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("profile_analyzer", profile_analyzer_node)
    workflow.add_node("planner", planner.plan_generator)
    workflow.add_node("notewriter", notewriter.generate_notes)
    workflow.add_node("advisor", advisor.generate_guidance)
    
    def entry_point_node(state: AcademicState) -> Dict:
        """A simple node that officially starts the graph."""
        print("--- (Node) Graph Entry Point ---")
        return {}
    workflow.add_node("entry_point", entry_point_node)
    
    # --- Define Edges ---
    workflow.set_entry_point("entry_point")

    # The master_router now directs traffic to the correct starting node of each workflow
    workflow.add_conditional_edges(
        "entry_point",
        master_router,
        {
            "senior_agent": "senior_agent",           # Route directly to the Senior Agent
            "academic_workflow": "coordinator"      # Route directly to the Coordinator
        },
    )

    # --- Senior Agent Workflow (Tool-using loop) ---
    workflow.add_conditional_edges(
        "senior_agent", should_continue, {"tools": "tools", "__end__": END}
    )
    workflow.add_edge("tools", "senior_agent") # Loop back to the agent after tool execution

    # --- Academic Agent Workflow ---
    workflow.add_edge("coordinator", "profile_analyzer")
    workflow.add_conditional_edges(
        "profile_analyzer",
        lambda state: [
            agent.lower()
            for agent in state["results"].get("coordinator_analysis", {}).get("required_agents", [])
        ],
        {"planner": "planner", "notewriter": "notewriter", "advisor": "advisor"},
    )
    workflow.add_edge("planner", END)
    workflow.add_edge("notewriter", END)
    workflow.add_edge("advisor", END)

    graph = workflow.compile(checkpointer=memory)
    print("✅ Graph compiled successfully.")
    return graph
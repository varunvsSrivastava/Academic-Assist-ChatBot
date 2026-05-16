# graph/workflow.py

from langgraph.graph import StateGraph, END
from backend.graph.state import GraphState

# Agents
from backend.agents.retriever import retriever_agent
from backend.agents.validator import context_validator_agent
from backend.agents.generator import generator_agent
from backend.agents.critic import critic_agent
from backend.agents.improver import improver_agent

# Learning layer
from backend.learning.learning_engine import learning_step
from backend.app.config import config


# -------------------------------
# Initialize Graph
# -------------------------------
builder = StateGraph(GraphState)


# -------------------------------
# Add Nodes (Agents)
# -------------------------------
builder.add_node("retriever", retriever_agent)
builder.add_node("validator", context_validator_agent)
builder.add_node("generator", generator_agent)
builder.add_node("critic", critic_agent)
builder.add_node("improver", improver_agent)
builder.add_node("learning", learning_step)


# -------------------------------
# Define Flow
# -------------------------------
builder.set_entry_point("retriever")

builder.add_edge("retriever", "validator")


def route_after_validation(state: GraphState):
    if state.get("validation_passed", False):
        return "generator"

    return "end"


builder.add_conditional_edges(
    "validator",
    route_after_validation,
    {
        "generator": "generator",
        "end": END,
    }
)

builder.add_edge("generator", "critic")


# -------------------------------
# Conditional Routing Logic
# -------------------------------
def route_after_critic(state: GraphState):
    """
    Decide next step after evaluation
    """
    score = state.get("score", 0)
    iterations = state.get("iterations", 0)

    # Good answer → go to learning → end
    if score >= 0.8:
        return "learning"

    if iterations >= config.MAX_REFINEMENT_ITERATIONS:
        return "learning"

    # Bad answer → improve → re-evaluate
    return "improver"


builder.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "learning": "learning",
        "improver": "improver",
    }
)


# Loop: Improver → Critic (refinement loop)
builder.add_edge("improver", "critic")

# Final step
builder.add_edge("learning", END)


# -------------------------------
# Compile Graph
# -------------------------------
graph = builder.compile()
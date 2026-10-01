from langgraph.graph import END, START, StateGraph
from app.agents.nodes import analytics, hr, manager, tech
from app.agents.routing import after_node, route_next
from app.agents.state import InterviewState

def build_graph():
    g=StateGraph(InterviewState)
    g.add_node("hr", hr.run)
    g.add_node("tech", tech.run)
    g.add_node("manager", manager.run)
    g.add_node("analytics", analytics.run)

    g.add_conditional_edges(START, route_next)
    for name in ("hr", "tech", "manager"):
        g.add_conditional_edges(name, after_node)
    g.add_edge("analytics", END)
    return g.compile()

interview_graph=build_graph()
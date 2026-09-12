from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
import json
import sys
import os

sys.path.append(os.path.dirname(__file__))
from model_client import ModelClient

TURN_CEILING = 6

class AgentState(TypedDict):
    title: str
    content: str
    planner_proposal: Dict[str, Any]
    reviewer_feedback: Dict[str, Any]
    turn_count: int

client = ModelClient()


def planner_node(state: AgentState) -> Dict[str, Any]:
    print("---NODE: Planner---")
    prompt = f"""You are a Planner agent. Given a title and content, propose exactly 3 topical tags and a one-sentence summary (max 25 words).
Respond ONLY in valid JSON with keys "tags" (list of 3 strings) and "summary" (string).

Title: {state['title']}
Content: {state['content']}
"""
    response = client.complete([{"role": "user", "content": prompt}])
    try:
        proposal = json.loads(response)
    except json.JSONDecodeError:
        proposal = {"tags": [], "summary": ""}
    return {"planner_proposal": proposal}


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    print("---NODE: Reviewer---")
    proposal = state.get("planner_proposal", {})
    prompt = f"""You are a Reviewer agent. Check this draft against exactly these rules:
1. There must be exactly 3 tags.
2. Each tag must be between 3 and 30 characters.
3. The summary must be 25 words or fewer.

Do NOT reject for style, vagueness, or subjective quality. ONLY reject if one of the 3 rules above is literally violated.
Respond ONLY in valid JSON with keys "has_issues" (boolean) and "feedback" (string: which rule was violated, or "OK" if none).

Draft: {json.dumps(proposal)}
"""
    response = client.complete([{"role": "user", "content": prompt}])
    try:
        feedback = json.loads(response)
    except json.JSONDecodeError:
        feedback = {"has_issues": False, "feedback": "Could not parse reviewer output"}
    return {"reviewer_feedback": feedback}


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    print(f"---NODE: Supervisor (turn {state.get('turn_count', 0) + 1})---")
    return {"turn_count": state.get("turn_count", 0) + 1}


def router_logic(state: AgentState) -> str:
    if state.get("turn_count", 0) >= TURN_CEILING:
        print("---ROUTER: Turn ceiling hit, ending---")
        return END

    if not state.get("planner_proposal"):
        print("---ROUTER: No proposal yet -> Planner---")
        return "planner"

    if not state.get("reviewer_feedback"):
        print("---ROUTER: No feedback yet -> Reviewer---")
        return "reviewer"

    if state["reviewer_feedback"].get("has_issues"):
        print("---ROUTER: Has issues -> back to Planner---")
        return "planner"

    print("---ROUTER: No issues -> END---")
    return END


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("planner", planner_node)
    graph.add_node("reviewer", reviewer_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", router_logic, {
        "planner": "planner",
        "reviewer": "reviewer",
        END: END
    })
    graph.add_edge("planner", "supervisor")
    graph.add_edge("reviewer", "supervisor")

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    initial_state = {
        "title": "Prototype pollution in lodash",
        "content": "A vulnerability in lodash allows attackers to modify object prototypes, potentially leading to denial of service or remote code execution in applications that merge untrusted user input.",
        "planner_proposal": {},
        "reviewer_feedback": {},
        "turn_count": 0
    }

    for step in app.stream(initial_state):
        print(step)
        print("---")
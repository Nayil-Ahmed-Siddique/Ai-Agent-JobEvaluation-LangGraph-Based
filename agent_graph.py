from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from job_discovery import get_jobs


# -----------------------------
# Agent State Definition
# -----------------------------
class AgentState(TypedDict):
    jobs: List[Dict[str, Any]]
    skipped_jobs: List[Dict[str, Any]]
    roles_targeted: List[str]
    max_experience_allowed: int
    decisions: List[Dict[str, Any]]


# -----------------------------
# Graph Setup
# -----------------------------
graph = StateGraph(AgentState)


# -----------------------------
# Nodes
# -----------------------------
def discover_jobs_node(state: AgentState) -> AgentState:
    """
    Pull jobs from job_discovery and inject into state.
    """
    result = get_jobs()   # MUST be a dict

    state["jobs"] = result["jobs"]
    state["skipped_jobs"] = result["skipped_jobs"]
    return state


def check_masked_node(state: AgentState) -> AgentState:
    clean = []
    skipped = state["skipped_jobs"]

    for job in state["jobs"]:
        if "*" in job["title"] or "*" in job["company"]:
            skipped.append({
                "title": job["title"],
                "company": job["company"],
                "reason": "masked"
            })
        else:
            clean.append(job)

    state["jobs"] = clean
    state["skipped_jobs"] = skipped
    return state


def check_role_node(state: AgentState) -> AgentState:
    clean = []
    skipped = state["skipped_jobs"]
    roles = [r.lower() for r in state["roles_targeted"]]

    for job in state["jobs"]:
        title = job["title"].lower()
        if any(role in title for role in roles):
            clean.append(job)
        else:
            skipped.append({
                "title": job["title"],
                "company": job["company"],
                "reason": "role_mismatch"
            })

    state["jobs"] = clean
    state["skipped_jobs"] = skipped
    return state


def check_experience_node(state: AgentState) -> AgentState:
    clean = []
    skipped = state["skipped_jobs"]
    max_exp = state["max_experience_allowed"]

    for job in state["jobs"]:
        req = job.get("required_experience")
        if req is not None and req > max_exp:
            skipped.append({
                "title": job["title"],
                "company": job["company"],
                "required_experience": req,
                "reason": "experience_too_high"
            })
        else:
            clean.append(job)

    state["jobs"] = clean
    state["skipped_jobs"] = skipped
    return state


def decide_apply_node(state: AgentState) -> AgentState:
    decisions = []
    for job in state["jobs"]:
        decisions.append({
            "title": job["title"],
            "company": job["company"],
            "decision": "apply"
        })

    state["decisions"] = decisions
    return state


# -----------------------------
# Graph Wiring
# -----------------------------
graph.add_node("discover_jobs", discover_jobs_node)
graph.add_node("check_masked", check_masked_node)
graph.add_node("check_role", check_role_node)
graph.add_node("check_experience", check_experience_node)
graph.add_node("decide_apply", decide_apply_node)

graph.set_entry_point("discover_jobs")
graph.add_edge("discover_jobs", "check_masked")
graph.add_edge("check_masked", "check_role")
graph.add_edge("check_role", "check_experience")
graph.add_edge("check_experience", "decide_apply")
graph.add_edge("decide_apply", END)

app = graph.compile()


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    initial_state = {
        "jobs": [],
        "skipped_jobs": [],
        "roles_targeted": ["ai engineer", "machine learning"],
        "max_experience_allowed": 5,
        "decisions": []
    }

    result = app.invoke(initial_state)
    print(result)

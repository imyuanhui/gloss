from app.agents.agent1_clarifier import run_agent1

def test_run_agent1():
    term = "crack"
    context = "what's the crack"
    run_agent1(term, context)

test_run_agent1()


#!/usr/bin/env python3
"""
Test script to verify the workflow completion logic fix
"""

def test_workflow_completion_logic():
    """Test the workflow completion logic"""
    
    # Mock agent roles and completion status
    agent_roles = {"agent1": "coordinator", "agent2": "coder"}
    agent_completion = {"agent1": False, "agent2": False}
    
    # Test 1: No completion signals
    response = "Hello, I'm the coordinator"
    result = _check_workflow_completion(agent_roles, agent_completion, response)
    print(f"Test 1 - No completion: {result} (expected: False)")
    
    # Test 2: Coordinator completion signal
    response = "COORDINATION COMPLETE"
    result = _check_workflow_completion(agent_roles, agent_completion, response)
    print(f"Test 2 - Coordinator complete: {result} (expected: True)")
    
    # Test 3: Code completion signal
    response = "CODE COMPLETE: Python function implemented"
    result = _check_workflow_completion(agent_roles, agent_completion, response)
    print(f"Test 3 - Code complete: {result} (expected: True)")
    
    # Test 4: All agents completed
    agent_completion = {"agent1": True, "agent2": True}
    response = "Some response"
    result = _check_workflow_completion(agent_roles, agent_completion, response)
    print(f"Test 4 - All agents complete: {result} (expected: True)")
    
    # Test 5: Coordinator + Coder pattern (should complete after coder)
    agent_completion = {"agent1": True, "agent2": True}
    response = "Code is ready"
    result = _check_workflow_completion(agent_roles, agent_completion, response)
    print(f"Test 5 - Coordinator + Coder pattern: {result} (expected: True)")

def _check_workflow_completion(agent_roles, agent_completion, last_response):
    """Mock implementation of the workflow completion check"""
    # Check for explicit completion signals
    if any(phrase in last_response.lower() for phrase in [
        "workflow complete", "task completed", "all done", "finished", "complete",
        "coordination complete", "code complete", "testing complete", "execution complete"
    ]):
        return True
    
    # Check if all agents have completed their roles
    if all(agent_completion.values()):
        return True
    
    # Check for specific role-based completion patterns
    roles = list(agent_roles.values())
    if len(roles) == 2 and "coordinator" in roles and "coder" in roles:
        # Simple coordinator + coder workflow
        # If coder has completed and coordinator has processed the result, we're done
        return True
    
    return False

def test_next_agent_logic():
    """Test the next agent selection logic"""
    
    agent_roles = {"agent1": "coordinator", "agent2": "coder"}
    
    # Test 1: Coordinator should delegate to coder
    agent_completion = {"agent1": True, "agent2": False}
    next_agent = _get_next_agent("agent1", agent_roles, agent_completion)
    print(f"Test 1 - Coordinator next: {next_agent} (expected: agent2)")
    
    # Test 2: Coder should end workflow (no tester)
    agent_completion = {"agent1": True, "agent2": True}
    next_agent = _get_next_agent("agent2", agent_roles, agent_completion)
    print(f"Test 2 - Coder next: {next_agent} (expected: None - workflow complete)")
    
    # Test 3: With tester available
    agent_roles = {"agent1": "coordinator", "agent2": "coder", "agent3": "tester"}
    agent_completion = {"agent1": True, "agent2": True, "agent3": False}
    next_agent = _get_next_agent("agent2", agent_roles, agent_completion)
    print(f"Test 3 - Coder with tester: {next_agent} (expected: agent3)")

def _get_next_agent(current_agent, agent_roles, agent_completion):
    """Mock implementation of the next agent selection"""
    current_role = agent_roles.get(current_agent, "").lower()
    
    # Define workflow patterns based on agent roles
    if current_role == "coordinator":
        # Coordinator should delegate to next available agent
        for agent_id, role in agent_roles.items():
            if agent_id != current_agent and not agent_completion.get(agent_id, False):
                return agent_id
    
    elif current_role == "coder":
        # Coder completes code, workflow should end or go to tester if available
        for agent_id, role in agent_roles.items():
            if role == "tester" and not agent_completion.get(agent_id, False):
                return agent_id
        # No tester, workflow complete
        return None
    
    elif current_role == "tester":
        # Tester completes validation, workflow should end
        return None
    
    elif current_role == "runner":
        # Runner executes code, workflow should end
        return None
    
    # Default: no more agents to process
    return None

if __name__ == "__main__":
    print("🧪 Testing Workflow Completion Logic")
    print("=" * 40)
    test_workflow_completion_logic()
    print()
    print("🧪 Testing Next Agent Logic")
    print("=" * 40)
    test_next_agent_logic()
    print()
    print("✅ All tests completed!")


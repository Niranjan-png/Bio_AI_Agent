from biopilot.agent import create_root_agent, dna_statistics_tool


def test_agent_is_constructed_with_constrained_tools() -> None:
    agent = create_root_agent()
    assert agent.name == "biopilot"
    assert len(agent.tools) == 4
    assert dna_statistics_tool("ACGT")["data"]["gc_percent"] == 50.0


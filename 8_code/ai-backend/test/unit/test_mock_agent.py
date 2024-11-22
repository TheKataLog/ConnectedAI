import pytest

from core.agent.mock_agent import MockAgent

from fixture import mock_outputs

@pytest.mark.asyncio
async def test_get_session_response(mock_outputs):
    config = {}
    agent = MockAgent(config, mock_outputs)

    response1 = await agent.get_session_response("session1", "message1")
    response2 = await agent.get_session_response("session1", "message2")
    response3 = await agent.get_session_response("session1", "message3")
    response4 = await agent.get_session_response("session1", "message4")

    assert response1 is not None
    assert response2 is not None
    assert response3 is not None
    assert str(response1) != str(response2)
    assert str(response2) != str(response3)
    assert str(response1) != str(response3)
    assert str(response1) == str(response4)
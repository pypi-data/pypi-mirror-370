# -*- coding: utf-8 -*-
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from genius_client_sdk.agent import GeniusAgent


class MockContinuation:
    def __init__(self):
        self.status_code = 202

    def json(self):
        return {
            "status": "pending",
            "id": "blahblahblah",
            "result_type": "LearnResponse",
            "result": None,
            "error": None,
            "created_at": datetime.now(),
        }

    def raise_for_status(self):
        pass


class MockResponse:
    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "status": "completed",
            "id": "blahblahblah",
            "result_type": "LearnResponse",
            "result": None,
            "error": "GPIL: inference: mocked error blah blah blah",
            "created_at": datetime.now(),
            "completed_at": datetime.now(),
        }

    def raise_for_status(self):
        pass


def test_server_invalid_response():
    """
    Regression test for GPIL-541
    Verifies that we have reasonable results, even if the server returns 200 for an error message.
    """
    agent = GeniusAgent()
    agent.model = MagicMock()

    with patch.object(
        agent._session,
        "post",
        return_value=MockContinuation(),
    ):
        with patch.object(
            agent._session,
            "get",
            return_value=MockResponse(),
        ):
            with pytest.raises(ValueError):
                agent.learn(
                    variables=["var1", "var2"], observations=[[0.1, 0.2], [0.3, 0.4]]
                )

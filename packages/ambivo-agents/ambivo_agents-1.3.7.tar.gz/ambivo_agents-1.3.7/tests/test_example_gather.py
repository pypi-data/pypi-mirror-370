#!/usr/bin/env python3
"""
Test for examples/gather_simple.py to validate GatherAgent basic flow.
"""
import asyncio
import os
import sys
import pytest

# Ensure project root is on sys.path so we can import examples.*
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ambivo_agents.agents.gather_agent import GatherAgent


@pytest.mark.asyncio
async def test_gather_example_flow(monkeypatch):
    # Patch submission to avoid network
    async def fake_submit(self, payload):
        return {"success": True, "status": 200, "response": "ok"}

    monkeypatch.setattr(GatherAgent, "_submit", fake_submit, raising=True)

    # Import the example runner
    from examples.gather_simple import run_demo

    responses = await run_demo()

    # We expect at least the first prompt, second prompt, and a final submission message
    assert len(responses) >= 3

    # First prompt should mention the yes/no question
    assert any("Are antivirus tools used" in r for r in responses), responses

    # After answering Yes, the conditional vendor question should be prompted
    assert any("Which antivirus vendor(s) do you use?" in r for r in responses), responses

    # Final response should indicate submission with successfully_collected status
    assert "Submitting your responses now" in responses[-1], responses[-1]
    assert "Status: successfully_collected" in responses[-1], responses[-1]

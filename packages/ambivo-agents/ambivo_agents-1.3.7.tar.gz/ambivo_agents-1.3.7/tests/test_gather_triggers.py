#!/usr/bin/env python3
"""
Tests for Conditional Dependent Question Logic in GatherAgent:
- Single-select with explicit condition_trigger_values
- Multi-select with explicit condition_trigger_values
"""
import json
import pytest

from ambivo_agents.agents.gather_agent import GatherAgent


class LocalMemory:
    """Minimal async in-memory context store used by GatherAgent in tests."""

    def __init__(self):
        self._ctx = {}

    async def store_context(self, key, value, conversation_id=None):
        self._ctx[key] = value

    async def get_context(self, key, conversation_id=None):
        return self._ctx.get(key)

    async def clear_memory(self, conversation_id=None):
        self._ctx.clear()


@pytest.mark.asyncio
async def test_single_select_triggers(monkeypatch):
    async def fake_submit(self, payload):
        return {"success": True, "status": 200, "response": "ok"}

    monkeypatch.setattr(GatherAgent, "_submit", fake_submit, raising=True)

    questionnaire = {
        "questions": [
            {
                "question_id": "q1",
                "text": "Select usage level",
                "type": "single-select",
                "required": True,
                "answer_option_dict_list": [
                    {"value": "No", "label": "No"},
                    {"value": "Basic", "label": "Basic"},
                    {"value": "Advanced", "label": "Advanced"},
                ],
            },
            {
                "question_id": "q1a",
                "text": "Please describe advanced usage details",
                "type": "free-text",
                "is_conditional": True,
                "parent_question_id": "q1",
                "condition_trigger_values": ["Advanced"],
                "required": False,
            },
            {
                "question_id": "q2",
                "text": "What is your email?",
                "type": "free-text",
                "required": True,
            },
        ]
    }

    agent = GatherAgent.create_advanced(
        agent_id="gather_trigger_single",
        memory_manager=LocalMemory(),
        llm_service=None,
        config={
            "gather": {
                "submission_endpoint": "http://localhost/void",
                "submission_method": "POST",
                "submission_headers": {"Content-Type": "application/json"},
                "memory_ttl_seconds": 3600,
            }
        },
    )

    # 1) Provide questionnaire
    r1 = await agent.chat(json.dumps(questionnaire))
    assert "Select usage level" in r1

    # 2) Answer with a non-trigger value -> child should be skipped, next should be q2
    r2 = await agent.chat("Basic")
    assert "What is your email?" in r2
    assert "Please describe advanced usage details" not in r2

    # 3) Answer q2 and finish -> should be successfully_collected
    r3 = await agent.chat("user@example.com")
    # Next prompt may auto-submit or ask to finish; we explicitly finish
    r4 = await agent.chat("finish")
    assert "Submitting your responses now" in r4
    assert "Status: successfully_collected" in r4


@pytest.mark.asyncio
async def test_multi_select_triggers(monkeypatch):
    async def fake_submit(self, payload):
        return {"success": True, "status": 200, "response": "ok"}

    monkeypatch.setattr(GatherAgent, "_submit", fake_submit, raising=True)

    questionnaire = {
        "questions": [
            {
                "question_id": "q1",
                "text": "Which cloud providers do you use?",
                "type": "multi-select",
                "required": True,
                "answer_option_dict_list": [
                    {"value": "AWS", "label": "AWS"},
                    {"value": "Azure", "label": "Azure"},
                    {"value": "GCP", "label": "GCP"},
                ],
            },
            {
                "question_id": "q1a",
                "text": "Please describe workloads on your selected AWS/GCP providers",
                "type": "free-text",
                "is_conditional": True,
                "parent_question_id": "q1",
                "condition_trigger_values": ["AWS", "GCP"],
                "required": False,
            },
            {
                "question_id": "q2",
                "text": "Company size?",
                "type": "single-select",
                "required": True,
                "answer_option_dict_list": [
                    {"value": "1-50", "label": "1-50"},
                    {"value": "51-200", "label": "51-200"},
                ],
            },
        ]
    }

    agent = GatherAgent.create_advanced(
        agent_id="gather_trigger_multi",
        memory_manager=LocalMemory(),
        llm_service=None,
        config={
            "gather": {
                "submission_endpoint": "http://localhost/void",
                "submission_method": "POST",
                "submission_headers": {"Content-Type": "application/json"},
                "memory_ttl_seconds": 3600,
            }
        },
    )

    # 1) Provide questionnaire
    r1 = await agent.chat(json.dumps(questionnaire))
    assert "Which cloud providers" in r1

    # 2) Case A: Select only non-trigger value -> child should be skipped
    r2 = await agent.chat("Azure")
    assert "Company size?" in r2
    assert "Please describe workloads" not in r2

    # Complete the flow for cleanliness
    r3 = await agent.chat("1-50")
    r4 = await agent.chat("finish")
    assert "Submitting your responses now" in r4

"""Tests for JpSegmenterAgent in conversation.py.

No real hass fixture is needed here: JpSegmenterAgent is constructed
directly with MagicMock() stand-ins for hass/entry, and user_input is a
duck-typed types.SimpleNamespace instead of a real
conversation.ConversationInput(...), since that dataclass's exact field
set varies across Home Assistant versions.
"""
import types
from unittest.mock import AsyncMock, MagicMock

from homeassistant.components import conversation
from homeassistant.components.conversation import HOME_ASSISTANT_AGENT
from homeassistant.helpers import intent

from custom_components.jp_segmenter_assistant.conversation import (
    JpSegmenterAgent,
    _normalize_segmented_text,
    _tokenize_text,
)


def _make_user_input(text: str) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        text=text,
        conversation_id="abc",
        context=MagicMock(),
        language="ja",
        agent_id="some_agent_id",
        device_id=None,
        satellite_id=None,
        extra_system_prompt=None,
    )


async def test_async_handle_message_success_path(monkeypatch):
    agent = JpSegmenterAgent(hass=MagicMock(), entry=MagicMock())
    user_input = _make_user_input("B'zのLOVE PHANTOMを流して")

    sentinel_result = MagicMock(name="ConversationResult")
    async_converse = AsyncMock(return_value=sentinel_result)
    monkeypatch.setattr(conversation, "async_converse", async_converse)

    result = await agent._async_handle_message(user_input, MagicMock())

    assert result is sentinel_result

    expected_text = _normalize_segmented_text(_tokenize_text(user_input.text))
    async_converse.assert_awaited_once()
    _, kwargs = async_converse.await_args
    assert kwargs["text"] == expected_text
    assert kwargs["agent_id"] == HOME_ASSISTANT_AGENT


async def test_async_handle_message_fallback_on_value_error(monkeypatch):
    agent = JpSegmenterAgent(hass=MagicMock(), entry=MagicMock())
    user_input = _make_user_input("こんにちは")

    async_converse = AsyncMock(side_effect=ValueError("boom"))
    monkeypatch.setattr(conversation, "async_converse", async_converse)

    result = await agent._async_handle_message(user_input, MagicMock())

    assert result.response.error_code == intent.IntentResponseErrorCode.UNKNOWN


async def test_async_prepare_defaults_to_hass_config_language(monkeypatch):
    hass = MagicMock()
    agent = JpSegmenterAgent(hass=hass, entry=MagicMock())

    async_prepare_agent = AsyncMock()
    monkeypatch.setattr(conversation, "async_prepare_agent", async_prepare_agent)

    await agent.async_prepare()

    async_prepare_agent.assert_awaited_once_with(
        hass, HOME_ASSISTANT_AGENT, hass.config.language
    )


async def test_async_prepare_uses_explicit_language(monkeypatch):
    hass = MagicMock()
    agent = JpSegmenterAgent(hass=hass, entry=MagicMock())

    async_prepare_agent = AsyncMock()
    monkeypatch.setattr(conversation, "async_prepare_agent", async_prepare_agent)

    await agent.async_prepare(language="en")

    async_prepare_agent.assert_awaited_once_with(hass, HOME_ASSISTANT_AGENT, "en")

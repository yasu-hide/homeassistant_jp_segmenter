"""Tests for async_setup_entry/async_unload_entry in __init__.py."""
from unittest.mock import AsyncMock, MagicMock

from custom_components.jp_segmenter_assistant import (
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
)


def test_platforms_is_conversation_only():
    assert PLATFORMS == ["conversation"]


async def test_async_setup_entry_forwards_to_platforms():
    hass = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)
    entry = MagicMock()

    result = await async_setup_entry(hass, entry)

    assert result is True
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry, PLATFORMS
    )


async def test_async_unload_entry_unloads_platforms():
    hass = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    entry = MagicMock()

    result = await async_unload_entry(hass, entry)

    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry, PLATFORMS
    )

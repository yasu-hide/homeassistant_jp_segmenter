"""The Japanese Segmenter Assistant integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# このドメイン名は manifest.json と一致させる必要があります
DOMAIN = "jp_segmenter_assistant"
PLATFORMS = ["conversation"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """統合をセットアップ（UIから追加された時に呼ばれる）"""
    _LOGGER.info("Initializing Japanese Segmenter Assistant")
    
    # conversation プラットフォーム（conversation.py）をロードする
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """統合をアンロード（削除された時に呼ばれる）"""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    if unload_ok:
        _LOGGER.info("Unloaded Japanese Segmenter Assistant")
        
    return unload_ok

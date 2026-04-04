"""Support for Japanese segmentation in the conversation pipeline."""
from __future__ import annotations

import logging
from tinysegmenter import TinySegmenter

from homeassistant.components import conversation
from homeassistant.components.conversation import HOME_ASSISTANT_AGENT
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
segmenter = TinySegmenter()

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> bool:
    """会話エージェントをセットアップ（UI経由で呼ばれる）"""
    async_add_entities([JpSegmenterAgent(hass, config_entry)])
    return True

class JpSegmenterAgent(conversation.ConversationEntity):
    """日本語分かち書きを行う会話エージェントラッパー"""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._attr_name = "Japanese Segmenter Assistant"
        self._attr_unique_id = entry.entry_id

    @property
    def supported_languages(self) -> list[str] | str:
        """日本語(ja)のみを対象とする"""
        return ["ja"]

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """入力を分かち書きして、デフォルトのHassilに渡す"""
        
        raw_text = user_input.text
        # TinySegmenterで分かち書きを実行
        # 例: "B'zのLOVE PHANTOMを流して" -> "B'z の LOVE PHANTOM を 流し て"
        segmented_text = " ".join(segmenter.segment(raw_text))

        _LOGGER.debug(
            "[%s] Original: '%s' -> Segmented: '%s'", 
            DOMAIN, raw_text, segmented_text
        )

        # Home Assistant 標準の会話エージェント (Hassil) を取得
        default_agent = conversation.async_get_agent(self.hass, HOME_ASSISTANT_AGENT)
        
        if default_agent is None:
            _LOGGER.error("Default conversation agent not found")
            return conversation.ConversationResult(
                response=intent.IntentResponse(language=user_input.language),
                conversation_id=user_input.conversation_id,
            )

        # テキストを分かち書き済みのものに差し替えて、標準エンジンに処理を委譲
        user_input.text = segmented_text
        
        return await default_agent.async_process(user_input)

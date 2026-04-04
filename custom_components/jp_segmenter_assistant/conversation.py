"""Support for Japanese segmentation in the conversation pipeline."""
from __future__ import annotations

import logging
import re
from tinysegmenter import TinySegmenter

from homeassistant.components import conversation
from homeassistant.components.conversation import HOME_ASSISTANT_AGENT
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import CONVERSATION_ENTITY_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)
segmenter = TinySegmenter()

_RE_HIRAGANA_ONLY = re.compile(r"^[\u3041-\u309F]+$")
_RE_KANJI_OR_KATAKANA_TAIL = re.compile(r".*[\u3400-\u9FFF\u30A0-\u30FF]$")
_JP_PARTICLES = {"の", "を", "に", "で", "が", "は", "へ", "と", "や", "か", "も"}


def _tokenize_text(text: str) -> list[str]:
    """Return segmented Japanese tokens across TinySegmenter variants."""
    tokenize = getattr(segmenter, "tokenize", None)
    if callable(tokenize):
        return tokenize(text)

    segment = getattr(segmenter, "segment", None)
    if callable(segment):
        return segment(text)

    raise AttributeError("TinySegmenter has no tokenize or segment method")


def _normalize_segmented_text(tokens: list[str]) -> str:
    """Normalize tokenized text for Hassil matching stability."""
    normalized_tokens = [token.strip() for token in tokens if token and token.strip()]

    # Merge contiguous hiragana chunks (e.g. "み", "ゆき" -> "みゆき").
    merged_hiragana: list[str] = []
    for token in normalized_tokens:
        if (
            merged_hiragana
            and _RE_HIRAGANA_ONLY.fullmatch(merged_hiragana[-1])
            and _RE_HIRAGANA_ONLY.fullmatch(token)
            and token not in _JP_PARTICLES
            and merged_hiragana[-1] not in _JP_PARTICLES
        ):
            merged_hiragana[-1] += token
            continue
        merged_hiragana.append(token)

    # Merge name-like kanji/katakana + hiragana chunks (e.g. "中島", "みゆき" -> "中島みゆき").
    merged_tokens: list[str] = []
    for token in merged_hiragana:
        if (
            merged_tokens
            and _RE_KANJI_OR_KATAKANA_TAIL.fullmatch(merged_tokens[-1])
            and _RE_HIRAGANA_ONLY.fullmatch(token)
            and len(token) >= 2
            and token not in _JP_PARTICLES
        ):
            merged_tokens[-1] += token
            continue
        merged_tokens.append(token)

    # Normalize whitespace.
    segmented = " ".join(merged_tokens)
    segmented = re.sub(r"\s+", " ", segmented).strip()

    # Re-join apostrophes inside latin words (e.g. B 'z -> B'z).
    segmented = re.sub(r"([A-Za-z0-9])\s+'\s*([A-Za-z0-9])", r"\1'\2", segmented)
    return segmented

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> bool:
    """会話エージェントをセットアップ（UI経由で呼ばれる）"""
    _LOGGER.warning("[%s][setup] Registering conversation entity: %s", DOMAIN, CONVERSATION_ENTITY_ID)
    async_add_entities([JpSegmenterAgent(hass, config_entry)])
    return True

class JpSegmenterAgent(conversation.ConversationEntity):
    """日本語分かち書きを行う会話エージェントラッパー"""

    _attr_supported_features = conversation.ConversationEntityFeature.CONTROL

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._attr_name = "Japanese Segmenter Assistant"
        self._attr_unique_id = DOMAIN
        self.entity_id = CONVERSATION_ENTITY_ID

    @property
    def supported_languages(self) -> list[str] | str:
        """日本語(ja)のみを対象とする"""
        return ["ja"]

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        _chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """入力を分かち書きして、デフォルトのHassilに渡す"""

        _LOGGER.warning(
            "[%s][step1] _async_handle_message called: agent_id=%s text=%s",
            DOMAIN,
            user_input.agent_id,
            user_input.text,
        )

        raw_text = user_input.text
        # TinySegmenterで分かち書きを実行
        # 例: "B'zのLOVE PHANTOMを流して" -> "B'z の LOVE PHANTOM を 流し て"
        segmented_text = _normalize_segmented_text(_tokenize_text(raw_text))

        _LOGGER.warning(
            "[%s][step2] tokenized text: original=%s segmented=%s",
            DOMAIN,
            raw_text,
            segmented_text,
        )

        _LOGGER.debug(
            "[%s] Original: '%s' -> Segmented: '%s'", 
            DOMAIN, raw_text, segmented_text
        )

        try:
            _LOGGER.warning(
                "[%s][step3] delegating to default agent: %s",
                DOMAIN,
                HOME_ASSISTANT_AGENT,
            )

            result = await conversation.async_converse(
                hass=self.hass,
                text=segmented_text,
                conversation_id=user_input.conversation_id,
                context=user_input.context,
                language=user_input.language,
                agent_id=HOME_ASSISTANT_AGENT,
                device_id=user_input.device_id,
                satellite_id=user_input.satellite_id,
                extra_system_prompt=user_input.extra_system_prompt,
            )

            _LOGGER.warning(
                "[%s][step4] default agent returned: response_type=%s",
                DOMAIN,
                result.response.response_type,
            )

            return result
        except ValueError:
            _LOGGER.exception("Default conversation agent not found")
            response = intent.IntentResponse(language=user_input.language)
            response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "Default conversation agent not found",
            )
            return conversation.ConversationResult(
                response=response,
                conversation_id=user_input.conversation_id,
            )

    async def async_prepare(self, language: str | None = None) -> None:
        """標準の会話エージェントの準備処理を委譲する"""
        await conversation.async_prepare_agent(
            self.hass,
            HOME_ASSISTANT_AGENT,
            language or self.hass.config.language,
        )

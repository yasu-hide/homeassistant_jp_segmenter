import logging
from tinysegmenter import TinySegmenter
from homeassistant.components import conversation
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

_LOGGER = logging.getLogger(__name__)
segmenter = TinySegmenter()

async def async_setup_entry(hass, entry):
    """Set up from a config entry."""
    # 会話エージェントとして登録
    conversation.async_set_agent(hass, entry, JpSegmenterAgent(hass))
    return True

class JpSegmenterAgent(conversation.AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    @property
    def supported_languages(self):
        return ["ja"]

    async def async_process(self, user_input: conversation.ConversationInput) -> conversation.ConversationResult:
        # 1. 元のテキストを取得
        raw_text = user_input.text
        
        # 2. 分かち書き実行
        # 助詞の前後をスペースで区切ることで、Hassilが「の」をスロットから除外しやすくなる
        segmented_text = " ".join(segmenter.segment(raw_text))
        
        _LOGGER.debug("Original: %s -> Segmented: %s", raw_text, segmented_text)

        # 3. デフォルトのエージェント (Hassil) を取得して処理を委譲
        default_agent = await conversation.async_get_agent(self.hass, "homeassistant")
        
        # 加工したテキストを渡す
        user_input.text = segmented_text
        return await default_agent.async_process(user_input)

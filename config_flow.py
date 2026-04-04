from homeassistant import config_entries
from .const import DOMAIN # DOMAIN = "jp_segmenter_assistant" を別ファイルにするか直書き

class JpSegmenterConfigFlow(config_entries.ConfigFlow, domain="jp_segmenter_assistant"):
    """Handle a config flow for Japanese Segmenter."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """最初のステップ。設定項目がなければ即作成。"""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.create_entry(title="Japanese Segmenter", data={})

        return self.async_show_form(step_id="user")

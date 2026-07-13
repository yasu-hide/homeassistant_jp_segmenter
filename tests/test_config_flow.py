"""Tests for JpSegmenterConfigFlow.async_step_user.

Uses the real hass fixture from pytest-homeassistant-custom-component plus
MockConfigEntry. The custom component is discovered from
custom_components/jp_segmenter_assistant via the autouse
enable_custom_integrations fixture in conftest.py.
"""
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.jp_segmenter_assistant.const import DOMAIN


async def test_user_flow_creates_entry(hass):
    # The conversation integration (a dependency pulled in via our
    # "conversation" platform) needs the core "homeassistant" component's
    # exposed_entities data, which the bare hass fixture doesn't set up.
    await async_setup_component(hass, "homeassistant", {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Japanese Segmenter"
    assert result2["data"] == {}


async def test_user_flow_aborts_when_already_configured(hass):
    await async_setup_component(hass, "homeassistant", {})

    MockConfigEntry(domain=DOMAIN).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"

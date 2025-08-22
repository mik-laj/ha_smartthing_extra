from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.smartthings.const import DOMAIN as ST_DOMAIN

from .const import DOMAIN


class SmartThingExtraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for SmartThings Extra."""

    async def async_step_user(self, user_input=None):
        # Single-instance guard
        for entry in self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # Check if SmartThings integration is loaded
        st_entries: list[ConfigEntry] = [
            e for e in self.hass.config_entries.async_entries(ST_DOMAIN)
            if e.state == config_entries.ConfigEntryState.LOADED
        ]
        if not st_entries:
            return self.async_abort(reason="no_smartthings")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=None)

        return self.async_create_entry(title="SmartThings Extra", data={})

    async def async_step_import(self, user_input):
        return await self.async_step_user(user_input)
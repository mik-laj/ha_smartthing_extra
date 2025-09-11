from __future__ import annotations

from datetime import datetime
from typing import Tuple, Optional
import logging

from homeassistant.components.smartthings.const import DOMAIN as ST_DOMAIN
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util


from pysmartthings import Attribute, Capability, Command, SmartThings

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_register_services(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    async def _resolve_st_ids(ha_device_id: str) -> Tuple[str, str]:
        """Return (st_device_id, st_config_entry_id) from an HA device_id."""
        dev_reg = dr.async_get(hass)
        device_entry = dev_reg.async_get(ha_device_id)
        if not device_entry:
            raise HomeAssistantError(f"No HA device found: {ha_device_id}")

        # SmartThings deviceId
        st_device_id: Optional[str] = None
        for domain, ident in device_entry.identifiers:
            if domain == ST_DOMAIN:
                st_device_id = ident
                break
        if not st_device_id:
            raise HomeAssistantError("Device is not linked to SmartThings.")

        # Find loaded SmartThings config entry
        st_entry_id: Optional[str] = None
        for entry_id in device_entry.config_entries:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry and entry.domain == ST_DOMAIN and entry.state == ConfigEntryState.LOADED:
                st_entry_id = entry.entry_id
                break
        if not st_entry_id:
            raise HomeAssistantError("No loaded SmartThings config entry for this device.")

        return st_device_id, st_entry_id

    async def handle_sync_time(call: ServiceCall) -> None:
        ha_device_id: str = call.data["device_id"]

        st_device_id, st_entry_id = await _resolve_st_ids(ha_device_id)
        entry: ConfigEntry | None = hass.config_entries.async_get_entry(st_entry_id)
        if not entry or not entry.runtime_data:
            raise HomeAssistantError("SmartThings entry not available or not loaded.")

        client = entry.runtime_data.client

        ts = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")

        _LOGGER.debug("Sync time -> ST device=%s, ts=%s", st_device_id, ts)

        kwargs = dict(
            device_id=st_device_id,
            capability=Capability.EXECUTE,
            command=Command.EXECUTE,
            argument=[
                "/configuration/vs/0",
                {"x.com.samsung.da.currentTime": ts},
            ]
        )
        result = await client.execute_device_command(**kwargs)
        _LOGGER.debug("Finished sync: response=%s", result)

    hass.services.async_register(DOMAIN, "sync_time", handle_sync_time)

    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, "sync_time"))

    async def handle_send_command(call: ServiceCall) -> None:
        ha_device_id: str = call.data["device_id"]

        st_device_id, st_entry_id = await _resolve_st_ids(ha_device_id)
        entry: ConfigEntry | None = hass.config_entries.async_get_entry(st_entry_id)
        if not entry or not entry.runtime_data:
            raise HomeAssistantError("SmartThings entry not available or not loaded.")

        client = entry.runtime_data.client

        capability_param = (call.data.get("capability", "EXECUTE")).upper()
        capability = getattr(Capability, capability_param, None)
        if not capability:
            raise HomeAssistantError(f"Unknown capability: {capability_param}")

        command_param = (call.data.get("command", "EXECUTE")).upper()
        command = getattr(Command, command_param, None)
        if not command:
            raise HomeAssistantError(f"Unknown command: {command_param}")
        component = (call.data.get("component", "main"))

        arguments = call.data.get("arguments", None)

        _LOGGER.debug(
            "Send command -> device=%s, capability=%s, command=%s, arguments=%s", 
            st_device_id, capability, command, arguments
        )

        kwargs = dict(
            device_id=st_device_id,
            capability=capability,
            command=command,
            component=component,
            argument=argumets
        )
        result = await client.execute_device_command(**kwargs)
        _LOGGER.debug("Finished command: response=%s", result)

    hass.services.async_register(DOMAIN, "send_command", handle_send_command)

    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, "send_command"))
    return True

async def async_unregister_services(hass: HomeAssistant) -> bool:
    try:
        hass.services.async_remove(DOMAIN, "sync_time")
    except Exception:
        pass
    try:
        hass.services.async_remove(DOMAIN, "send_command")
    except Exception:
        pass

    return True

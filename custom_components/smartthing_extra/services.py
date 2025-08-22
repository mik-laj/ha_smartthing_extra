from __future__ import annotations

from datetime import datetime
from typing import Tuple, Optional
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import device_registry as dr
from homeassistant.components.smartthings.const import DOMAIN as ST_DOMAIN
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from pysmartthings import Attribute, Capability, Command, SmartThings

_LOGGER = logging.getLogger(__name__)

async def async_register_services(hass: HomeAssistant) -> bool:

    async def _resolve_st_ids(ha_device_id: str) -> Tuple[str, str]:
        """Return (st_device_id, st_config_entry_id) from an HA device_id."""
        dev_reg = dr.async_get(hass)
        device_entry = dev_reg.async_get(ha_device_id)
        if not device_entry:
            raise ValueError(f"No HA device found: {ha_device_id}")

        # SmartThings deviceId
        st_device_id: Optional[str] = None
        for domain, ident in device_entry.identifiers:
            if domain == ST_DOMAIN:
                st_device_id = ident
                break
        if not st_device_id:
            raise ValueError("Device is not linked to SmartThings.")

        # Find loaded SmartThings config entry
        st_entry_id: Optional[str] = None
        for entry_id in device_entry.config_entries:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry and entry.domain == ST_DOMAIN and entry.state == ConfigEntryState.LOADED:
                st_entry_id = entry.entry_id
                break
        if not st_entry_id:
            raise ValueError("No loaded SmartThings config entry for this device.")

        return st_device_id, st_entry_id

    async def handle_sync_time(call: ServiceCall) -> None:
        ha_device_id: str = call.data["device_id"]

        st_device_id, st_entry_id = await _resolve_st_ids(ha_device_id)
        entry: ConfigEntry | None = hass.config_entries.async_get_entry(st_entry_id)
        if not entry or not entry.runtime_data:
            raise ValueError("SmartThings entry not available or not loaded.")

        client = entry.runtime_data.client

        ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        _LOGGER.info("Sync time -> ST device=%s, ts=%s", st_device_id, ts)

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
        _LOGGER.info("Finished sync: response=%s", result)

    hass.services.async_register(DOMAIN, "sync_time", handle_sync_time)
    return True

from __future__ import annotations


import logging
from datetime import datetime
from typing import Optional, Tuple

from homeassistant.components.smartthings.const import DOMAIN as ST_DOMAIN
from homeassistant.config_entries import ConfigEntry, ConfigEntryState, SOURCE_IMPORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .services import async_register_services, async_unregister_services

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """YAML setup hook: migrate to UI if somebody added 'smartthing_extra:' in YAML."""
    if DOMAIN in config:
        # Create a config entry from YAML for backward compatibility.
        if not any(e.domain == DOMAIN for e in hass.config_entries.async_entries(DOMAIN)):
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data={}
                )
            )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartThings Extra from a config entry."""

    await async_register_services(hass, entry)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SmartThings Extra config entry (enables UI Reload)."""
    
    await async_unregister_services(hass)

    return True
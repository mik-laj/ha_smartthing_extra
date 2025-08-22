from __future__ import annotations

from homeassistant.helpers.typing import ConfigType
from .services import async_register_services

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:

    await async_register_services(hass)

    return True

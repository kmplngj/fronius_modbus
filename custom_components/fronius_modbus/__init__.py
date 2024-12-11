"""The Detailed Hello World Push integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from .const import (
    DOMAIN,
    CONF_MODBUS_ADDRESS,
    CONF_METER_MODBUS_ADDRESS,
    CONF_STORAGE_MODBUS_ADDRESS,
)

from . import hub

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS = [Platform.NUMBER, Platform.SELECT, Platform.SENSOR]

type HubConfigEntry = ConfigEntry[hub.Hub]

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry) -> bool:
    """Set up Hello World from a config entry."""

    name = entry.data[CONF_NAME]
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    address = entry.data.get(CONF_MODBUS_ADDRESS, 1)
    meter_addresses = [entry.data.get(CONF_METER_MODBUS_ADDRESS, 1)]
    storage_addresses = [entry.data.get(CONF_STORAGE_MODBUS_ADDRESS, 1)]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.
    entry.runtime_data = hub.Hub(hass = hass, name = name, host = host, port = port, address = address, meter_addresses=meter_addresses, storage_addresses=storage_addresses, scan_interval = scan_interval)
    
    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok

async def reload_service_handler(service: ServiceCall) -> None:
    """Remove all user-defined groups and load new ones from config."""
    conf = None
    with contextlib.suppress(HomeAssistantError):
        conf = await async_integration_yaml_config(hass, DOMAIN)
    if conf is None:
        return
    await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)
    _async_setup_shared_data(hass)
    await _async_process_config(hass, conf)    


from homeassistant.components.switch import SwitchEntity
from . import _LOGGER, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api = entry_data.get("api")
    light_devices = entry_data.get("devices", {}).get("LIGHT", [])
    fan_devices = entry_data.get("devices", {}).get("WIND", [])

    if api:
        entities = []

        if light_devices:
            entities.extend(
                [
                    MarsHydroSwitch(api, entry.entry_id, light_data, device_type="LIGHT")
                    for light_data in light_devices
                ]
            )
        else:
            _LOGGER.debug("No Mars Hydro light found; light switch not created.")

        if fan_devices:
            _LOGGER.debug("Fan switch not created; fan entity handles power control.")

        if entities:
            async_add_entities(entities, update_before_add=True)


class MarsHydroSwitch(SwitchEntity):
    """Representation of a Mars Hydro switch."""

    def __init__(self, api, entry_id, device_data, device_type):
        self._api = api
        self._device_id = device_data.get("id")
        self._device_name = device_data.get("deviceName")
        self._state = None
        self._available = True
        self._entry_id = entry_id
        self._device_type = device_type  # LIGHT or WIND
        self._apply_device_data(device_data)

    @property
    def name(self):
        """Return the name of the switch, dynamically including the device name and ID."""
        return "Switch"

    @property
    def is_on(self):
        """Return True if the switch is on."""
        return self._state

    @property
    def available(self):
        """Return True if the switch is available."""
        return self._available

    @property
    def unique_id(self):
        """Return a unique ID for the switch."""
        return (
            f"{self._entry_id}_switch_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_switch_{self._device_type}"
        )

    @property
    def device_info(self):
        """Return device information for linking with the device registry."""
        if not self._device_id or not self._device_name:
            return None

        return {
            "identifiers": {
                (DOMAIN, self._device_id)
            },  # Match the registered device ID
            "name": self._device_name,  # Use the dynamic deviceName
            "manufacturer": "Mars Hydro",
            "model": f"Mars Hydro {self._device_type.capitalize()}",
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        try:
            if not self._device_id:
                _LOGGER.error("Device ID is not available; cannot turn on.")
                return

            response = await self._api.safe_api_call(
                self._api.toggle_switch, False, self._device_id
            )
            if response.get("code") == "000":
                self._state = True
                _LOGGER.info(f"Switch '{self._device_name}' turned on successfully.")
            else:
                _LOGGER.error(f"Error turning on switch: {response.get('msg')}")
        except Exception as e:
            _LOGGER.error(f"Error in async_turn_on: {e}")
            self._available = False

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        try:
            if not self._device_id:
                _LOGGER.error("Device ID is not available; cannot turn off.")
                return

            response = await self._api.safe_api_call(
                self._api.toggle_switch, True, self._device_id
            )
            if response.get("code") == "000":
                self._state = False
                _LOGGER.info(f"Switch '{self._device_name}' turned off successfully.")
            else:
                _LOGGER.error(f"Error turning off switch: {response.get('msg')}")
        except Exception as e:
            _LOGGER.error(f"Error in async_turn_off: {e}")
            self._available = False

    async def async_update(self):
        """Update the state of the switch."""
        try:
            # Choose the correct API endpoint based on device type
            device_data = await self._api.safe_api_call(
                self._api.get_lightdata
                if self._device_type == "LIGHT"
                else self._api.get_fandata,
                self._device_id,
            )
            if device_data:
                self._apply_device_data(device_data)
            else:
                _LOGGER.debug(
                    f"Could not update switch state for {self._device_type}."
                )
                self._available = False
        except Exception as e:
            _LOGGER.error(f"Error updating switch state for {self._device_type}: {e}")
            self._available = False

    def _apply_device_data(self, device_data):
        """Apply API data to the switch entity."""
        self._device_id = device_data.get("id")
        self._device_name = device_data.get("deviceName")
        self._state = not device_data.get("isClose", False)
        self._available = True

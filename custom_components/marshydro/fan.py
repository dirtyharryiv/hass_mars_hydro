from homeassistant.components.fan import FanEntity, FanEntityFeature
from . import _LOGGER, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Mars Hydro fan entity."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api = entry_data.get("api")
    fan_devices = entry_data.get("devices", {}).get("WIND", [])

    if api and fan_devices:
        async_add_entities(
            [
                MarsHydroFanEntity(api, entry.entry_id, fan_data)
                for fan_data in fan_devices
            ],
            update_before_add=True,
        )
        _LOGGER.info("Mars Hydro fan entity added successfully.")
    elif api:
        _LOGGER.debug("No Mars Hydro fan found; fan entity not created.")
    else:
        _LOGGER.error("API instance not found. Cannot set up fan entity.")


class MarsHydroFanEntity(FanEntity):
    """Representation of a Mars Hydro fan."""

    def __init__(self, api, entry_id, fan_data):
        self._api = api
        self._device_id = fan_data.get("id")
        self._device_name = fan_data.get("deviceName")
        self._speed_percentage = None
        self._state = None
        self._available = True
        self._entry_id = entry_id
        self._enable_turn_on_off_backwards_compatibility = False
        self._apply_fan_data(fan_data)

    @property
    def name(self):
        """Return the name of the fan."""
        if self._device_name:
            return f"{self._device_name} Fan"
        return "Mars Hydro Fan"

    @property
    def available(self):
        """Return True if the fan is available."""
        return self._available

    @property
    def percentage(self):
        """Return the current speed percentage of the fan."""
        return self._speed_percentage

    @property
    def is_on(self):
        """Return True if the fan is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the fan."""
        return (
            f"{self._entry_id}_fan_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan"
        )

    @property
    def device_info(self):
        """Return device information for linking with the device registry."""
        if not self._device_id or not self._device_name:
            _LOGGER.debug("Device info incomplete for fan entity.")
            return None

        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Mars Hydro",
            "model": "Mars Hydro Fan",
        }

    @property
    def supported_features(self):
        """Return supported features of the fan."""
        features = FanEntityFeature.SET_SPEED

        if hasattr(FanEntityFeature, "TURN_ON"):
            features |= FanEntityFeature.TURN_ON
        if hasattr(FanEntityFeature, "TURN_OFF"):
            features |= FanEntityFeature.TURN_OFF

        return features

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs):
        """Turn the fan on."""
        try:
            if not await self._async_ensure_device_id():
                _LOGGER.error("Fan device ID is not available; cannot turn on.")
                return

            response = await self._api.safe_api_call(
                self._api.toggle_switch, False, self._device_id
            )
            if response.get("code") == "000":
                self._state = True
                self._available = True

                if percentage is not None:
                    await self.async_set_percentage(percentage)
                _LOGGER.info("Fan '%s' turned on successfully.", self._device_name)
            else:
                _LOGGER.error("Error turning on fan: %s", response.get("msg"))
        except Exception as e:
            self._available = False
            _LOGGER.error("Error in async_turn_on: %s", e)

    async def async_turn_off(self, **kwargs):
        """Turn the fan off."""
        try:
            if not await self._async_ensure_device_id():
                _LOGGER.error("Fan device ID is not available; cannot turn off.")
                return

            response = await self._api.safe_api_call(
                self._api.toggle_switch, True, self._device_id
            )
            if response.get("code") == "000":
                self._state = False
                self._available = True
                _LOGGER.info("Fan '%s' turned off successfully.", self._device_name)
            else:
                _LOGGER.error("Error turning off fan: %s", response.get("msg"))
        except Exception as e:
            self._available = False
            _LOGGER.error("Error in async_turn_off: %s", e)

    async def async_set_percentage(self, percentage):
        """Set the fan speed percentage."""
        if percentage <= 0:
            await self.async_turn_off()
            return

        if percentage < 25:
            _LOGGER.warning("Fan speed percentage below 25% is not allowed.")
            percentage = 25

        if percentage > 100:
            _LOGGER.warning("Fan speed percentage above 100% is not allowed.")
            percentage = 100

        try:
            if not await self._async_ensure_device_id():
                _LOGGER.error("Fan device ID is not available; cannot set speed.")
                return

            response = await self._api.safe_api_call(
                self._api.set_fanspeed, round(percentage), self._device_id
            )
            if response.get("code") == "000":
                self._speed_percentage = percentage
                self._available = True
                _LOGGER.info(f"Fan speed set to {percentage}% successfully.")
            else:
                _LOGGER.error(f"Error setting fan speed: {response.get('msg')}")
        except Exception as e:
            _LOGGER.error(f"Error in async_set_percentage: {e}")
            self._available = False

    async def async_update(self):
        """Update the fan state."""
        try:
            fan_data = await self._api.safe_api_call(
                self._api.get_fandata, self._device_id
            )
            if fan_data:
                self._apply_fan_data(fan_data)
            else:
                self._available = False
                self._state = None
                _LOGGER.debug("Could not update fan state.")
        except Exception as e:
            self._available = False
            _LOGGER.error(f"Error updating fan state: {e}")

    async def _async_ensure_device_id(self):
        """Ensure the fan device ID is available before sending commands."""
        if self._device_id:
            return True

        await self.async_update()
        return self._device_id is not None

    def _apply_fan_data(self, fan_data):
        """Apply API data to the fan entity."""
        self._device_id = fan_data.get("id")
        self._device_name = fan_data.get("deviceName")
        self._state = not fan_data.get("isClose", False)
        raw_speed = fan_data.get("deviceLightRate", 25)

        try:
            self._speed_percentage = min(max(int(raw_speed), 25), 100)
            self._available = True
        except (TypeError, ValueError):
            _LOGGER.warning(
                f"Invalid speed data for fan {self._device_name}: {raw_speed}"
            )
            self._speed_percentage = None
            self._available = False

from homeassistant.components.number import NumberEntity

from . import _LOGGER, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Mars Hydro number entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api = entry_data.get("api")
    fan_data = entry_data.get("devices", {}).get("WIND")

    if api and fan_data:
        async_add_entities(
            [MarsHydroFanStrengthNumber(api, entry.entry_id)],
            update_before_add=True,
        )
    elif api:
        _LOGGER.debug("No Mars Hydro fan found; fan strength number not created.")


class MarsHydroFanStrengthNumber(NumberEntity):
    """Representation of a settable Mars Hydro fan strength percentage."""

    def __init__(self, api, entry_id):
        self._api = api
        self._device_id = None
        self._device_name = None
        self._strength = None
        self._available = True
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the number entity."""
        if self._device_name and self._device_id:
            return f"{self._device_name} Strength ({self._device_id})"
        elif self._device_name:
            return f"{self._device_name} Strength"
        return "Mars Hydro Fan Strength"

    @property
    def unique_id(self):
        """Return a unique ID for the number entity."""
        return (
            f"{self._entry_id}_fan_strength_number_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_strength_number"
        )

    @property
    def device_info(self):
        """Return device information for linking with the fan device registry."""
        if not self._device_id or not self._device_name:
            return None

        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Mars Hydro",
            "model": "Mars Hydro Fan",
        }

    @property
    def available(self):
        """Return True if the number entity is available."""
        return self._available

    @property
    def native_value(self):
        """Return the current fan strength percentage."""
        return self._strength

    @property
    def native_min_value(self):
        """Return the minimum fan strength."""
        return 25

    @property
    def native_max_value(self):
        """Return the maximum fan strength."""
        return 100

    @property
    def native_step(self):
        """Return the fan strength step size."""
        return 1

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def mode(self):
        """Return the number entity UI mode."""
        return "slider"

    async def async_set_native_value(self, value):
        """Set the fan strength percentage."""
        try:
            strength = min(max(round(value), 25), 100)

            if not self._device_id:
                await self.async_update()

            if not self._device_id:
                _LOGGER.error("Fan device ID is not available; cannot set strength.")
                self._available = False
                return

            response = await self._api.safe_api_call(
                self._api.set_fanspeed,
                strength,
                self._device_id,
            )
            if response.get("code") == "000":
                self._strength = strength
                self._available = True
                _LOGGER.info("Fan strength set to %s%% successfully.", strength)
            else:
                _LOGGER.error("Error setting fan strength: %s", response.get("msg"))
        except Exception as e:
            self._available = False
            _LOGGER.error("Error setting fan strength: %s", e)

    async def async_update(self):
        """Update the current fan strength percentage."""
        try:
            fan_data = await self._api.safe_api_call(self._api.get_fandata)
            if fan_data:
                self._device_id = fan_data["id"]
                self._device_name = fan_data["deviceName"]
                raw_strength = fan_data.get("deviceLightRate")

                try:
                    self._strength = min(max(int(raw_strength), 25), 100)
                    self._available = True
                except (TypeError, ValueError):
                    _LOGGER.warning("Invalid fan strength data: %s", raw_strength)
                    self._strength = None
                    self._available = False
            else:
                self._available = False
                self._strength = None
                _LOGGER.debug("Could not update fan strength number.")
        except Exception as e:
            self._available = False
            _LOGGER.error("Error updating fan strength number: %s", e)

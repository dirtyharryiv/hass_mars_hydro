from homeassistant.components.sensor import SensorEntity
from . import _LOGGER, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Mars Hydro sensors."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api = entry_data.get("api")
    devices = entry_data.get("devices", {})

    if api:
        entities = []

        if devices.get("LIGHT"):
            entities.append(MarsHydroBrightnessSensor(api, entry.entry_id))
        else:
            _LOGGER.debug("No Mars Hydro light found; brightness sensor not created.")

        if devices.get("WIND"):
            temperature_unit = entry.data.get("temperature_unit", "F")
            temperature_sensor = (
                MarsHydroFanTemperatureCelsiusSensor(api, entry.entry_id)
                if temperature_unit == "C"
                else MarsHydroFanTemperatureSensor(api, entry.entry_id)
            )
            entities.extend(
                [
                    temperature_sensor,
                    MarsHydroFanHumiditySensor(api, entry.entry_id),
                    MarsHydroFanSpeedSensor(api, entry.entry_id),
                ]
            )
        else:
            _LOGGER.debug("No Mars Hydro fan found; fan sensors not created.")

        if entities:
            async_add_entities(entities, update_before_add=True)


class MarsHydroBrightnessSensor(SensorEntity):
    """Representation of the Mars Hydro brightness sensor."""

    def __init__(self, api, entry_id):
        self._api = api
        self._device_id = None
        self._device_name = None
        self._brightness = None
        self._available = True
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._device_name and self._device_id:
            return f"{self._device_name} Brightness Sensor ({self._device_id})"
        elif self._device_name:
            return f"{self._device_name} Brightness Sensor"
        return "Mars Hydro Brightness Sensor"

    @property
    def native_value(self):
        """Return the brightness value."""
        return self._brightness

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._available

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return (
            f"{self._entry_id}_brightness_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_brightness_sensor"
        )

    @property
    def device_info(self):
        """Return device information for linking with the device registry."""
        if not self._device_id or not self._device_name:
            return None

        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Mars Hydro",
            "model": "Mars Hydro Light",
        }

    async def async_update(self):
        """Update the sensor state."""
        try:
            light_data = await self._api.safe_api_call(self._api.get_lightdata)
            if light_data:
                self._device_id = light_data["id"]
                self._device_name = light_data["deviceName"]
                self._brightness = light_data["deviceLightRate"]
                self._available = True
            else:
                self._available = False
                _LOGGER.debug("Could not update brightness sensor.")
        except Exception as e:
            self._available = False
            _LOGGER.error(f"Error updating brightness sensor: {e}")


class MarsHydroFanTemperatureSensor(SensorEntity):
    """Representation of the Mars Hydro fan temperature sensor."""

    def __init__(self, api, entry_id):
        self._api = api
        self._device_id = None
        self._device_name = None
        self._temperature = None
        self._available = True
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the fan temperature sensor."""
        if self._device_name and self._device_id:
            return f"{self._device_name} Temperature Sensor ({self._device_id})"
        elif self._device_name:
            return f"{self._device_name} Temperature Sensor"
        return "Mars Hydro Fan Temperature Sensor"

    @property
    def native_value(self):
        """Return the fan's temperature."""
        return self._temperature

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._available

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "°F"

    @property
    def unique_id(self):
        """Return a unique ID for the fan temperature sensor."""
        return (
            f"{self._entry_id}_fan_temperature_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_temperature_sensor"
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

    async def async_update(self):
        """Update the fan temperature sensor state."""
        try:
            fan_data = await self._api.safe_api_call(self._api.get_fandata)
            if fan_data:
                self._device_id = fan_data["id"]
                self._device_name = fan_data["deviceName"]
                raw_temperature = fan_data["temperature"]

                try:
                    self._temperature = float(raw_temperature)
                    self._available = True
                except (TypeError, ValueError):
                    _LOGGER.warning("Invalid temperature data: %s", raw_temperature)
                    self._temperature = None
                    self._available = False
            else:
                self._available = False
                self._temperature = None
                _LOGGER.debug("Could not update fan temperature sensor.")
        except Exception as e:
            self._available = False
            _LOGGER.error(f"Error updating fan temperature sensor: {e}")


class MarsHydroFanTemperatureCelsiusSensor(SensorEntity):
    """Representation of the Mars Hydro fan temperature sensor in Celsius."""

    def __init__(self, api, entry_id):
        self._api = api
        self._device_id = None
        self._device_name = None
        self._temperature_celsius = None
        self._available = True
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the fan temperature sensor (Celsius)."""
        if self._device_name and self._device_id:
            return (
                f"{self._device_name} Temperature Sensor (Celsius) ({self._device_id})"
            )
        elif self._device_name:
            return f"{self._device_name} Temperature Sensor (Celsius)"
        return "Mars Hydro Fan Temperature Sensor (Celsius)"

    @property
    def native_value(self):
        """Return the fan's temperature in Celsius."""
        return self._temperature_celsius

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._available

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "°C"

    @property
    def unique_id(self):
        """Return a unique ID for the fan temperature sensor in Celsius."""
        return (
            f"{self._entry_id}_fan_temperature_celsius_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_temperature_celsius_sensor"
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

    async def async_update(self):
        """Update the fan temperature in Celsius."""
        try:
            fan_data = await self._api.safe_api_call(self._api.get_fandata)
            if fan_data:
                self._device_id = fan_data["id"]
                self._device_name = fan_data["deviceName"]
                raw_temperature = fan_data["temperature"]

                try:
                    self._temperature_celsius = round(
                        (float(raw_temperature) - 32) * 5 / 9, 1
                    )
                    self._available = True
                except (TypeError, ValueError):
                    _LOGGER.warning("Invalid temperature data: %s", raw_temperature)
                    self._temperature_celsius = None
                    self._available = False
            else:
                self._available = False
                self._temperature_celsius = None
                _LOGGER.debug("Could not update fan temperature (Celsius) sensor.")
        except Exception as e:
            self._available = False
            _LOGGER.error(f"Error updating fan temperature (Celsius) sensor: {e}")


class MarsHydroFanHumiditySensor(SensorEntity):
    """Representation of the Mars Hydro fan humidity sensor."""

    def __init__(self, api, entry_id):
        self._api = api
        self._device_id = None
        self._device_name = None
        self._humidity = None
        self._available = True
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the fan humidity sensor."""
        if self._device_name and self._device_id:
            return f"{self._device_name} Humidity Sensor ({self._device_id})"
        elif self._device_name:
            return f"{self._device_name} Humidity Sensor"
        return "Mars Hydro Fan Humidity Sensor"

    @property
    def native_value(self):
        """Return the fan's humidity."""
        return self._humidity

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._available

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def unique_id(self):
        """Return a unique ID for the fan humidity sensor."""
        return (
            f"{self._entry_id}_fan_humidity_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_humidity_sensor"
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

    async def async_update(self):
        """Update the fan humidity sensor state."""
        try:
            fan_data = await self._api.safe_api_call(self._api.get_fandata)
            if fan_data:
                self._device_id = fan_data["id"]
                self._device_name = fan_data["deviceName"]
                raw_humidity = fan_data["humidity"]

                try:
                    self._humidity = float(raw_humidity)
                    self._available = True
                except (TypeError, ValueError):
                    _LOGGER.warning("Invalid humidity data: %s", raw_humidity)
                    self._humidity = None
                    self._available = False
            else:
                self._available = False
                self._humidity = None
                _LOGGER.debug("Could not update fan humidity sensor.")
        except Exception as e:
            self._available = False
            _LOGGER.error(f"Error updating fan humidity sensor: {e}")


class MarsHydroFanSpeedSensor(SensorEntity):
    """Representation of the Mars Hydro fan speed sensor."""

    def __init__(self, api, entry_id):
        self._api = api
        self._device_id = None
        self._device_name = None
        self._speed = None
        self._available = True
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the fan speed sensor."""
        if self._device_name and self._device_id:
            return f"{self._device_name} Speed Sensor ({self._device_id})"
        elif self._device_name:
            return f"{self._device_name} Speed Sensor"
        return "Mars Hydro Fan Speed Sensor"

    @property
    def native_value(self):
        """Return the fan's speed."""
        return self._speed

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._available

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "RPM"

    @property
    def unique_id(self):
        """Return a unique ID for the fan speed sensor."""
        return (
            f"{self._entry_id}_fan_speed_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_speed_sensor"
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

    async def async_update(self):
        """Update the fan speed sensor state."""
        try:
            fan_data = await self._api.safe_api_call(self._api.get_fandata)
            if fan_data:
                self._device_id = fan_data["id"]
                self._device_name = fan_data["deviceName"]
                raw_speed = fan_data.get("speed")

                try:
                    self._speed = int(raw_speed)
                    self._available = True
                except (TypeError, ValueError):
                    _LOGGER.warning("Invalid speed data: %s", raw_speed)
                    self._speed = None
                    self._available = False
            else:
                self._available = False
                self._speed = None
                _LOGGER.debug("Could not update fan speed sensor.")
        except Exception as e:
            self._available = False
            _LOGGER.error(f"Error updating fan speed sensor: {e}")

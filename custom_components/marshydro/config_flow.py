from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)
import voluptuous as vol
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

OPTIONS_FLOW_BASE = getattr(
    config_entries, "OptionsFlowWithReload", config_entries.OptionsFlow
)

TEMPERATURE_UNIT_OPTIONS = [
    SelectOptionDict(value="C", label="C°"),
    SelectOptionDict(value="F", label="F°"),
]


class MarsHydroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mars Hydro."""

    VERSION = 1

    def __init__(self):
        self._email = None
        self._password = None
        self._temperature_unit = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._email = user_input["email"]
            self._password = user_input["password"]
            self._temperature_unit = user_input["temperature_unit"]

            if not self._validate_email(self._email):
                errors["email"] = "invalid_email"
            else:
                login_success = await self._test_login(self._email, self._password)
                if login_success:
                    return self.async_create_entry(
                        title="Mars Hydro",
                        data={
                            "email": self._email,
                            "password": self._password,
                            "temperature_unit": self._temperature_unit,
                        },
                    )
                else:
                    errors["base"] = "cannot_connect"

        # Schema für das Eingabeformular
        data_schema = vol.Schema(
            {
                vol.Required("email"): str,
                vol.Required("password"): str,
                vol.Required("temperature_unit", default="C"): SelectSelector(
                    SelectSelectorConfig(options=TEMPERATURE_UNIT_OPTIONS)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _test_login(self, email: str, password: str) -> bool:
        """Test the API login."""
        from .api import MarsHydroAPI

        api = MarsHydroAPI(email, password)
        try:
            await api.login()
            return True
        except Exception as e:
            _LOGGER.error("Error testing login credentials: %s", e)
            return False

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate an email address."""
        import re

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(email_regex, email) is not None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow."""
        return MarsHydroOptionsFlow()


class MarsHydroOptionsFlow(OPTIONS_FLOW_BASE):
    """Handle an options flow for Mars Hydro."""

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Handle the options flow."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required(
                    "temperature_unit",
                    default=self.config_entry.options.get(
                        "temperature_unit",
                        self.config_entry.data.get("temperature_unit", "C"),
                    ),
                ): SelectSelector(
                    SelectSelectorConfig(options=TEMPERATURE_UNIT_OPTIONS)
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )

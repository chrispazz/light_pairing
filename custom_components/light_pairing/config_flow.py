import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN

@callback
def configured_instances(hass):
    """Return a set of configured instances."""
    return set(entry.title for entry in hass.config_entries.async_entries(DOMAIN))

class LightPairingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Light Pairing."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        # Get available entities
        entities_switch = [e.entity_id for e in self.hass.states.async_all() if e.domain in ["switch", "light"]]
        entities_light = [e.entity_id for e in self.hass.states.async_all() if e.domain == "light"]

        schema = vol.Schema({
            vol.Required("physical_light"): vol.In(entities_switch),
            vol.Required("smart_light"): vol.In(entities_light),
            vol.Required("name"): str
        })

        return self.async_show_form(step_id="user", data_schema=schema)

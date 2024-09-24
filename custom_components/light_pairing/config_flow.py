from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers.selector import selector
from .const import DOMAIN

class LightPairConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gestisce il flusso di configurazione iniziale."""
        if user_input is not None:
            # Gestisce i dati inseriti dall'utente
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("physical_light"): selector({"entity": {"domain": ["switch", "light"]}}),
                vol.Required("smart_light"): selector({"entity": {"domain": "light"}}),
                vol.Required("name"): str,
                vol.Optional("brightness_on_switch", default=80): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional("turn_off_physical", default=True): bool
            })
        )

    async def async_step_reconfigure(self, user_input=None):
        """Gestisce il flusso di riconfigurazione."""
        if user_input is not None:
            # Aggiorna la configurazione esistente con i nuovi valori
            return self.async_create_entry(title=user_input["name"], data=user_input)

        current_config = self._get_current_config()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required("physical_light", default=current_config.get("physical_light")): selector({"entity": {"domain": ["switch", "light"]}}),
                vol.Required("smart_light", default=current_config.get("smart_light")): selector({"entity": {"domain": "light"}}),
                vol.Required("name", default=current_config.get("name")): str,
                vol.Optional("brightness_on_switch", default=current_config.get("brightness_on_switch", 100)): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional("turn_off_physical", default=current_config.get("turn_off_physical", True)): bool
            })
        )

    def _get_current_config(self):
        """Ottiene la configurazione attuale per l'entità da modificare."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return entry.data if entry else {}

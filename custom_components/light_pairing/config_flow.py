import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

# Parametri di configurazione
CONF_BRIGHTNESS_ON_SWITCH = "brightness_on_switch"
CONF_TURN_OFF_PHYSICAL = "turn_off_physical"
CONF_PHYSICAL_LIGHT = "physical_light"
CONF_SMART_LIGHT = "smart_light"

class LightPairingConfigFlow(config_entries.ConfigFlow, domain="light_pairing"):
    """Gestisce il flusso di configurazione per il pairing delle luci."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gestisce lo step iniziale."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required(CONF_PHYSICAL_LIGHT): selector({
                "entity": {"domain": "light"}
            }),
            vol.Required(CONF_SMART_LIGHT): selector({
                "entity": {"domain": "light"}
            }),
            vol.Optional(CONF_BRIGHTNESS_ON_SWITCH, default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            vol.Optional(CONF_TURN_OFF_PHYSICAL, default=False): bool
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Ritorna il flusso di opzioni per la riconfigurazione."""
        return LightPairingOptionsFlowHandler(config_entry)


class LightPairingOptionsFlowHandler(config_entries.OptionsFlow):
    """Gestisce il flusso di opzioni per riconfigurare i parametri."""

    def __init__(self, config_entry):
        """Inizializza il flusso di opzioni."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Inizia il flusso di riconfigurazione."""
        return await self.async_step_reconfigure()

    async def async_step_reconfigure(self, user_input=None):
        """Gestisce la riconfigurazione dei parametri."""
        if user_input is not None:
            # Aggiorna i parametri nel config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options={**self.config_entry.options, **user_input}
            )
            return self.async_create_entry(title="", data=None)

        # Preleva i parametri attuali dalle opzioni o dai dati di configurazione iniziale
        current_brightness_on_switch = self.config_entry.options.get(
            CONF_BRIGHTNESS_ON_SWITCH, 
            self.config_entry.data.get(CONF_BRIGHTNESS_ON_SWITCH, 100)
        )
        current_turn_off_physical = self.config_entry.options.get(
            CONF_TURN_OFF_PHYSICAL, 
            self.config_entry.data.get(CONF_TURN_OFF_PHYSICAL, False)
        )

        # Schema per riconfigurare i due parametri
        schema = vol.Schema({
            vol.Optional(CONF_BRIGHTNESS_ON_SWITCH, default=current_brightness_on_switch): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            vol.Optional(CONF_TURN_OFF_PHYSICAL, default=current_turn_off_physical): bool
        })

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema
        )

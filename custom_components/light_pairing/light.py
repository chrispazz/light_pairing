from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_XY_COLOR,
    ATTR_COLOR_MODE,
    ATTR_SUPPORTED_COLOR_MODES,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_COLOR,
    LightEntity,
)
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import callback
import asyncio

# Parametri di configurazione
CONF_BRIGHTNESS_ON_SWITCH = "brightness_on_switch"
CONF_TURN_OFF_PHYSICAL = "turn_off_physical"
CONF_PHYSICAL_LIGHT = "physical_light"
CONF_SMART_LIGHT = "smart_light"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Imposta l'entità della luce virtuale in base a una configurazione."""
    physical_light = config_entry.data[CONF_PHYSICAL_LIGHT]
    smart_light = config_entry.data[CONF_SMART_LIGHT]
    name = config_entry.data["name"]

    # Legge i parametri dalle opzioni o dai dati di configurazione
    brightness_on_switch = config_entry.options.get(CONF_BRIGHTNESS_ON_SWITCH, config_entry.data.get(CONF_BRIGHTNESS_ON_SWITCH, 100))
    turn_off_physical = config_entry.options.get(CONF_TURN_OFF_PHYSICAL, config_entry.data.get(CONF_TURN_OFF_PHYSICAL, False))

    async_add_entities([LightPairEntity(
        hass, 
        physical_light, 
        smart_light, 
        name, 
        config_entry.entry_id, 
        brightness_on_switch, 
        turn_off_physical,
        config_entry  # Passa il config_entry per aggiornamenti futuri
    )])

class LightPairEntity(LightEntity):
    """Rappresenta una luce virtuale composta da una luce fisica e una smart."""

    def __init__(self, hass, physical_light, smart_light, name, entry_id, brightness_on_switch, turn_off_physical, config_entry):
        """Inizializza la luce virtuale."""
        self.hass = hass
        self._physical_light = physical_light
        self._smart_light = smart_light
        self._name = name
        self._entry_id = entry_id
        self._brightness_on_switch = brightness_on_switch
        self._turn_off_physical = turn_off_physical
        self._config_entry = config_entry  # Mantiene un riferimento al config_entry per futuri aggiornamenti
        self._state = None
        self._brightness = None
        self._xy_color = None
        self._color_temp = None
        self._color_mode = None
        self._supported_color_modes = []
        self._supported_features = SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP | SUPPORT_COLOR
        self._waiting_for_smart_light = False  # Flag per tracciare se stiamo aspettando la luce smart

        self.hass.bus.async_listen("state_changed", self._state_changed_listener)

    def _update_parameters_from_config(self):
        """Aggiorna i parametri leggendo le opzioni dal config entry."""
        self._brightness_on_switch = self._config_entry.options.get(CONF_BRIGHTNESS_ON_SWITCH, self._config_entry.data.get(CONF_BRIGHTNESS_ON_SWITCH, 100))
        self._turn_off_physical = self._config_entry.options.get(CONF_TURN_OFF_PHYSICAL, self._config_entry.data.get(CONF_TURN_OFF_PHYSICAL, False))

    @callback
    def _state_changed_listener(self, event):
        """Gestisce i cambiamenti di stato delle luci fisiche o smart."""
        new_state = event.data.get("new_state")
        entity_id = event.data.get("entity_id")

        if entity_id == self._physical_light or entity_id == self._smart_light:
            self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Ritorna il nome della luce."""
        return self._name

    @property
    def is_on(self):
        """Ritorna True se la luce è accesa."""
        return self._state == STATE_ON

    @property
    def brightness(self):
        """Ritorna la luminosità della luce."""
        return self._brightness

    @property
    def xy_color(self):
        """Ritorna il valore di colore XY."""
        return self._xy_color

    @property
    def color_temp(self):
        """Ritorna la temperatura colore in Kelvin."""
        return self._color_temp

    @property
    def color_mode(self):
        """Ritorna la modalità di colore attuale."""
        return self._color_mode

    @property
    def supported_color_modes(self):
        """Ritorna le modalità di colore supportate."""
        return self._supported_color_modes or ['color_temp', 'xy']

    @property
    def supported_features(self):
        """Ritorna le funzionalità supportate."""
        return self._supported_features

    @property
    def device_info(self):
        """Ritorna le informazioni del dispositivo per la luce virtuale."""
        return {
            "identifiers": {(self._entry_id,)},
            "name": self._name,
            "manufacturer": "Virtual Light Manufacturer",
            "model": "Virtual Light Model",
            "sw_version": "1.0",
            "via_device": (self._entry_id,)
        }

    async def async_turn_on(self, **kwargs):
        """Accende la luce."""
        # Aggiorna i parametri nel caso in cui siano stati modificati
        self._update_parameters_from_config()

        physical_state = self.hass.states.get(self._physical_light).state

        if physical_state == STATE_OFF:
            # Accendi la luce fisica
            await self.hass.services.async_call("light", "turn_on", {
                "entity_id": self._physical_light
            })

        # Attendere che la luce smart diventi disponibile prima di applicare la luminosità
        await self._wait_for_smart_light_available()

        # Applica la luminosità solo dopo che la luce smart è disponibile
        if self._brightness_on_switch and ATTR_BRIGHTNESS not in kwargs:
            await self.hass.services.async_call("light", "turn_on", {
                "entity_id": self._smart_light,
                "brightness_pct": self._brightness_on_switch
            })
        else:
            await self.hass.services.async_call("light", "turn_on", {"entity_id": self._smart_light})

        self._state = STATE_ON
        self.async_write_ha_state()

    async def _wait_for_smart_light_available(self):
        """Aspetta che la luce smart diventi disponibile e controlla se la luce fisica viene spenta."""
        smart_state = self.hass.states.get(self._smart_light)
        self._waiting_for_smart_light = True  # Imposta il flag di attesa per la luce smart

        # Continua a controllare fino a quando la luce smart non è disponibile o fino a quando la luce fisica non viene spenta
        while smart_state.state == "unavailable" and self._waiting_for_smart_light:
            await asyncio.sleep(1)
            smart_state = self.hass.states.get(self._smart_light)

            # Controlla lo stato della luce fisica
            physical_state = self.hass.states.get(self._physical_light)
            if physical_state.state == STATE_OFF:
                # Interrompi l'attesa e spegni subito la luce fisica se richiesto
                self._waiting_for_smart_light = False  # Spegni il flag
                if self._turn_off_physical:
                    await self.hass.services.async_call("light", "turn_off", {
                        "entity_id": self._physical_light
                    })
                return  # Spegni subito la luce e interrompi l'attesa

    async def async_turn_off(self, **kwargs):
        """Spegne la luce."""
        self._update_parameters_from_config()

        # Se la luce smart è disponibile, spegnila
        await self.hass.services.async_call("light", "turn_off", {"entity_id": self._smart_light})

        # Se è abilitata l'opzione per spegnere la luce fisica, spegnila
        if self._turn_off_physical:
            await self.hass.services.async_call("light", "turn_off", {"entity_id": self._physical_light})

        # Interrompi l'attesa per la luce smart, se attiva
        self._waiting_for_smart_light = False

        self._state = STATE_OFF
        self.async_write_ha_state()

    async def async_update(self):
        """Recupera lo stato da entrambe le luci."""
        smart_state = self.hass.states.get(self._smart_light)
        physical_state = self.hass.states.get(self._physical_light)

        if smart_state and smart_state.state == STATE_ON:
            self._state = STATE_ON
            self._brightness = smart_state.attributes.get(ATTR_BRIGHTNESS)
            self._xy_color = smart_state.attributes.get(ATTR_XY_COLOR)
            self._color_temp = smart_state.attributes.get(ATTR_COLOR_TEMP)
            self._color_mode = smart_state.attributes.get(ATTR_COLOR_MODE)
            self._supported_color_modes = smart_state.attributes.get(ATTR_SUPPORTED_COLOR_MODES) or ['color_temp', 'xy']
            self._supported_features = smart_state.attributes.get('supported_features', SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP | SUPPORT_COLOR)
        else:
            self._state = STATE_OFF

        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Assicura che l'entità venga aggiornata quando viene aggiunta a Home Assistant."""
        await self.async_update()

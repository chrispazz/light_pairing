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

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the light pairing based on a config entry."""
    physical_light = config_entry.data["physical_light"]
    smart_light = config_entry.data["smart_light"]
    name = config_entry.data["name"]

    async_add_entities([LightPairEntity(hass, physical_light, smart_light, name, config_entry.entry_id)])

class LightPairEntity(LightEntity):
    """Representation of the paired light with a corresponding device."""

    def __init__(self, hass, physical_light, smart_light, name, entry_id):
        """Initialize the light pairing."""
        self.hass = hass
        self._physical_light = physical_light
        self._smart_light = smart_light
        self._name = name
        self._entry_id = entry_id  # ID univoco del dispositivo
        self._state = None
        self._brightness = None
        self._xy_color = None
        self._color_temp = None
        self._color_mode = None
        self._supported_color_modes = []
        self._supported_features = SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP | SUPPORT_COLOR

        # Ascolta i cambiamenti di stato delle luci fisiche e smart
        self.hass.bus.async_listen("state_changed", self._state_changed_listener)

    @callback
    def _state_changed_listener(self, event):
        """Handle the state changes of the physical or smart lights."""
        new_state = event.data.get("new_state")
        entity_id = event.data.get("entity_id")

        if entity_id == self._physical_light or entity_id == self._smart_light:
            # Aggiorna lo stato interno
            self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self):
        """Return true if the light is on."""
        return self._state == STATE_ON

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def xy_color(self):
        """Return the XY color value."""
        return self._xy_color

    @property
    def color_temp(self):
        """Return the color temperature in Kelvin."""
        return self._color_temp

    @property
    def color_mode(self):
        """Return the current color mode."""
        return self._color_mode

    @property
    def supported_color_modes(self):
        """Return supported color modes."""
        return self._supported_color_modes or ['color_temp', 'xy']

    @property
    def supported_features(self):
        """Flag supported features."""
        return self._supported_features

    @property
    def device_info(self):
        """Return device information for the virtual light."""
        return {
            "identifiers": {(self._entry_id,)},
            "name": self._name,
            "manufacturer": "Virtual Light Manufacturer",
            "model": "Virtual Light Model",
            "sw_version": "1.0",
            "entry_type": "service",
        }

    async def async_turn_on(self, **kwargs):
        """Turn on the light."""
        physical_state = self.hass.states.get(self._physical_light).state

        # Accendi la luce fisica se è spenta
        if physical_state == STATE_OFF:
            await self.hass.services.async_call("light", "turn_on", {"entity_id": self._physical_light})

        # Se non ci sono parametri aggiuntivi (luminosità, colore), invia solo il comando turn_on alla luce smart
        if not kwargs:
            # Nessun parametro, accendi semplicemente la luce smart
            await self.hass.services.async_call("light", "turn_on", {"entity_id": self._smart_light})
        else:
            # Se ci sono parametri come luminosità o colore, invia questi parametri
            if ATTR_XY_COLOR in kwargs:
                await self.hass.services.async_call(
                    "light", "turn_on", {"entity_id": self._smart_light, ATTR_XY_COLOR: kwargs[ATTR_XY_COLOR]}
                )
            elif ATTR_COLOR_TEMP in kwargs:
                await self.hass.services.async_call(
                    "light", "turn_on", {"entity_id": self._smart_light, ATTR_COLOR_TEMP: kwargs[ATTR_COLOR_TEMP]}
                )
            if ATTR_BRIGHTNESS in kwargs:
                await self.hass.services.async_call(
                    "light", "turn_on", {"entity_id": self._smart_light, ATTR_BRIGHTNESS: kwargs[ATTR_BRIGHTNESS]}
                )

        # Imposta lo stato a ON
        self._state = STATE_ON
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the light."""
        await self.hass.services.async_call("light", "turn_off", {"entity_id": self._smart_light})
        self._state = STATE_OFF
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch state from both lights."""
        # Recupera lo stato della luce smart
        smart_state = self.hass.states.get(self._smart_light)
        physical_state = self.hass.states.get(self._physical_light)

        if smart_state and smart_state.state == STATE_ON:
            self._state = STATE_ON  # Assicurati di impostare lo stato come ON
            self._brightness = smart_state.attributes.get(ATTR_BRIGHTNESS)
            self._xy_color = smart_state.attributes.get(ATTR_XY_COLOR)
            self._color_temp = smart_state.attributes.get(ATTR_COLOR_TEMP)
            self._color_mode = smart_state.attributes.get(ATTR_COLOR_MODE)
            self._supported_color_modes = smart_state.attributes.get(ATTR_SUPPORTED_COLOR_MODES) or ['color_temp', 'xy']
            self._supported_features = smart_state.attributes.get('supported_features', SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP | SUPPORT_COLOR)
        else:
            # Se lo stato della luce smart è OFF, imposta lo stato della virtuale su OFF
            self._state = STATE_OFF

        # Aggiorna lo stato della luce virtuale per riflettere gli stati aggiornati
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Ensure the entity is updated when added to Home Assistant."""
        # Forza un aggiornamento dello stato quando l'entità è aggiunta a Home Assistant
        await self.async_update()

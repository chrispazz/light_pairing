# 💡 Light Pairing Integration

[![Add Integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg?domain=light_pairing)](https://my.home-assistant.io/redirect/config_flow_start/?domain=light_pairing)

**Light Pairing** is a custom [Home Assistant](https://www.home-assistant.io/) integration that allows you to combine a physical light and a smart light, creating a **new virtual entity** that intelligently manages both lights. This entire integration was developed with the assistance of artificial intelligence.

## 📋 Description

This integration allows you to create **light pairs** consisting of:

1. **Physical Light**: A physical switch or light that controls the light fixture (with on/off functionality).
2. **Smart Light**: A smart light entity with on/off, brightness, and color control.

### 🔧 How It Works

The virtual light entity acts as a unified interface to control both the physical and smart lights seamlessly, providing the following behavior:

- **Turn On (ON)**:
    - Turns on the physical light if it is off.
    - If the physical light is already on, it turns on the smart light.
  
- **Turn Off (OFF)**:
    - Turns off the smart light but leaves the physical light on (unless configured otherwise).

- **Brightness Adjustment**:
    - If the physical light is off, it turns on the physical light first and then adjusts the brightness of the smart light once it becomes available.

- **Color Change**:
    - If the physical light is off, it turns it on and then adjusts the color of the smart light once it becomes available.

### 🔧 Configuration Parameters

When setting up the integration, you can configure the following options:

- **Brightness on Switch On**: Specify the brightness percentage (0-100%) that should be applied to the smart light when the physical light is turned on.
  
- **Turn Off Physical Light**: Choose whether to turn off the physical light when the virtual entity is turned off.

## 🚀 Installation & Setup

1. **Add the Integration**: Use the button below to add the Light Pairing integration directly to your Home Assistant instance.

   [![Add Integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg?domain=light_pairing)](https://my.home-assistant.io/redirect/config_flow_start/?domain=light_pairing)

2. **Configure the Light Pair**:
    - Select a **physical light** (switch or light entity).
    - Select a **smart light** (light entity).
    - Choose a **name** for the new virtual light.
    - Set the **brightness percentage** for when the physical switch is turned on.
    - Choose if the **physical light should turn off** when the virtual light is turned off.

## 🧠 AI-Powered Development

This integration was fully developed using **artificial intelligence** to ensure a smooth and efficient workflow. From concept to implementation, the AI provided structured code, intelligent configuration flows, and seamless user experience.

## 📘 Documentation & Support

For more details on how to use this integration and troubleshooting, please visit the official [Home Assistant documentation](https://www.home-assistant.io/) or refer to the community forums.

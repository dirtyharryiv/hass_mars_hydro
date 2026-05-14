# HA Mars Hydro

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Community Forum][forum-shield]][forum]

## Mars Hydro Cloud Integration

This Home Assistant custom integration communicates with the Mars Hydro Cloud API and exposes supported Mars Hydro lights and fans as Home Assistant entities.

## Project Notice

This project is a fork of [suppqt/hass_mars_hydro](https://github.com/suppqt/hass_mars_hydro).
AI tools helped during development.

## Supported Devices

The integration is intended for Mars Hydro lights and compatible fans connected through the Mars Hydro Bluetooth USB Stick or directly via wifi and visible in the Mars Legacy app (Mars Hydro app).

The integration uses the first light and the first fan returned by the Mars Hydro API. Entity creation depends on the devices found by the API:

- If a light is found, light entities are created.
- If a fan is found, fan entities are created.
- If a device type is missing, entities for that device type are skipped.

## Features

- Light brightness control through a Home Assistant light entity.
- Fan strength control through a Home Assistant fan entity with a 25-100 percent percentage slider.
- Power switches for detected lights and fans.
- Brightness sensor for detected lights.
- Fan sensors for temperature, humidity, and speed.
- Temperature sensor unit selection during setup: Celsius or Fahrenheit.

## Entities

Detected lights can create:

- `light`: brightness control
- `switch`: light power
- `sensor`: brightness percentage

Detected fans can create:

- `fan`: fan strength control
- `switch`: fan power
- `sensor`: temperature in the selected unit
- `sensor`: humidity percentage
- `sensor`: fan speed in RPM

The temperature setup option creates one temperature sensor, either Celsius or Fahrenheit.

## Setup

### Installation

[![Open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dirtyharryiv&repository=hass_mars_hydro&category=Integration)

1. Open the link above and add the repository to HACS.
2. Install the Mars Hydro integration from HACS.
3. Restart Home Assistant.

### Configuration

1. Sign in to the Mars Hydro app and connect the devices there.
2. Add the Mars Hydro integration in Home Assistant.
3. Enter the Mars Hydro account email and password.
4. Select the temperature unit for the fan temperature sensor: `C` or `F`.

## Notes

- This integration uses the Mars Hydro Cloud API.
- Devices must be connected to the Mars Hydro account and reachable through the cloud API.
- Use the Mars Legacy (Mars Hydro app), not MarsPro.
- The Mars Hydro API allows a single active app session. Logging in through Home Assistant can sign the account out of the Mars Hydro app.
- Home Assistant may keep old registry entries after an entity type is removed from the integration. Remove unused entities from the Home Assistant entity registry if needed.

## Contributions

Contributions are welcome. Please read the [Contribution guidelines](CONTRIBUTING.md).

***

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/dirtyharryiv/hass_mars_hydro.svg?style=for-the-badge
[commits]: https://github.com/dirtyharryiv/hass_mars_hydro/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/dirtyharryiv/hass_mars_hydro.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%20%40dirtyharryiv-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/dirtyharryiv/hass_mars_hydro.svg?style=for-the-badge
[releases]: https://github.com/dirtyharryiv/hass_mars_hydro/releases

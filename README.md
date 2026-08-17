# VelaSmart for Home Assistant

Home Assistant integration for **VelaSmart** smart curtains / blinds. Control your
VelaSmart curtains — open, close, and set an exact position — from Home Assistant.

> This is a custom integration distributed via [HACS](https://hacs.xyz).

## Features

- Control your VelaSmart curtains (cover entities).
- Open / close / set position (0–100%).
- Automatic state polling every 30 seconds.
- Multiple accounts supported — add each VelaSmart account as a separate entry.

## Installation

### HACS (recommended)

1. Make sure [HACS](https://hacs.xyz) is installed.
2. Add this repository as a **custom repository** (category *Integration*), or
   install it directly from the HACS store once it is listed.
3. Search for **VelaSmart** and install.
4. Restart Home Assistant.

### Manual

Copy the `custom_components/velasmart` folder into the `custom_components`
directory of your Home Assistant configuration, then restart Home Assistant.

## Configuration

1. In Home Assistant go to **Settings → Devices & Services → Add Integration**.
2. Search for **VelaSmart**.
3. Enter your VelaSmart account **username** and **password**.
4. Your curtains will appear as cover entities.

## Supported devices

VelaSmart smart curtains / blinds that are bound to a VelaSmart account and are
visible in the VelaSmart app.

## Known limitations

- State is polled from the VelaSmart cloud every 30 seconds, so there may be a
  short delay before a position change is reflected in Home Assistant.
- An internet connection is required (the integration talks to the VelaSmart cloud).

## Troubleshooting

- **"Invalid username or password"** — double-check your VelaSmart account
  credentials.
- **Device not showing up** — confirm the curtain is bound to the same account in
  the VelaSmart app.

## License

[MIT](LICENSE)

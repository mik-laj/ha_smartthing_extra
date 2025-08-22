# SmartThings Extra (Home Assistant Custom Component)

This custom component adds a simple service to **synchronize the clock on Samsung ovens** (and other supported Samsung devices) through the **existing SmartThings integration** in Home Assistant.  
It does **not** use a Personal Access Token — instead it reuses the SmartThings client and tokens already managed by HA.

---

## Installation

1. Copy the folder `smartthing_extra` into your Home Assistant `custom_components/` directory:

```
config/
└── custom_components/
  └── smartthing_extra/
    ├── __init__.py
    ├── manifest.json
    └── services.yaml

```

2. Add the component to your `configuration.yaml`:

```yaml
smartthing_extra:
```

3. Restart Home Assistant.

4. After restart, the new service `smartthing_extra.sync_time`` will be available in Developer Tools → Services.

---

## Service: `smartthing_extra.sync_time`

### Fields

| Field      | Required | Description                                                                 |
|------------|----------|-----------------------------------------------------------------------------|
| `device_id`| yes      | The **HA device_id** of your Samsung oven (from *Settings → Devices*). Only SmartThings devices can be selected. |

The service automatically:
- Resolves the SmartThings `deviceId` and the proper SmartThings config entry.
- Builds the correct `execute` command with the current system time (`YYYY-MM-DDTHH:MM:SS`).
- Sends it to the device through SmartThings Cloud.

---

## Example Usage

### One-time service call
```yaml
  - action: smartthing_extra.sync_time
    metadata: {}
    data:
      device_id: e92fdc827a68e76c6025876d90174f84
```

### Automation: Sync clock at HA startup

```yaml
alias: Sync time on kitchen oven
description: ""
triggers:
  - trigger: homeassistant
    event: start
conditions: []
actions:
  - action: smartthing_extra.sync_time
    metadata: {}
    data:
      device_id: e92fdc827a68e76c6025876d90174f84
mode: single

```

---

## Notes

* Only works for devices connected through the **SmartThings integration**.
* No PAT (personal access token) needed — tokens are handled by HA’s built-in SmartThings integration.
* The time is sent in local time without timezone offset (e.g. `2025-08-22T13:37:00`).

---

## License

MIT

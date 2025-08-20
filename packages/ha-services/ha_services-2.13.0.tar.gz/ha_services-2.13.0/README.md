# ha_services

[![tests](https://github.com/jedie/ha_services/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jedie/ha_services/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/jedie/ha_services/branch/main/graph/badge.svg)](https://app.codecov.io/github/jedie/ha_services)
[![ha_services @ PyPi](https://img.shields.io/pypi/v/ha_services?label=ha_services%20%40%20PyPi)](https://pypi.org/project/ha_services/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ha_services)](https://github.com/jedie/ha_services/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/ha_services)](https://github.com/jedie/ha_services/blob/main/LICENSE)

Helpers to send periodic information via MQTT to Home Assistant

* https://pypi.org/project/ha-services/

Use by:

* https://github.com/jedie/tinkerforge2mqtt
* https://github.com/jedie/victron-ble2mqtt
* https://github.com/jedie/energymeter2mqtt
* https://github.com/jedie/pysmartmeter

# start development

```bash
~$ git clone https://github.com/jedie/ha-services.git
~$ cd inverter-connect
~/ha-services$ ./dev-cli.py --help
```


# dev CLI

[comment]: <> (✂✂✂ auto generated dev help start ✂✂✂)
```
usage: ./dev-cli.py [-h]
                    {check-code-style,coverage,fix-code-style,install,mypy,nox,pip-audit,publish,test,update,update-te
st-snapshot-files,version}



╭─ options ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ -h, --help        show this help message and exit                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ subcommands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ {check-code-style,coverage,fix-code-style,install,mypy,nox,pip-audit,publish,test,update,update-test-snapshot-file │
│ s,version}                                                                                                         │
│     check-code-style                                                                                               │
│                   Check code style by calling darker + flake8                                                      │
│     coverage      Run tests and show coverage report.                                                              │
│     fix-code-style                                                                                                 │
│                   Fix code style of all ha_services source code files via darker                                   │
│     install       Install requirements and 'ha_services' via pip as editable.                                      │
│     mypy          Run Mypy (configured in pyproject.toml)                                                          │
│     nox           Run nox                                                                                          │
│     pip-audit     Run pip-audit check against current requirements files                                           │
│     publish       Build and upload this project to PyPi                                                            │
│     test          Run unittests                                                                                    │
│     update        Update "requirements*.txt" dependencies files                                                    │
│     update-test-snapshot-files                                                                                     │
│                   Update all test snapshot files (by remove and recreate all snapshot files)                       │
│     version       Print version and exit                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated dev help end ✂✂✂)


# DEMO app CLI

[comment]: <> (✂✂✂ auto generated main help start ✂✂✂)
```
usage: ./cli.py [-h]
                {edit-settings,info,print-settings,publish-loop,systemd-debug,systemd-logs,systemd-remove,systemd-setu
p,systemd-status,systemd-stop,test-mqtt-connection,update-readme-history,version,wifi-info}



╭─ options ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ -h, --help        show this help message and exit                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ subcommands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ {edit-settings,info,print-settings,publish-loop,systemd-debug,systemd-logs,systemd-remove,systemd-setup,systemd-st │
│ atus,systemd-stop,test-mqtt-connection,update-readme-history,version,wifi-info}                                    │
│     edit-settings                                                                                                  │
│                   Edit the settings file. On first call: Create the default one.                                   │
│     info          Publish data once and display information about all registered components.                       │
│     print-settings                                                                                                 │
│                   Display (anonymized) MQTT server username and password                                           │
│     publish-loop  Publish data via MQTT for Home Assistant (endless loop)                                          │
│     systemd-debug                                                                                                  │
│                   Print Systemd service template + context + rendered file content.                                │
│     systemd-logs  List and follow logs of systemd service. (May need sudo)                                         │
│     systemd-remove                                                                                                 │
│                   Write Systemd service file, enable it and (re-)start the service. (May need sudo)                │
│     systemd-setup                                                                                                  │
│                   Write Systemd service file, enable it and (re-)start the service. (May need sudo)                │
│     systemd-status                                                                                                 │
│                   Display status of systemd service. (May need sudo)                                               │
│     systemd-stop  Stops the systemd service. (May need sudo)                                                       │
│     test-mqtt-connection                                                                                           │
│                   Test connection to MQTT Server                                                                   │
│     update-readme-history                                                                                          │
│                   Update project history base on git commits/tags in README.md Will be exited with 1 if the        │
│                   README.md was updated otherwise with 0.                                                          │
│                                                                                                                    │
│                   Also, callable via e.g.:                                                                         │
│                       python -m cli_base update-readme-history -v                                                  │
│     version       Print version and exit                                                                           │
│     wifi-info     Just display the WiFi info                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated main help end ✂✂✂)


# Backwards-incompatible changes
## v2.10.0

For new validation the main loop should catch `InvalidStateValue` exceptions,
log it as warning and continue the loop.
See `ha_services.example.publish_forever()` for an example ;)

## v2.0.0

Complete refactor of `mqtt4homeassistant` module.
New usage, see: `ha_services/example.py`


# History

[comment]: <> (✂✂✂ auto generated history start ✂✂✂)

* [v2.13.0](https://github.com/jedie/ha-services/compare/v2.12.0...v2.13.0)
  * 2025-08-20 - NEW: Add "info" command to display information about all components
  * 2025-08-20 - Bugfix: Make registry of all components "global"
  * 2025-08-19 - Individual "throttle_sec" and "config_throttle_sec"
  * 2025-08-19 - Update requirements
* [v2.12.0](https://github.com/jedie/ha-services/compare/v2.11.0...v2.12.0)
  * 2025-06-17 - Add "systemd-logs"
* [v2.11.0](https://github.com/jedie/ha-services/compare/v2.10.0...v2.11.0)
  * 2025-06-17 - Add and send "qos" and "retain"
  * 2025-06-16 - Update requirements
* [v2.10.0](https://github.com/jedie/ha-services/compare/v2.9.0...v2.10.0)
  * 2025-04-08 - Optional validation of sensor states

<details><summary>Expand older history entries ...</summary>

* [v2.9.0](https://github.com/jedie/ha-services/compare/v2.8.0...v2.9.0)
  * 2025-04-08 - Add Wifi info into MainMqttDevice
* [v2.8.0](https://github.com/jedie/ha-services/compare/v2.7.0...v2.8.0)
  * 2025-04-08 - Fix get_system_start_datetime()
  * 2025-04-08 - pip-tools -> uv
* [v2.7.0](https://github.com/jedie/ha-services/compare/v2.6.0...v2.7.0)
  * 2024-09-20 - Apply manageprojects updates and replace safety with pip-audit
  * 2024-09-20 - Update requirements
  * 2024-04-22 - Bugfix: "Mhz" -> "MHz"
* [v2.6.0](https://github.com/jedie/ha-services/compare/v2.5.0...v2.6.0)
  * 2024-04-22 - fix tests using freezegun
  * 2024-04-22 - Add MQTT Select component for Home Assistant
* [v2.5.0](https://github.com/jedie/ha-services/compare/v2.4.0...v2.5.0)
  * 2024-03-27 - Skip config publising for a while and add more system sensors
* [v2.4.0](https://github.com/jedie/ha-services/compare/v2.3.0...v2.4.0)
  * 2024-03-26 - Enhance system sensors
* [v2.3.0](https://github.com/jedie/ha-services/compare/v2.2.0...v2.3.0)
  * 2024-03-26 - Replace up_time, running_time and add cpu_freq_sensor
  * 2024-03-25 - Update README.md
* [v2.2.0](https://github.com/jedie/ha-services/compare/v2.1.0...v2.2.0)
  * 2024-03-25 - Add `main_uid` as unique "prefix" that defaults to the current hostname
* [v2.1.0](https://github.com/jedie/ha-services/compare/v2.0.1...v2.1.0)
  * 2024-03-25 - Remove Python 3.9 support
  * 2024-03-25 - Update requirements
  * 2024-03-25 - Add "via_device"
* [v2.0.1](https://github.com/jedie/ha-services/compare/v2.0.0...v2.0.1)
  * 2024-03-24 - Fix #59 Don't crash if command topic can't be subscribed
* [v2.0.0](https://github.com/jedie/ha-services/compare/v0.6.0...v2.0.0)
  * 2024-03-23 - Add device class to BinarySensor
  * 2024-03-23 - fix test with python 3.10
  * 2024-03-23 - Add BinarySensor
  * 2024-03-22 - Complete refactor mqtt4homeassistant module
* [v0.6.0](https://github.com/jedie/ha-services/compare/v0.5.0...v0.6.0)
  * 2024-03-15 - Bugfix publish command
  * 2024-03-15 - Enhance MQTT data structure and defaults
  * 2024-03-15 - Update project by split CLI
  * 2024-03-15 - Update requirements
* [v0.5.0](https://github.com/jedie/ha-services/compare/v0.4.0...v0.5.0)
  * 2024-03-09 - Migrate to new paho api
  * 2024-03-09 - Apply cookiecutter template updates
  * 2024-02-22 - Update requirements
  * 2023-12-17 - Apply manageprojects updates
  * 2023-12-17 - Fix useless tuple creation
* [v0.4.0](https://github.com/jedie/ha-services/compare/v0.3.4...v0.4.0)
  * 2023-08-09 - Use https://github.com/jedie/cli-base-utilities
* [v0.3.4](https://github.com/jedie/ha-services/compare/v0.3.3...v0.3.4)
  * 2023-08-08 - move "subprocess_utils" to "cli_tools"
* [v0.3.3](https://github.com/jedie/ha-services/compare/v0.3.2...v0.3.3)
  * 2023-08-08 - Update requirements
  * 2023-08-08 - toml-settings: Expand ~ and ~user constructs for path configs
  * 2023-08-08 - Display more frames in tracebacks
* [v0.3.2](https://github.com/jedie/ha-services/compare/v0.3.1...v0.3.2)
  * 2023-05-21 - Bugfix systemd.api if Systemd is not available (e.g. on a Mac)
* [v0.3.1](https://github.com/jedie/ha-services/compare/v0.3.0...v0.3.1)
  * 2023-05-20 - Better error message in open_editor_for() and add test for it.
* [v0.3.0](https://github.com/jedie/ha-services/compare/v0.2.0...v0.3.0)
  * 2023-05-19 - Move unittest/tox commands and add a coverage fix
  * 2023-05-19 - Refactor logging setup and verbosity levels
* [v0.2.0](https://github.com/jedie/ha-services/compare/v0.1.0...v0.2.0)
  * 2023-05-18 - Use term width == 100 for README examples.
  * 2023-05-18 - Fix github CI run by apply strip_ansi() to CLI stdout
  * 2023-05-18 - try to fix CI
  * 2023-05-18 - add: AssertCliHelpInReadme() and CliMock()
  * 2023-05-18 - Add MockTomlSettings
  * 2023-05-18 - update requirements
  * 2023-05-18 - Refactor MockSystemdServiceInfo and add some tests tools
  * 2023-05-17 - Refactor SystemdServiceInfo dataclass
  * 2023-05-11 - Rafactor toml settings and systemd and other stuff ;)
  * 2023-05-11 - Bugfix sudo calls by expand_user() that has special handling for sudo calls
* [v0.1.0](https://github.com/jedie/ha-services/compare/v0.0.1...v0.1.0)
  * 2023-05-09 - Add systemd service helper
  * 2023-05-08 - Update README.md
  * 2023-05-07 - fix CI
* [v0.0.1](https://github.com/jedie/ha-services/compare/9fa332a...v0.0.1)
  * 2023-05-07 - fix packaging
  * 2023-05-07 - Implement "publish-loop"
  * 2023-05-07 - sensible editor ;)
  * 2023-05-07 - Add "mqtt4homeassistant" and "toml_settings"
  * 2023-05-07 - init

</details>


[comment]: <> (✂✂✂ auto generated history end ✂✂✂)

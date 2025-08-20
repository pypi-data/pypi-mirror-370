# py-wifi-helper

[![PyPI version](https://img.shields.io/pypi/v/py-wifi-helper.svg)](https://pypi.org/project/py-wifi-helper)
[![PyPI Downloads](https://static.pepy.tech/badge/py-wifi-helper)](https://pepy.tech/projects/py-wifi-helper)

This is a Python tool/library developed for macOS 13.5, Ubuntu 22.04, and Windows 10/11, primarily providing operations for wireless interfaces. It includes functionalities such as listing available wireless interfaces, scanning for WiFi signals using a specified wireless interface, connecting a chosen wireless interface to a specific WiFi access point, retrieving information about the connected WiFi access points for the specified wireless interface, and disconnecting the specified wireless interface.

# Installation

## Dependencies

### Windows
```bash
pip install pywifi comtypes
```

### macOS
```bash
pip install "pyobjc-core>=9.2" "pyobjc-framework-Cocoa>=9.2" "pyobjc-framework-CoreWLAN>=9.2"
```

### Ubuntu
Requires `nmcli` to be installed:
```bash
sudo apt-get install network-manager
```

# Usage

```
% py-wifi-helper --help
usage: py-wifi-helper [-h] [--action {device,scan,connect,disconnect}] [--device DEVICE] [--ssid SSID] [--password PASSWORD] [--scanner-path SCANNER_PATH]

options:
  -h, --help            show this help message and exit
  --action {device,scan,connect,disconnect}
                        command action
  --device DEVICE       interface
  --ssid SSID          ssid
  --password PASSWORD   password
  --scanner-path SCANNER_PATH
                        Path to WiFiScanner.app (macOS only)
```

## Windows

```powershell
> py-wifi-helper
{
    "version": "1.0.0",
    "device": {
        "default": "Intel(R) Wi-Fi 6 AX201 160MHz",
        "list": [
            "Intel(R) Wi-Fi 6 AX201 160MHz"
        ],
        "error": null,
        "select": "Intel(R) Wi-Fi 6 AX201 160MHz"
    },
    "connection": {
        "default": {
            "ssid": "MyWiFi",
            "log": null
        },
        "Intel(R) Wi-Fi 6 AX201 160MHz": {
            "ssid": "MyWiFi",
            "log": null
        }
    },
    "action": {
        "name": "device",
        "status": true,
        "error": null,
        "log": null
    }
}
```

## Ubuntu

```
$ lsb_release -a
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 22.04.3 LTS
Release:	22.04
Codename:	jammy

$ sudo py-wifi-helper
{
    "version": "1.0.0",
    "device": {
        "default": "wlxd1234567890",
        "list": [
            "wlxd1234567890"
        ],
        "error": null,
        "select": "wlxd1234567890"
    },
    "connection": {
        "default": {
            "ssid": null,
            "log": null
        },
        "wlxd1234567890": {
            "ssid": null,
            "log": null
        }
    },
    "action": {
        "name": "device",
        "status": true,
        "error": null,
        "log": null
    }
}
```

## macOS

### Setup Location Services Permission
Starting from macOS 15+, scanning WiFi networks requires Location Services permission. You need to set up WiFiScanner.app first:

```bash
# Default setup (creates WiFiScanner.app in current directory)
py-wifi-helper-macos-setup

# Or specify a custom location
py-wifi-helper-macos-setup --target-path ~/Applications/WiFiScanner.app
```

After setup, you'll need to:
1. Allow Location Services access when prompted
2. Or manually enable Location Services for WiFiScanner in System Settings > Privacy & Security > Location Services

### Basic Usage

```
% sw_vers
ProductName:		macOS
ProductVersion:		13.5
BuildVersion:		22G74

% py-wifi-helper
{
    "version": "1.0.0",
    "device": {
        "default": "en0",
        "list": [
            "en0"
        ],
        "error": null,
        "select": "en0"
    },
    "connection": {
        "default": {
            "ssid": "MyHomeWIFIAP",
            "log": null
        },
        "en0": {
            "ssid": "MyHomeWIFIAP",
            "log": null
        }
    },
    "action": {
        "name": "device",
        "status": true,
        "error": null,
        "log": null
    }
}
```

For scanning operations, you can either use the default WiFiScanner.app location or specify a custom path:
```bash
# Use default WiFiScanner.app location
py-wifi-helper --action scan

# Use custom WiFiScanner.app location
py-wifi-helper --action scan --scanner-path ~/Applications/WiFiScanner.app
```

### Examples

#### Scan for WiFi Networks
```bash
py-wifi-helper --action scan
```

#### Connect to WiFi
```bash
py-wifi-helper --action connect --ssid "MyWiFi" --password "12345678"
```

#### Disconnect from WiFi
```bash
py-wifi-helper --action disconnect
```

#### Use Specific Interface
```bash
py-wifi-helper --action scan --device "wlan0"
```

# Notes

- Windows requires administrator privileges for some operations
- Ubuntu requires sudo for network operations
- macOS requires Location Services permission for WiFi scanning (set up using `py-wifi-helper-macos-setup`)

# Platform Support

- Windows 10/11 (via pywifi)
- macOS 13.5+ (via CoreWLAN)
- Ubuntu 22.04+ (via nmcli)

#!/usr/bin/env python3
"""
Universal WiFiScanner.app Generator

Creates a self-contained WiFiScanner.app that works across different Python environments
"""

import os
import sys
import shutil
import plistlib
import subprocess
from pathlib import Path
import logging


def create_universal_wifi_scanner(target_dir=None, app_name="WiFiScanner"):
    """
    創建通用的 WiFiScanner.app
    
    這個 app 不依賴特定的 Python 環境，使用系統 Python
    """
    
    if target_dir is None:
        target_dir = Path.cwd()
    else:
        target_dir = Path(target_dir)
    
    app_path = target_dir / f"{app_name}.app"
    
    logger = logging.getLogger(__name__)
    logger.info(f"Creating universal WiFiScanner.app at: {app_path}")
    
    # 清除現有的 app
    if app_path.exists():
        shutil.rmtree(app_path)
    
    # 創建目錄結構
    contents = app_path / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    
    for path in [contents, macos, resources]:
        path.mkdir(parents=True, exist_ok=True)
    
    # 創建 Info.plist
    info_plist = {
        'CFBundleDisplayName': app_name,
        'CFBundleExecutable': 'wifiscan',
        'CFBundleIdentifier': f'com.py-wifi-helper.{app_name.lower()}',
        'CFBundleName': app_name,
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleVersion': '2.0.0',
        'LSMinimumSystemVersion': '10.15',  # macOS Catalina+
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,  # 讓用戶可以看到 app 啟動
        'NSLocationUsageDescription': 'WiFiScanner needs location access to scan for WiFi networks on macOS 14+',
        'NSLocationWhenInUseUsageDescription': 'This app needs location access to scan for WiFi networks',
    }
    
    plist_path = contents / 'Info.plist'
    with open(plist_path, 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # 創建主要的 CLI 工具
    cli_script = macos / "wifiscan"
    with open(cli_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Universal WiFi Scanner CLI Tool

This tool is designed to work with system Python and doesn't depend on
virtual environments or specific pyobjc installations.
"""

import sys
import json
import argparse
import traceback

def check_requirements():
    """Check if required modules are available"""
    try:
        import CoreWLAN
        import objc
        return True, None
    except ImportError as e:
        return False, str(e)

def get_security_mode_str(network):
    """Convert security mode to human readable string"""
    import CoreWLAN
    try:
        mode = network.securityMode()
        security_map = {
            CoreWLAN.kCWSecurityNone: "None",
            CoreWLAN.kCWSecurityWEP: "WEP", 
            CoreWLAN.kCWSecurityWPAPersonal: "WPA Personal",
            CoreWLAN.kCWSecurityWPAPersonalMixed: "WPA Personal Mixed",
            CoreWLAN.kCWSecurityWPA2Personal: "WPA2 Personal",
            CoreWLAN.kCWSecurityPersonal: "Personal",
            CoreWLAN.kCWSecurityDynamicWEP: "Dynamic WEP",
            CoreWLAN.kCWSecurityWPAEnterprise: "WPA Enterprise",
            CoreWLAN.kCWSecurityWPAEnterpriseMixed: "WPA Enterprise Mixed", 
            CoreWLAN.kCWSecurityWPA2Enterprise: "WPA2 Enterprise",
            CoreWLAN.kCWSecurityEnterprise: "Enterprise",
        }
        return security_map.get(mode, f"Unknown ({mode})")
    except Exception:
        return "Unknown"

def scan_wifi_networks():
    """Scan for WiFi networks using CoreWLAN"""
    import CoreWLAN
    
    try:
        # Get WiFi client
        wifi_client = CoreWLAN.CWWiFiClient.sharedWiFiClient()
        if not wifi_client:
            return {"error": "No WiFi client available"}
        
        # Get default interface
        interface = wifi_client.interface()
        if not interface:
            return {"error": "No WiFi interface found"}
        
        # Scan for networks
        networks, error = interface.scanForNetworksWithName_includeHidden_error_(None, True, None)
        
        if error:
            return {"error": f"Scan failed: {error}"}
        
        if not networks:
            return {"networks": [], "message": "No networks found"}
        
        # Convert to our format
        result_networks = []
        seen_ssids = set()
        
        for network in networks:
            try:
                ssid = network.ssid()
                if ssid and ssid not in seen_ssids:
                    seen_ssids.add(ssid)
                    
                    network_info = {
                        "ssid": ssid,
                        "signal_strength": network.rssiValue(),
                        "security": get_security_mode_str(network),
                        "channel": network.wlanChannel().channelNumber() if network.wlanChannel() else None,
                        "bssid": network.bssid() if hasattr(network, 'bssid') else None,
                    }
                    result_networks.append(network_info)
            except Exception as e:
                # Skip networks that cause errors
                continue
        
        return {"networks": result_networks}
        
    except Exception as e:
        return {"error": f"Scan exception: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="Universal WiFi Scanner")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--check", action="store_true", help="Check requirements only")
    args = parser.parse_args()
    
    # Check requirements first
    req_ok, req_error = check_requirements()
    
    if args.check:
        if req_ok:
            print(json.dumps({"status": "ok", "message": "All requirements satisfied"}))
            return 0
        else:
            print(json.dumps({"status": "error", "message": f"Missing requirements: {req_error}"}))
            return 1
    
    if not req_ok:
        error_result = {
            "error": f"Required modules not available: {req_error}",
            "help": [
                "This usually means pyobjc is not installed in the system Python.",
                "Try running: pip3 install pyobjc-framework-CoreWLAN",
                "Or install via Homebrew: brew install python-pyobjc"
            ]
        }
        print(json.dumps(error_result, indent=2 if args.json else None))
        return 1
    
    # Perform WiFi scan
    result = scan_wifi_networks()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
            return 1
        elif "networks" in result:
            networks = result["networks"]
            print(f"Found {len(networks)} networks:")
            for i, network in enumerate(networks, 1):
                print(f"  {i}. {network['ssid']}")
                print(f"     Signal: {network['signal_strength']}dB")
                print(f"     Security: {network['security']}")
                if network['channel']:
                    print(f"     Channel: {network['channel']}")
                print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))
        sys.exit(1)
''')
    
    # Make CLI script executable
    cli_script.chmod(0o755)
    
    # 創建 GUI 應用程式（用於權限請求）
    gui_script = macos / "gui_app"
    with open(gui_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
GUI component for WiFiScanner.app

This script shows a simple dialog and performs a test scan to trigger
permission requests.
"""

import sys
import time

def show_permission_dialog():
    """Show permission request dialog"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        message = """WiFiScanner needs Location Services permission to scan WiFi networks on macOS 14+.

Click OK to perform a test scan, then:
1. Allow Location Services when prompted
2. Or manually enable it in System Settings > Privacy & Security > Location Services > WiFiScanner

This window will close automatically after the test."""
        
        messagebox.showinfo("WiFi Scanner Permission Setup", message)
        root.destroy()
        
    except ImportError:
        # Fallback to simple print if tkinter not available
        print("WiFiScanner Permission Setup")
        print("=" * 40)
        print("This app needs Location Services permission to scan WiFi networks.")
        print("Please allow permission when prompted, or enable it manually in System Settings.")
        print("Performing test scan in 3 seconds...")
        time.sleep(3)

def main():
    show_permission_dialog()
    
    # Perform test scan to trigger permission request
    from pathlib import Path
    import subprocess
    import json
    
    cli_path = Path(__file__).parent / "wifiscan"
    try:
        result = subprocess.run(
            [str(cli_path), "--json"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "networks" in data:
                print(f"✅ Success! Found {len(data['networks'])} networks.")
            else:
                print("⚠️ Scan completed but may need permission setup.")
        else:
            print("⚠️ Permission setup may be required.")
            print("Please check System Settings > Privacy & Security > Location Services")
            
    except Exception as e:
        print(f"⚠️ Test scan failed: {e}")
        print("Please ensure Location Services permission is granted.")
    
    print("\\nSetup complete. You can now close this window.")
    time.sleep(2)

if __name__ == "__main__":
    main()
''')
    
    gui_script.chmod(0o755)
    
    # 更新 Info.plist 指向 GUI app
    info_plist['CFBundleExecutable'] = 'gui_app'
    with open(plist_path, 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # 簽名應用程式
    try:
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(app_path)], 
                      check=True, capture_output=True)
        logger.info("✅ App signed successfully")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ App signing failed: {e}")
    
    logger.info(f"✅ Universal WiFiScanner.app created at: {app_path}")
    return app_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    create_universal_wifi_scanner()
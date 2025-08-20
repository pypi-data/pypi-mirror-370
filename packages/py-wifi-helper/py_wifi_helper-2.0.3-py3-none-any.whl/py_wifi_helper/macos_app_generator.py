#!/usr/bin/env python3
import os
import plistlib
import shutil
from pathlib import Path
import subprocess
import sys
import logging
import traceback

def check_dependencies(quiet=False):
    """Check and install required packages."""
    required_packages = [
        'pyobjc-framework-CoreWLAN',
        'pyobjc-framework-CoreLocation',
        'pyobjc-framework-Cocoa'
    ]
    
    if not quiet:
        print("Checking and installing required packages...")
        
    try:
        for package in required_packages:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package],
                stdout=subprocess.PIPE if quiet else None,
                stderr=subprocess.PIPE if quiet else None
            )
            if not quiet:
                print(f"✓ {package} installed/verified")
        return True
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"Error installing {package}: {e}")
        return False

def sign_app(app_path, quiet=False):
    """Sign the application to enable permission requests."""
    try:
        # Remove extended attributes
        subprocess.run(
            ['xattr', '-cr', app_path],
            check=True,
            stdout=subprocess.PIPE if quiet else None,
            stderr=subprocess.PIPE if quiet else None
        )
        
        # Sign the application
        subprocess.run([
            'codesign',
            '--force',
            '--deep',
            '--sign',
            '-',
            app_path
        ], check=True,
            stdout=subprocess.PIPE if quiet else None,
            stderr=subprocess.PIPE if quiet else None
        )
        
        if not quiet:
            print("✓ Application signed successfully")
        return True
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"Error signing application: {e}")
        return False

def generate_app(app_name="WiFiScanner", quiet=False, target_dir=None, debug=False):
    """Generate the WiFiScanner.app"""
    try:
        if not check_dependencies(quiet):
            return False, "Failed to install required dependencies"

        # 處理目標目錄和應用名稱
        if target_dir is None:
            target_dir = os.getcwd()
            final_app_path = os.path.join(target_dir, f"{app_name}.app")
        else:
            # 展開用戶目錄並獲取絕對路徑
            target_dir = os.path.expanduser(target_dir)
            target_dir = os.path.abspath(target_dir)
            
            # 如果目標路徑以 .app 結尾
            if target_dir.endswith('.app'):
                final_app_path = target_dir
                app_name = os.path.basename(target_dir)[:-4]  # 移除 .app
                target_dir = os.path.dirname(target_dir)
            else:
                final_app_path = os.path.join(target_dir, f"{app_name}.app")

        if debug:
            print(f"Target directory: {target_dir}")
            print(f"App name: {app_name}")
            print(f"Final app path: {final_app_path}")
            print(f"Current working directory: {os.getcwd()}")

        # 確保目標目錄存在
        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception as e:
            return False, f"Failed to create target directory {target_dir}: {str(e)}"

        # 檢查目錄權限
        if not os.access(target_dir, os.W_OK):
            return False, f"Target directory is not writable: {target_dir}"

        # 設定應用路徑
        app_path = final_app_path
        contents_path = os.path.join(app_path, "Contents")
        macos_path = os.path.join(contents_path, "MacOS")
        resources_path = os.path.join(contents_path, "Resources")

        if debug:
            print(f"Creating app at: {app_path}")

        # 如果已存在則移除
        if os.path.exists(app_path):
            if debug:
                print(f"Removing existing app at: {app_path}")
            shutil.rmtree(app_path)

        # 創建目錄結構
        for path in [macos_path, resources_path]:
            os.makedirs(path, exist_ok=True)
            if debug:
                print(f"Created directory: {path}")

        # Generate shared WiFi scanner module
        wifi_scanner_path = os.path.join(macos_path, "wifi_scanner.py")
        with open(wifi_scanner_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
import CoreWLAN
import CoreLocation
import objc

def get_security_mode_str(network):
    """Convert security mode to human readable string"""
    try:
        mode = network.securityMode()
        if mode == CoreWLAN.kCWSecurityNone:
            return "None"
        elif mode == CoreWLAN.kCWSecurityWEP:
            return "WEP"
        elif mode == CoreWLAN.kCWSecurityWPAPersonal:
            return "WPA Personal"
        elif mode == CoreWLAN.kCWSecurityWPAPersonalMixed:
            return "WPA Personal Mixed"
        elif mode == CoreWLAN.kCWSecurityWPA2Personal:
            return "WPA2 Personal"
        elif mode == CoreWLAN.kCWSecurityPersonal:
            return "Personal"
        elif mode == CoreWLAN.kCWSecurityDynamicWEP:
            return "Dynamic WEP"
        elif mode == CoreWLAN.kCWSecurityWPAEnterprise:
            return "WPA Enterprise"
        elif mode == CoreWLAN.kCWSecurityWPAEnterpriseMixed:
            return "WPA Enterprise Mixed"
        elif mode == CoreWLAN.kCWSecurityWPA2Enterprise:
            return "WPA2 Enterprise"
        elif mode == CoreWLAN.kCWSecurityEnterprise:
            return "Enterprise"
        else:
            return f"Unknown ({mode})"
    except Exception:
        return "Unknown"

def scan_wifi():
    """Scan WiFi networks and return results"""
    try:
        wifi = CoreWLAN.CWWiFiClient.sharedWiFiClient()
        interface = wifi.interface()
        
        if not interface:
            return None, "No WiFi interface found"
        
        networks, error = interface.scanForNetworksWithName_includeHidden_error_(None, True, None)
        if error:
            return None, str(error)
        
        if not networks:
            return None, "No networks found"
        
        return networks, None
        
    except Exception as e:
        return None, str(e)
''')

        # Generate CLI tool
        cli_script_path = os.path.join(macos_path, "wifiscan")
        with open(cli_script_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
import os
import sys
import json
import argparse

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from wifi_scanner import scan_wifi, get_security_mode_str

def format_scan_results(networks, args):
    """Format scan results according to args"""
    if not networks:
        return []
        
    results = []
    for network in networks:
        ssid = network.ssid()
        if ssid:
            net_info = {
                "ssid": ssid,
                "signal_strength": network.rssiValue(),
                "security": get_security_mode_str(network),
                "channel": network.wlanChannel().channelNumber()
            }
            results.append(net_info)
    
    if args.sort:
        results.sort(key=lambda x: x["signal_strength"], reverse=True)
    
    if args.min_strength:
        results = [n for n in results if n["signal_strength"] >= args.min_strength]
    
    if args.ssid:
        results = [n for n in results if args.ssid.lower() in n["ssid"].lower()]
    
    if args.limit:
        results = results[:args.limit]
    
    return results

def print_results(networks, args):
    """Print results in the specified format"""
    if args.json:
        print(json.dumps({"networks": networks}, indent=2))
        return
    
    if not networks:
        print("No networks found matching criteria")
        return
    
    print(f"Found {len(networks)} networks:")
    for net in networks:
        print(f"\\nSSID: {net['ssid']}")
        print(f"  Signal Strength: {net['signal_strength']}dB")
        print(f"  Security: {net['security']}")
        print(f"  Channel: {net['channel']}")

def main():
    os.chdir(current_dir)
    
    parser = argparse.ArgumentParser(description="WiFi Network Scanner")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--sort", action="store_true", help="Sort by signal strength")
    parser.add_argument("--min-strength", type=int, help="Minimum signal strength in dB")
    parser.add_argument("--ssid", help="Filter by SSID (case insensitive)")
    parser.add_argument("--limit", type=int, help="Limit the number of results")
    args = parser.parse_args()

    networks, error = scan_wifi()
    if error:
        print(f"Error: {error}")
        return 1
        
    results = format_scan_results(networks, args)
    print_results(results, args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
''')
        os.chmod(cli_script_path, 0o755)

        # Generate main application script
        main_script_path = os.path.join(macos_path, "main.py")
        if debug:
            print(f"Generating main script at: {main_script_path}")
            
        with open(main_script_path, 'w', encoding='utf-8') as f:
            f.write('''#!/usr/bin/env python3
import os
import sys
import time
import AppKit
import Foundation
from wifi_scanner import scan_wifi, get_security_mode_str

def main():
    # Initialize notification center
    notification_center = Foundation.NSUserNotificationCenter.defaultUserNotificationCenter()

    # Create notification
    notification = AppKit.NSUserNotification.alloc().init()
    notification.setTitle_("WiFi Scanner")
    notification.setInformativeText_("Started WiFi scanning...")
    
    # Show notification
    notification_center.deliverNotification_(notification)
    
    try:
        networks, error = scan_wifi()
        
        if networks:
            result = ["Found WiFi networks:"]
            for network in networks:
                ssid = network.ssid()
                if ssid:
                    result.append(f"SSID: {ssid}, Signal: {network.rssiValue()}dB")
                    security = get_security_mode_str(network)
                    result.append(f"  Security: {security}")
                    result.append("  Channel: {}".format(network.wlanChannel().channelNumber()))
                    result.append("")
            
            # Create result notification
            notification = AppKit.NSUserNotification.alloc().init()
            notification.setTitle_("WiFi Scan Complete")
            notification.setInformativeText_("\\n".join(result[:5]) + "\\n...")
            notification_center.deliverNotification_(notification)
            
            # Write full results to file
            result_path = os.path.join(os.path.dirname(__file__), "scan_result.txt")
            with open(result_path, "w", encoding='utf-8') as f:
                f.write("\\n".join(result))
        else:
            notification = AppKit.NSUserNotification.alloc().init()
            notification.setTitle_("WiFi Scan Failed")
            notification.setInformativeText_(error or "Unknown error")
            notification_center.deliverNotification_(notification)
    
    except Exception as e:
        notification = AppKit.NSUserNotification.alloc().init()
        notification.setTitle_("WiFi Scan Error")
        notification.setInformativeText_(str(e))
        notification_center.deliverNotification_(notification)

if __name__ == "__main__":
    main()
    time.sleep(2)
''')
        os.chmod(main_script_path, 0o755)

        if debug:
            print(f"Generated main script: {os.path.exists(main_script_path)}")

        # Generate launcher script
        launcher_script_path = os.path.join(macos_path, "run")
        with open(launcher_script_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    env = os.environ.copy()
    python_path = subprocess.check_output(['python3', '-c', 'import site; print(site.getsitepackages()[0])'], text=True).strip()
    env['PYTHONPATH'] = f"{{env.get('PYTHONPATH', '')}}:{{python_path}}"
    
    os.chdir(script_dir)
    os.execve(sys.executable, [sys.executable, main_script], env)

if __name__ == "__main__":
    main()
''')
        os.chmod(launcher_script_path, 0o755)

        # Generate Info.plist
        info_plist = {
            'CFBundleDisplayName': app_name,
            'CFBundleExecutable': 'run',
            'CFBundleIconFile': 'AppIcon',
            'CFBundleIdentifier': f'com.example.{app_name.lower()}',
            'CFBundleName': app_name,
            'CFBundlePackageType': 'APPL',
            'CFBundleShortVersionString': '1.0',
            'LSMinimumSystemVersion': '10.10',
            'NSHighResolutionCapable': True,
            'NSSupportsAutomaticGraphicsSwitching': True,
            'LSBackgroundOnly': True,
            'NSLocationUsageDescription': 'This app needs location access to scan for WiFi networks',
            'NSLocationWhenInUseUsageDescription': 'This app needs location access to scan for WiFi networks',
        }
        
        plist_path = os.path.join(contents_path, 'Info.plist')
        with open(plist_path, 'wb') as f:
            plistlib.dump(info_plist, f)

        # Sign the application
        if not sign_app(app_path, quiet):
            return False, "Failed to sign the application"

        # 最終驗證
        paths_to_verify = [
            (app_path, "App"),
            (contents_path, "Contents"),
            (macos_path, "MacOS"),
            (resources_path, "Resources"),
            (cli_script_path, "CLI tool"),
            (plist_path, "Info.plist")
        ]
        
        for path, name in paths_to_verify:
            if not os.path.exists(path):
                return False, f"Failed to verify {name} at: {path}"
            if debug:
                print(f"✓ {name} exists at: {path}")

        return True, f"Application generated successfully at {app_path}"

    except Exception as e:
        tb = traceback.format_exc() if debug else ""
        error_msg = f"Failed to generate app: {str(e)}\n{tb}"
        return False, error_msg

if __name__ == "__main__":
    success, message = generate_app(debug=True)
    if not success:
        print(f"Error: {message}")
        sys.exit(1)
    sys.exit(0)

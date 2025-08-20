# -*- encoding: utf-8 -*-
import sys
import argparse
import datetime
import time
import json
import platform
import subprocess

from py_wifi_helper import __version__
from py_wifi_helper import yy_wifi_helper
from .config import WiFiScannerConfig

def _get_host_os_info():
    """獲取主機作業系統版本資訊"""
    try:
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            try:
                # 使用 sw_vers 獲取詳細的 macOS 資訊
                result = subprocess.run(
                    ['sw_vers'], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                
                if result.returncode == 0:
                    # 解析 sw_vers 輸出
                    lines = result.stdout.strip().split('\n')
                    info = {}
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower().replace(' ', '_')
                            info[key] = value.strip()
                    
                    version_str = info.get('productversion', 'Unknown')
                    result = {
                        'system': 'macOS',
                        'version': version_str,
                        'build': info.get('buildversion', 'Unknown'),
                        'name': info.get('productname', 'macOS'),
                        'platform_info': platform.platform()
                    }
                    
                    # 為 macOS 14+ 添加特殊提示
                    try:
                        if version_str != 'Unknown':
                            major_version = int(version_str.split('.')[0])
                            if major_version >= 14:
                                result['info'] = [
                                    f"macOS {major_version}+ requires special permissions for WiFi scanning",
                                    "Check current connection: networksetup -getairportnetwork en0",
                                    "Location Services: open \"x-apple.systempreferences:com.apple.preference.security?Privacy_LocationServices\"",
                                    "Setup permissions: py-wifi-helper-macos-setup"
                                ]
                    except (ValueError, IndexError):
                        pass
                    
                    return result
            except Exception:
                pass
            
            # Fallback 到 platform 模組
            version_str = platform.mac_ver()[0] or 'Unknown'
            result = {
                'system': 'macOS',
                'version': version_str,
                'platform_info': platform.platform()
            }
            
            # 為 macOS 14+ 添加特殊提示（fallback 版本）
            try:
                if version_str != 'Unknown':
                    major_version = int(version_str.split('.')[0])
                    if major_version >= 14:
                        result['info'] = [
                            f"macOS {major_version}+ requires special permissions for WiFi scanning",
                            "Check current connection: networksetup -getairportnetwork en0",
                            "Location Services: open \"x-apple.systempreferences:com.apple.preference.security?Privacy_LocationServices\"",
                            "Setup permissions: py-wifi-helper-macos-setup"
                        ]
            except (ValueError, IndexError):
                pass
            
            return result
            
        elif system == 'Windows':
            return {
                'system': 'Windows',
                'version': platform.version(),
                'release': platform.release(),
                'platform_info': platform.platform()
            }
            
        elif system == 'Linux':
            try:
                # 嘗試讀取 /etc/os-release
                with open('/etc/os-release', 'r') as f:
                    lines = f.readlines()
                    info = {}
                    for line in lines:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            info[key] = value.strip('"')
                    
                    return {
                        'system': 'Linux',
                        'distribution': info.get('NAME', 'Unknown'),
                        'version': info.get('VERSION', 'Unknown'),
                        'kernel': platform.release(),
                        'platform_info': platform.platform()
                    }
            except Exception:
                pass
            
            # Fallback
            return {
                'system': 'Linux',
                'distribution': platform.linux_distribution()[0] if hasattr(platform, 'linux_distribution') else 'Unknown',
                'kernel': platform.release(),
                'platform_info': platform.platform()
            }
            
        else:
            # 其他系統
            return {
                'system': system,
                'version': platform.version(),
                'platform_info': platform.platform()
            }
            
    except Exception as e:
        # 如果所有方法都失敗，返回基本資訊
        return {
            'system': platform.system(),
            'error': str(e),
            'platform_info': platform.platform()
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=['device', 'scan', 'connect', 'disconnect'], 
                       default='device', help="command action")
    parser.add_argument("--device", type=str, default=None, help="interface")
    parser.add_argument("--ssid", type=str, help="ssid")
    parser.add_argument("--password", type=str, help="password")
    parser.add_argument("--scanner-path", type=str, help="Path to WiFiScanner.app (macOS only)")
    parser.add_argument("--use-v1", action="store_true", 
                       help="Use legacy WiFi helper V1 (compatibility mode)")
    parser.add_argument("--helper-version", action="store_true",
                       help="Show which helper version is being used")
    args = parser.parse_args()

    if args.scanner_path and sys.platform == 'darwin':
        config = WiFiScannerConfig()
        config.scanner_app_path = args.scanner_path

    # 處理 helper 版本顯示
    if args.helper_version:
        if sys.platform == 'darwin':
            from .my_macos_helper import get_helper_version
            current_version = get_helper_version()
            forced_version = "v1" if args.use_v1 else None
            
            print(json.dumps({
                "platform": "macOS",
                "current_version": forced_version or current_version,
                "environment_variable": "PY_WIFI_HELPER_USE_V1=" + ("true" if current_version == "v1" else "false"),
                "command_override": "v1" if args.use_v1 else "default (v2)"
            }, indent=4))
        else:
            print(json.dumps({
                "platform": sys.platform,
                "message": "Version selection only available on macOS"
            }, indent=4))
        sys.exit(0)

    # 建立 WiFi helper，傳遞版本選擇參數
    obj = yy_wifi_helper.YYWIFIHelper(use_v1=args.use_v1 if sys.platform == 'darwin' else None)

    output = {}
    output['platform'] = obj._platform
    output['version'] = __version__
    
    # 添加 host OS 版本資訊
    output['host_os'] = _get_host_os_info()
    output['device'] = obj.getInterface()
    output['device']['select'] = args.device if args.device != None else output['device']['default']
    output['connection'] = { 'default': { 'ssid': None, 'log': None } }

    for deviceId in output['device']['list']:
        queryStatus, queryLog, queryError = obj.getConnectedAPSSID(deviceId)
        output['connection'][deviceId] = { 'ssid': None, 'log': None }
        if queryStatus:
            output['connection'][deviceId]['ssid'] = queryLog
        else:
            # 使用 queryError 如果有，否則使用 queryLog
            output['connection'][deviceId]['log'] = queryError or queryLog
        if deviceId == output['device']['select']:
            output['connection']['default'] = output['connection'][deviceId]
        
    output['action'] = {
        'name': args.action,
        'status' : False,
        'error': None,
        'log': None,
    }
    if args.action == 'device':
        if output['device']['error'] != None:
            output['action']['error'] = output['device']['error']
        else:
            output['action']['status'] = True
        print(json.dumps(output, indent=4))
        sys.exit(0)

    if args.action == 'scan':
        output['ssid'] = []
        query = obj.getAPList(output['device']['select'])
        if 'status' in query and query['status']:
            output['action']['status'] = True
            for item in query['list']:
                if item['ssid'] == None:
                    continue
                output['ssid'].append(item['ssid'])
            output['ssid'].sort()
        elif 'error' in query:
            output['action']['error'] = query['error']
        print(json.dumps(output, indent=4))
        sys.exit(0)

    if args.action == 'disconnect':
        queryStatus, queryError = obj.disconnect(output['device']['select'])
        if queryStatus:
            output['action']['status'] = True
        else:
            output['action']['error'] = queryError
        print(json.dumps(output, indent=4))
        sys.exit(0)

    if args.action == 'connect':
        if args.ssid == None:
            output['action']['error'] = 'target ssid is empty'
        else:
            queryStatus, querylog = obj.connectToAP(args.ssid, args.password, targetInterface=output['device']['select'], findSSIDBeforeConnect=True)
            if queryStatus:
                output['action']['status'] = True
                output['action']['log'] = querylog
            else:
                output['action']['error'] = querylog
        print(json.dumps(output, indent=4))
        sys.exit(0)

    output['action']['error'] = 'Not Found'
    print(json.dumps(output, indent=4))
    return

if __name__ == '__main__':
    main()

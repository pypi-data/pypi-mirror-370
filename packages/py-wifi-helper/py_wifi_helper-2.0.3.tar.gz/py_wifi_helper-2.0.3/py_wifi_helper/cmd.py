# -*- encoding: utf-8 -*-
import sys
import argparse
import datetime
import time
import json

from py_wifi_helper import __version__
from py_wifi_helper import yy_wifi_helper
from .config import WiFiScannerConfig

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=['device', 'scan', 'connect', 'disconnect'], 
                       default='device', help="command action")
    parser.add_argument("--device", type=str, default=None, help="interface")
    parser.add_argument("--ssid", type=str, help="ssid")
    parser.add_argument("--password", type=str, help="password")
    parser.add_argument("--scanner-path", type=str, help="Path to WiFiScanner.app (macOS only)")
    args = parser.parse_args()

    if args.scanner_path and sys.platform == 'darwin':
        config = WiFiScannerConfig()
        config.scanner_app_path = args.scanner_path

    obj = yy_wifi_helper.YYWIFIHelper()

    output = {}
    output['platform'] = obj._platform
    output['version'] = __version__
    output['device'] = obj.getInterface()
    output['device']['select'] = args.device if args.device != None else output['device']['default']
    output['connection'] = { 'default': { 'ssid': None, 'log': None } }

    for deviceId in output['device']['list']:
        queryStatus, queryLog = obj.getConnectedAPSSID(deviceId)
        output['connection'][deviceId] = { 'ssid': None, 'log': None }
        if queryStatus:
            output['connection'][deviceId]['ssid'] = queryLog
        else:
            output['connection'][deviceId]['log'] = queryLog
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

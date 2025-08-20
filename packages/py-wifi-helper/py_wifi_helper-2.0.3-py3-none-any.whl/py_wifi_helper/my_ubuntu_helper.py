# -*- encoding: utf-8 -*-

import time
import platform
import json
import subprocess

from . import yy_wifi_helper

class YYUbuntuWIFIHelper(yy_wifi_helper.YYOSWIFIHelper):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def disableEventHandler(self):
        pass

    def enableEventHandler(self, handler:yy_wifi_helper.YYWIFIHelper, debug:bool = False ):
        pass
    
    def getConnectedAPSSID(self, targetInterface: str | None = None) -> (bool, str | None, str | None):
        output = None

        checkInterface = self.getInterface()
        target = None
        if targetInterface == None:
            target = checkInterface['default']
        for iface in checkInterface['list']:
            if targetInterface == iface:
                target = targetInterface

        if target == None:
            return (False, f"interface not found: {targetInterface}, default: {checkInterface['default']}")

        cli = subprocess.Popen(['nmcli', 'device', 'show', target],
                stdin =subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0)
        cli.stdin.close()

        item = {}
        for line in cli.stdout:
            keyValue = line.split(":", 2)
            if len(keyValue) == 2:
                key = keyValue[0].strip()
                value = keyValue[1].strip()
                item[key] = value
        if 'GENERAL.CONNECTION' in item and item['GENERAL.CONNECTION'] != '--':
            output = item['GENERAL.CONNECTION']

        return (True, output)

    def disconnect(self, targetInterface:str | None = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> (bool, str):
        timeCost = {
            'total': time.time(),
        }

        checkInterface = self.getInterface()
        foundInterface = None
        if targetInterface == None:
            foundInterface = checkInterface['default']
        for iface in checkInterface['list']:
            if targetInterface == iface:
                foundInterface = targetInterface

        if foundInterface == None:
            return (False, f"interface not found: {targetInterface}")

        cliParams = ['nmcli', 'device', 'disconnect', foundInterface]

        cli = subprocess.Popen(cliParams,
                stdin =subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0)
        cli.stdin.close()

        result = False
        cmdOutput = []
        for line in cli.stdout:
            cmdOutput.append(line)
            if line.find('successfully disconnected'):
                result = True

        timeCost['total'] = time.time() - timeCost['total']

        cmdOutput = "\n".join(cmdOutput)
        if result == False:
            cmdOutput = f"stdout:\n{cmdOutput}\n stderr:\n{cli.stderr.read()}\n"
        return (result, f"info: {timeCost}, cmd: {cmdOutput}")

    def connectToAP(self, targetSSID:str , targetPassword: str | None = None, targetSecurity: yy_wifi_helper.YYWIFISecurityMode | None = None, findSSIDBeforeConnect:bool = False, targetInterface: str | None = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> (bool, str):
        timeCost = {
            'total': 0.0,
            'scan': 0.0,
            'connect': 0.0,
            'connected': 0.0,
        }
        timeCost['total'] = time.time()

        checkInterface = self.getInterface()
        foundInterface = None
        if targetInterface == None:
            foundInterface = checkInterface['default']
        for iface in checkInterface['list']:
            if targetInterface == iface:
                foundInterface = targetInterface

        if foundInterface == None:
            return (False, f"interface not found: {targetInterface}")

        result = False
                
        timeCost['connected'] = time.time()

        cliParams = ['nmcli', 'device', 'wifi', 'connect', targetSSID, 'ifname', foundInterface]
        if targetPassword != None:
            cliParams += ['password', targetPassword]

        cli = subprocess.Popen(cliParams,
                stdin =subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0)
        cli.stdin.close()

        result = False
        cmdOutput = []
        for line in cli.stdout:
            cmdOutput.append(line)
            if line.find('successfully activated'):
                result = True

        timeCost['connected'] = time.time() - timeCost['connected']
        timeCost['total'] = time.time() - timeCost['total']
        cmdOutput = "\n".join(cmdOutput)
        if result == False:
            cmdOutput = f"stdout:\n{cmdOutput}\n\nstderr:\n{cli.stderr.read()}\n"

        return (result, f"time cost: {timeCost}, cmd: {cmdOutput}")

    def scanToGetAPList(self, targetInterface:str | None = None):
        output = { 'status': False, 'list': [] , 'error': None }

        checkInterface = self.getInterface()
        foundInterface = None
        if targetInterface == None:
            foundInterface = checkInterface['default']
        for iface in checkInterface['list']:
            if targetInterface == iface:
                foundInterface = targetInterface

        if foundInterface == None:
            return output

        cli = subprocess.Popen(['nmcli', 'device', 'wifi', 'list', 'ifname', foundInterface],
                stdin =subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0)
        cli.stdin.close()

        fields = ["IN-USE", "BSSID", "SSID", "MODE", "CHAN", "RATE", "SIGNAL","BARS", "SECURITY"]
        fieldsInfo = {}

        getTitle = False
        for line in cli.stdout:
            if getTitle == False:
                checkPass = True
                for fieldName in fields:
                    beginOffset = line.find(fieldName)
                    if beginOffset > 0 and line[beginOffset - 1] != ' ':
                        beginOffset = line.find(fieldName, beginOffset + 1)
                    if beginOffset == -1:
                        checkPass = False
                        break
                    fieldsInfo[fieldName] = [beginOffset, -1]

                if checkPass:
                    for fieldName in fields:
                        beginOffset = fieldsInfo[fieldName][0]
                        nextOffset = -1
                        for findNextFieldName in fields:
                            if findNextFieldName == fieldName:
                                continue
                            if fieldsInfo[findNextFieldName][0] > beginOffset and (nextOffset == -1 or fieldsInfo[findNextFieldName][0] < nextOffset):
                                nextOffset = fieldsInfo[findNextFieldName][0]
                        if nextOffset != -1:
                            fieldsInfo[fieldName][1] = nextOffset - 1  
                if checkPass:
                    getTitle = True
            else:
                item = {}
                for fieldName in fields:
                    item[fieldName] = line[ fieldsInfo[fieldName][0] : fieldsInfo[fieldName][1] ].strip() if fieldsInfo[fieldName][1] != -1 else line[ fieldsInfo[fieldName][0]: ].strip() 
                #print(item)
                itemOutput = {
                    yy_wifi_helper.WIFIAP.SSID: item['SSID'],
                    yy_wifi_helper.WIFIAP.BSSID: item['BSSID'],
                    yy_wifi_helper.WIFIAP.RSSI: None,
                    yy_wifi_helper.WIFIAP.IBSS: None,
                    yy_wifi_helper.WIFIAP.SECURITY: item['SECURITY'],
                    yy_wifi_helper.WIFIAP.CHANNEL_BAND: None,
                    yy_wifi_helper.WIFIAP.CHANNEL_NUMBER: item['CHAN'],
                    yy_wifi_helper.WIFIAP.CHANNEL_WIDTH: None,
                    yy_wifi_helper.WIFIAP.RAW : item
                }
                output['list'].append(itemOutput)

        output['status'] = len(output['list']) > 0

        return output

    def getInterface(self):
        output = { 'default': None, 'list': [], 'error': None }
        cli = subprocess.Popen(['nmcli', 'device', 'show'],
                stdin =subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0)
        cli.stdin.close()

        item = {}
        for line in cli.stdout:
            keyValue = line.split(":", 2)
            if len(keyValue) == 2:
                key = keyValue[0].strip()
                value = keyValue[1].strip()
                item[key] = value
            else:
                if len(item) > 0 and 'GENERAL.TYPE' in item and item['GENERAL.TYPE'] == 'wifi' and 'GENERAL.DEVICE' in item:
                    if output['default'] == None:
                        output['default'] = item['GENERAL.DEVICE']
                    output['list'].append(item['GENERAL.DEVICE'])
                item = {}
        
        return output

    def scanToGetAPListInJSON(self, targetInterface: str | None = None):
        output = self.scanToGetAPList(targetInterface)
        if output['status'] == True:
            for i in range(len(output['list'])):
                if 'object' in output['list'][i]:
                    del output['list'][i]['object']
        try:
            return json.dumps(output, indent=4)
        except Exception as e:
            return {'error': str(e)}

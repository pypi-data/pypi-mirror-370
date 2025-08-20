# -*- encoding: utf-8 -*-

import time
import platform
import json
import pywifi
from pywifi import const

from . import yy_wifi_helper

class YYWindowsWIFIHelper(yy_wifi_helper.YYOSWIFIHelper):
    def __init__(self):
        self.wifi = pywifi.PyWiFi()
        self.eventHandler = None

    def __del__(self):
        self.disableEventHandler()
        self.wifi = None

    def disableEventHandler(self):
        self.eventHandler = None

    def enableEventHandler(self, handler:yy_wifi_helper.YYWIFIHelper, debug:bool = False):
        self.eventHandler = handler
    
    def getConnectedAPSSID(self, targetInterface: str | None = None) -> (bool, str | None, str | None):
        """獲取指定介面當前連接的 WiFi SSID"""
        output = None
        
        try:
            currentInterface = self.getInterface()
            if targetInterface is None:
                targetInterface = currentInterface['default']
            elif targetInterface not in currentInterface['list']:
                return (False, output, f"interface not found: {targetInterface}")
        except Exception as e:
            return (False, output, f"find interface error: {targetInterface}, {str(e)}")

        targetRealInterface = None
        try:
            for iface in self.wifi.interfaces():
                if iface.name() == targetInterface:
                    targetRealInterface = iface
                    break
        except Exception as e:
            return (False, output, f"get interface error: {str(e)}")

        if targetRealInterface is None:
            return (False, output, f"interface is empty")

        try:
            if targetRealInterface.status() == const.IFACE_CONNECTED:
                try:
                    # 獲取當前連接的配置
                    profile = targetRealInterface.network_profiles()[0]
                    output = profile.ssid
                except IndexError:
                    return (False, output, "No network profile found")
            return (True, output)
        except Exception as e:
            return (False, output, f"get ssid error: {str(e)}")

    def disconnect(self, targetInterface:str | None = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> (bool, str):
        """斷開指定介面的 WiFi 連接"""
        timeCost = {
            'total': time.time(),
        }

        try:
            currentInterface = self.getInterface()
            if targetInterface is None:
                targetInterface = currentInterface['default']
            elif targetInterface not in currentInterface['list']:
                return (False, f"interface not found: {targetInterface}")
        except Exception as e:
            return (False, f"find interface error: {targetInterface}, {str(e)}")

        targetRealInterface = None
        try:
            for iface in self.wifi.interfaces():
                if iface.name() == targetInterface:
                    targetRealInterface = iface
                    break
        except Exception as e:
            return (False, f"get interface error: {str(e)}")

        if targetRealInterface is None:
            return (False, f"interface is empty")

        try:
            targetRealInterface.disconnect()
            
            if not asyncMode:
                waitCount = asyncWaitTimeout
                while waitCount > 0:
                    if targetRealInterface.status() != const.IFACE_CONNECTED:
                        break
                    time.sleep(0.1)
                    waitCount -= 0.1
                if targetRealInterface.status() == const.IFACE_CONNECTED:
                    return (False, "disconnect timeout")
            
            timeCost['total'] = time.time() - timeCost['total']
            return (True, f"time cost: {timeCost}")
            
        except Exception as e:
            return (False, f"disconnect error: {str(e)}")

    def connectToAP(self, targetSSID:str, targetPassword: str | None = None, targetSecurity: yy_wifi_helper.YYWIFISecurityMode | None = None, findSSIDBeforeConnect:bool = False, targetInterface: str | None = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> (bool, str):
        """連接到指定的 WiFi 網路"""
        timeCost = {
            'total': time.time(),
            'scan': 0.0,
            'connect': 0.0,
            'connected': 0.0,
        }

        try:
            currentInterface = self.getInterface()
            if targetInterface is None:
                targetInterface = currentInterface['default']
            elif targetInterface not in currentInterface['list']:
                return (False, f"interface not found: {targetInterface}")
        except Exception as e:
            return (False, f"find interface error: {targetInterface}, {str(e)}")

        targetRealInterface = None
        try:
            for iface in self.wifi.interfaces():
                if iface.name() == targetInterface:
                    targetRealInterface = iface
                    break
        except Exception as e:
            return (False, f"get interface error: {str(e)}")

        if targetRealInterface is None:
            return (False, f"interface is empty")

        # 檢查當前連接
        try:
            currentStatus, currentSSID = self.getConnectedAPSSID(targetInterface)
            if currentStatus and currentSSID == targetSSID:
                timeCost['total'] = time.time() - timeCost['total']
                return (True, f"Already connected to {targetSSID}, time cost: {timeCost}")
        except Exception:
            pass

        try:
            if findSSIDBeforeConnect:
                timeCost['scan'] = time.time()
                targetRealInterface.scan()
                time.sleep(2)
                scan_results = targetRealInterface.scan_results()
                timeCost['scan'] = time.time() - timeCost['scan']
                
                found_network = False
                for result in scan_results:
                    if result.ssid == targetSSID:
                        found_network = True
                        break
                
                if not found_network:
                    return (False, f"Network {targetSSID} not found")

            # 創建網路配置
            profile = pywifi.Profile()
            profile.ssid = targetSSID
            profile.auth = const.AUTH_ALG_OPEN

            if targetPassword:
                profile.akm = [const.AKM_TYPE_WPA2PSK]
                profile.cipher = const.CIPHER_TYPE_CCMP
                profile.key = targetPassword
            else:
                profile.akm = [const.AKM_TYPE_NONE]
                profile.cipher = const.CIPHER_TYPE_NONE

            timeCost['connect'] = time.time()
            
            # 移除現有配置並添加新配置
            targetRealInterface.remove_all_network_profiles()
            tmp_profile = targetRealInterface.add_network_profile(profile)
            
            # 嘗試連接
            targetRealInterface.connect(tmp_profile)
            
            timeCost['connect'] = time.time() - timeCost['connect']

            if not asyncMode:
                timeCost['connected'] = time.time()
                waitCount = asyncWaitTimeout
                while waitCount > 0:
                    if targetRealInterface.status() == const.IFACE_CONNECTED:
                        break
                    time.sleep(0.1)
                    waitCount -= 0.1
                    
                if targetRealInterface.status() != const.IFACE_CONNECTED:
                    return (False, f"Connection timeout")
                    
                timeCost['connected'] = time.time() - timeCost['connected']

            timeCost['total'] = time.time() - timeCost['total']
            return (True, f"time cost: {timeCost}")
            
        except Exception as e:
            return (False, f"connect error: {str(e)}")

    def scanToGetAPList(self, targetInterface:str | None = None):
        """掃描可用的 WiFi 網路"""
        output = {'status': False, 'list': [], 'error': None}

        try:
            currentInterface = self.getInterface()
            if targetInterface is None:
                targetInterface = currentInterface['default']
            elif targetInterface not in currentInterface['list']:
                output['error'] = [f"interface not found: {targetInterface}, current: {currentInterface['list']}"]
                return output
        except Exception as e:
            output['error'] = [f"interface error: {str(e)}"]
            return output

        targetRealInterface = None
        try:
            for iface in self.wifi.interfaces():
                if iface.name() == targetInterface:
                    targetRealInterface = iface
                    break
        except Exception as e:
            output['error'] = [f"get interface error: {str(e)}"]
            return output

        if targetRealInterface is None:
            output['error'] = [f"interface is empty"]
            return output

        try:
            targetRealInterface.scan()
            time.sleep(2)
            results = targetRealInterface.scan_results()
            
            for result in results:
                try:
                    # 安全地獲取安全類型
                    security_type = None
                    if hasattr(result, 'akm') and result.akm:
                        security_type = str(result.akm[0])
                    
                    # 安全地獲取加密類型
                    cipher_type = None
                    if hasattr(result, 'cipher') and result.cipher:
                        cipher_type = str(result.cipher)
                    
                    # 安全地獲取 AKM 列表
                    akm_list = []
                    if hasattr(result, 'akm') and result.akm:
                        akm_list = [str(x) for x in result.akm]
                    
                    itemOutput = {
                        yy_wifi_helper.WIFIAP.SSID: result.ssid,
                        yy_wifi_helper.WIFIAP.BSSID: result.bssid,
                        yy_wifi_helper.WIFIAP.RSSI: result.signal,
                        yy_wifi_helper.WIFIAP.IBSS: None,
                        yy_wifi_helper.WIFIAP.SECURITY: security_type,
                        yy_wifi_helper.WIFIAP.CHANNEL_BAND: None,
                        yy_wifi_helper.WIFIAP.CHANNEL_NUMBER: result.freq,
                        yy_wifi_helper.WIFIAP.CHANNEL_WIDTH: None,
                        yy_wifi_helper.WIFIAP.RAW: {
                            'signal': result.signal,
                            'frequency': result.freq,
                            'akm': akm_list,
                            'cipher': cipher_type,
                            # 移除了 'quality' 因為 Profile 物件沒有這個屬性
                        }
                    }
                    output['list'].append(itemOutput)
                except Exception as e:
                    if output['error'] is None:
                        output['error'] = []
                    output['error'].append(f"parse network error: {str(e)}")
                    
            output['status'] = len(output['list']) > 0
            
        except Exception as e:
            if output['error'] is None:
                output['error'] = []
            output['error'].append(f"scan error: {str(e)}")

        return output

    def getInterface(self):
        """獲取所有可用的無線網卡介面"""
        output = {'default': None, 'list': [], 'error': None}
        
        try:
            interfaces = self.wifi.interfaces()
            
            for interface in interfaces:
                try:
                    name = interface.name()
                    if name not in output['list']:
                        output['list'].append(name)
                        if output['default'] is None:
                            output['default'] = name
                except Exception as e:
                    if output['error'] is None:
                        output['error'] = []
                    output['error'].append(f"get interface name error: {str(e)}")
                    
        except Exception as e:
            if output['error'] is None:
                output['error'] = []
            output['error'].append(f"get interfaces error: {str(e)}")
            
        return output

    def scanToGetAPListInJSON(self, targetInterface: str | None = None):
        """以 JSON 格式返回掃描結果"""
        output = self.scanToGetAPList(targetInterface)
        try:
            return json.dumps(output, indent=4)
        except Exception as e:
            return {'error': str(e)}

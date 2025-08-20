# -*- encoding: utf-8 -*-

import time
import platform
import json
import logging
import subprocess
import sys

# https://pyobjc.readthedocs.io/en/latest/notes/framework-wrappers.html
import objc
import CoreWLAN

from . import yy_wifi_helper
from .macos_wifi_permission_helper import MacOSWiFiPermissionHelper
from .config import WiFiScannerConfig

# Import existing helper for inheritance
from .my_macos_helper import YYMacOSCoreWLANHelper


class YYMacOSWIFIHelperV2(yy_wifi_helper.YYOSWIFIHelper):
    """改進版的 macOS WiFi Helper，支援 macOS 14+ 的權限要求"""
    
    def __init__(self):
        self.client = CoreWLAN.CWWiFiClient.alloc().init()
        self.systemEventHandler = None
        self._permission_helper = None
        self._config = WiFiScannerConfig()
        self._macos_version = self._get_macos_version()
        self._scan_method_tried = {'direct': False, 'wifiscanner': False}
        
        # 設定日誌
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _get_macos_version(self):
        """獲取 macOS 版本號碼"""
        try:
            # 使用 sw_vers 命令獲取版本
            result = subprocess.run(
                ['sw_vers', '-productVersion'],
                capture_output=True,
                text=True,
                check=True
            )
            version_str = result.stdout.strip()
            
            # 解析版本號（例如 "14.2.1" -> 14.2）
            parts = version_str.split('.')
            if len(parts) >= 2:
                major = int(parts[0])
                minor = int(parts[1]) if parts[1] else 0
                return float(f"{major}.{minor}")
            elif len(parts) == 1:
                return float(parts[0])
        except Exception as e:
            # 不依賴 self.logger，直接使用 logging
            logger = logging.getLogger(__name__)
            # 檢查是否在測試環境中
            if 'unittest' in sys.modules:
                logger.debug(f"Test environment: macOS version detection failed: {e}, assuming 14.0")
            else:
                logger.warning(f"無法獲取 macOS 版本: {e}，假設為 14.0")
            return 14.0  # 假設是較新的版本，使用安全的方法
        
        return 14.0
    
    def __del__(self):
        self.disableEventHandler()
        del self.client
        self.client = None
        if self.systemEventHandler != None:
            self.systemEventHandler.removeCallback()
        self.systemEventHandler = None
    
    @property
    def permission_helper(self):
        if self._permission_helper is None:
            self._permission_helper = MacOSWiFiPermissionHelper(
                app_path=self._config.scanner_app_path
            )
        return self._permission_helper
    
    def _should_use_direct_scan(self):
        """判斷是否應該使用直接掃描（CoreWLAN API）"""
        # macOS 14 之前可以直接使用 CoreWLAN
        # macOS 14+ 需要特殊處理
        return self._macos_version < 14.0
    
    def _scan_with_corewlan(self, targetInterface=None):
        """使用 CoreWLAN 直接掃描（macOS 13 及之前）"""
        output = {'status': False, 'list': [], 'error': None}
        
        try:
            # 獲取介面
            if targetInterface is None:
                currentInterface = self.getInterface()
                targetInterface = currentInterface['default']
            
            target = self.client.interfaceWithName_(targetInterface)
            if target is None:
                output['error'] = [f"Interface not found: {targetInterface}"]
                return output
            
            # 執行掃描
            networks, err = target.scanForNetworksWithName_error_(None, None)
            
            if err:
                output['error'] = [f"Scan error: {str(err)}"]
                return output
            
            if networks:
                output['status'] = True
                for item in networks:
                    try:
                        itemOutput = {
                            yy_wifi_helper.WIFIAP.SSID: item.ssid(),
                            yy_wifi_helper.WIFIAP.BSSID: item.bssid(),
                            yy_wifi_helper.WIFIAP.RSSI: item.rssiValue(),
                            yy_wifi_helper.WIFIAP.IBSS: item.ibss(),
                            yy_wifi_helper.WIFIAP.SECURITY: None,
                            yy_wifi_helper.WIFIAP.CHANNEL_BAND: None,
                            yy_wifi_helper.WIFIAP.CHANNEL_NUMBER: None,
                            yy_wifi_helper.WIFIAP.CHANNEL_WIDTH: None,
                        }
                        
                        # 嘗試獲取額外資訊
                        try:
                            itemOutput[yy_wifi_helper.WIFIAP.SECURITY] = item.security()
                        except:
                            pass
                        
                        try:
                            itemOutput[yy_wifi_helper.WIFIAP.CHANNEL_BAND] = item.wlanChannel().channelBand()
                            itemOutput[yy_wifi_helper.WIFIAP.CHANNEL_NUMBER] = item.wlanChannel().channelNumber()
                            itemOutput[yy_wifi_helper.WIFIAP.CHANNEL_WIDTH] = item.wlanChannel().channelWidth()
                        except:
                            pass
                        
                        output['list'].append(itemOutput)
                    except Exception as e:
                        self.logger.debug(f"Error processing network: {e}")
                        continue
            
        except Exception as e:
            output['error'] = [f"CoreWLAN scan failed: {str(e)}"]
        
        return output
    
    def _scan_with_wifiscanner(self, targetInterface=None):
        """使用 WiFiScanner.app 掃描（macOS 14+）"""
        output = {'status': False, 'list': [], 'error': None}
        
        # 確保 WiFiScanner.app 存在
        if not self.permission_helper.ensure_scanner_app():
            output['error'] = [
                "WiFiScanner.app not found.",
                "Please run: py-wifi-helper-macos-setup",
                f"Current macOS version: {self._macos_version}"
            ]
            return output
        
        # 使用 wifiscan CLI 工具
        try:
            cli_path = self._permission_helper.cli_path
            result = subprocess.run(
                [str(cli_path), '--json'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            data = json.loads(result.stdout)
            if 'networks' in data and data['networks']:
                output['status'] = True
                for network in data['networks']:
                    network_info = {
                        yy_wifi_helper.WIFIAP.SSID: network['ssid'],
                        yy_wifi_helper.WIFIAP.RSSI: network['signal_strength'],
                        yy_wifi_helper.WIFIAP.SECURITY: network['security'],
                        yy_wifi_helper.WIFIAP.CHANNEL_NUMBER: network['channel'],
                    }
                    output['list'].append(network_info)
            else:
                output['error'] = [
                    "No networks found or permission denied.",
                    "Please check Location Services permission for WiFiScanner.",
                    f"macOS {self._macos_version} requires Location Services for WiFi scanning."
                ]
                
        except subprocess.TimeoutExpired:
            output['error'] = ["WiFi scan timed out"]
        except json.JSONDecodeError as e:
            output['error'] = [f"Failed to parse scan results: {str(e)}"]
        except subprocess.CalledProcessError as e:
            output['error'] = [f"WiFiScanner failed: {str(e)}"]
        except Exception as e:
            output['error'] = [f"Unexpected error: {str(e)}"]
        
        return output
    
    def scanToGetAPList(self, targetInterface=None):
        """掃描 WiFi 網路，自動選擇最佳方法並提供 fallback"""
        output = {'status': False, 'list': [], 'error': None}
        errors = []
        
        self.logger.info(f"Starting WiFi scan on macOS {self._macos_version}")
        
        # 方法 1: 嘗試直接使用 CoreWLAN（適用於 macOS 13 及之前）
        if self._should_use_direct_scan() or not self._scan_method_tried['direct']:
            self.logger.debug("Trying direct CoreWLAN scan...")
            self._scan_method_tried['direct'] = True
            
            result = self._scan_with_corewlan(targetInterface)
            if result['status']:
                self.logger.info("CoreWLAN scan successful")
                return result
            else:
                if result['error']:
                    errors.extend(result['error'])
                self.logger.debug(f"CoreWLAN scan failed: {result['error']}")
        
        # 方法 2: 使用 WiFiScanner.app（適用於 macOS 14+）
        if not self._scan_method_tried['wifiscanner']:
            self.logger.debug("Trying WiFiScanner.app scan...")
            self._scan_method_tried['wifiscanner'] = True
            
            result = self._scan_with_wifiscanner(targetInterface)
            if result['status']:
                self.logger.info("WiFiScanner scan successful")
                return result
            else:
                if result['error']:
                    errors.extend(result['error'])
                self.logger.debug(f"WiFiScanner scan failed: {result['error']}")
        
        # 如果兩種方法都失敗，提供有用的錯誤訊息
        if self._macos_version >= 14.0:
            errors.insert(0, f"macOS {self._macos_version} requires special permissions for WiFi scanning.")
            errors.append("Solution: Run 'py-wifi-helper-macos-setup' to configure permissions.")
        
        output['error'] = errors if errors else ["All scan methods failed"]
        return output
    
    def scanToGetAPListInJSON(self, targetInterface=None):
        """返回 JSON 格式的掃描結果"""
        output = self.scanToGetAPList(targetInterface)
        try:
            return json.dumps(output, indent=4)
        except Exception as e:
            return json.dumps({'error': str(e)})
    
    # 以下是保持相容性的其他方法
    def getInterface(self):
        """獲取網路介面列表"""
        output = {'default': None, 'list': [], 'error': None}
        
        try:
            output['default'] = self.client.interface().interfaceName()
        except Exception as e:
            output['error'] = [str(e)]
        
        try:
            for item in self.client.interfaces():
                try:
                    output['list'].append(item.interfaceName())
                except Exception as e:
                    if output['error'] is None:
                        output['error'] = []
                    output['error'].append(str(e))
        except Exception as e:
            if output['error'] is None:
                output['error'] = []
            output['error'].append(str(e))
        
        return output
    
    def getConnectedAPSSID(self, targetInterface=None):
        """獲取當前連接的 WiFi SSID"""
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
            targetRealInterface = self.client.interfaceWithName_(targetInterface)
        except Exception as e:
            return (False, output, f"client.interface(withName): {str(e)}")
        
        if targetRealInterface == None:
            return (False, output, f"interface is empty")
        
        try:
            currentNetworkSSID = targetRealInterface.ssid()
            output = currentNetworkSSID
        except Exception as e:
            return (False, output, f"get ssid error: {str(e)}")
        
        return (True, output, None)
    
    def disconnect(self, targetInterface=None, asyncMode=False, asyncWaitTimeout=15):
        """斷開 WiFi 連接"""
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
            targetRealInterface = self.client.interfaceWithName_(targetInterface)
        except Exception as e:
            return (False, f"client.interface(withName): {str(e)}")
        
        if targetRealInterface == None:
            return (False, f"interface is empty")
        
        try:
            targetRealInterface.disassociate()
        except Exception as e:
            return (False, f"disassociate error: {str(e)}")
        
        if asyncMode == False:
            waitCount = asyncWaitTimeout + 0.5
            currentConnectedSSID = None
            while waitCount > 0.5:
                queryStatus, currentConnectedSSID, _ = self.getConnectedAPSSID(targetInterface)
                if queryStatus and currentConnectedSSID == None:
                    break
                time.sleep(0.1)
                waitCount -= 0.1
            if currentConnectedSSID != None:
                return (False, 'disassociate timeout')
        
        return (True, None)
    
    def connectToAP(self, targetSSID, targetPassword=None, targetSecurity=None, 
                    findSSIDBeforeConnect=True, targetInterface=None, 
                    asyncMode=False, asyncWaitTimeout=15):
        """連接到指定的 WiFi 網路"""
        timeCost = {
            'total': 0.0,
            'scan': 0.0,
            'connect': 0.0,
            'connected': 0.0,
        }
        timeCost['total'] = time.time()
        
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
            targetRealInterface = self.client.interfaceWithName_(targetInterface)
        except Exception as e:
            return (False, f"client.interface(withName): {str(e)}")
        
        if targetRealInterface == None:
            return (False, f"interface is empty")
        
        queryCurrentConnectedSSID, queryLog, _ = self.getConnectedAPSSID(targetInterface)
        if queryCurrentConnectedSSID == False:
            return (False, f"getConnectedAP error: {queryLog}")
        if queryLog != None:
            if queryLog == targetSSID:
                return (True, f"Already connected to the specified SSID")
        
        result = False
        errorMessage = None
        
        if findSSIDBeforeConnect:
            timeCost['scan'] = time.time()
            errorLog = None
            networks, error = targetRealInterface.scanForNetworksWithSSID_error_(
                targetSSID.encode("utf-8"), errorLog
            )
            timeCost['scan'] = time.time() - timeCost['scan']
            
            if error:
                return (False, f"Scan error: {str(error)}")
            if len(networks) == 0:
                return (False, f"Network '{targetSSID}' not found")
            
            targetNetwork = networks[0]
            
            timeCost['connect'] = time.time()
            try:
                success = targetRealInterface.associateToNetwork_password_error_(
                    targetNetwork, targetPassword, errorLog
                )
                if success:
                    result = True
                else:
                    errorMessage = f"connect error: {str(errorLog)}"
            except Exception as e:
                result = False
                errorMessage = f"connect exception: {str(e)}"
            
            timeCost['connect'] = time.time() - timeCost['connect']
        else:
            return (False, 'macOS requires findSSIDBeforeConnect=True')
        
        if result and not asyncMode:
            timeCost['connected'] = time.time()
            waitCount = asyncWaitTimeout + 0.5
            currentConnectedSSID = None
            while waitCount > 0.5:
                queryStatus, queryLog, _ = self.getConnectedAPSSID(targetInterface)
                if queryStatus and queryLog != None and queryLog == targetSSID:
                    currentConnectedSSID = queryLog
                    break
                time.sleep(0.1)
                waitCount -= 0.1
            result = currentConnectedSSID == targetSSID
            timeCost['connected'] = time.time() - timeCost['connected']
        
        timeCost['total'] = time.time() - timeCost['total']
        errorMessage = f"time cost: {timeCost}" if errorMessage == None else f"{errorMessage}, time cost: {timeCost}"
        return (result, errorMessage)
    
    def disableEventHandler(self):
        """停用事件處理器"""
        if self.systemEventHandler == None:
            return
        success = self.client.stopMonitoringAllEventsAndReturnError_(None)
        if success:
            self.logger.debug("Event monitoring stopped successfully")
        else:
            self.logger.debug("Failed to stop event monitoring")
        self.client.setDelegate_(None)
    
    def enableEventHandler(self, handler, debug=False):
        """啟用事件處理器"""
        if self.systemEventHandler == None:
            self.systemEventHandler = YYMacOSCoreWLANHelper.alloc().init()
            if handler != None:
                self.systemEventHandler.setCallback_(handler, debug)
            
            self.client.setDelegate_(self.systemEventHandler)
            for option in [
                CoreWLAN.CWEventTypeSSIDDidChange,
                CoreWLAN.CWEventTypeLinkDidChange,
                CoreWLAN.CWEventTypeLinkQualityDidChange,
                CoreWLAN.CWEventTypeScanCacheUpdated,
                CoreWLAN.CWEventTypeCountryCodeDidChange,
                CoreWLAN.CWEventTypeBSSIDDidChange,
            ]:
                success = self.client.startMonitoringEventWithType_error_(option, None)
                if success and debug:
                    self.logger.debug(f"Monitoring enabled for event type: {option}")
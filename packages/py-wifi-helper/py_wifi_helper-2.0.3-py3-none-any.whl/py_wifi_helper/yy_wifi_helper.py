# -*- encoding: utf-8 -*-

import os
import platform
import json
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

class WIFIAP_SECURITY(Enum):
    pass

class WIFIAP(str, Enum):
    SSID = 'ssid'
    BSSID = 'bssid'
    RSSI = 'rssi'
    IBSS = 'ibbs'
    SECURITY = 'security'
    CHANNEL_BAND = 'channel.band'
    CHANNEL_NUMBER = 'channel.number'
    CHANNEL_WIDTH = 'channel.width'
    RAW = 'raw'

class YYWIFISecurityMode(str, Enum):
    SecurityNone = 'SecurityNone'
    SecurityWEP = 'SecurityWEP'
    SecurityWPAPersonal = 'SecurityWPAPersonal'
    SecurityWPAPersonalMixed = 'SecurityWPAPersonalMixed'
    SecurityWPA2Personal = 'SecurityWPA2Personal'
    SecurityPersonal = 'SecurityPersonal'
    SecurityDynamicWEP = 'SecurityDynamicWEP'
    SecurityWPAEnterprise = 'SecurityWPAEnterprise'
    SecurityWPAEnterpriseMixed = 'SecurityWPAEnterpriseMixed'
    SecurityWPA2Enterprise = 'SecurityWPA2Enterprise'
    SecurityEnterprise = 'SecurityEnterprise'
    SecurityWPA3Personal = 'SecurityWPA3Personal'
    SecurityWPA3Enterprise = 'SecurityWPA3Enterprise'
    SecurityWPA3Transition = 'SecurityWPA3Transition'
    SecurityUnknown = 'SecurityUnknown'

class YYOSWIFIHelper:
    def disableEventHandler(self):
        pass

    def enableEventHandler(self, handler: None, debug:bool = False ):
        pass

    def getConnectedAPSSID(self, targetInterface: str | None = None) -> Tuple[bool, Optional[str], Optional[str]]:
        pass

    def getInterface(self) -> Dict[str, Any]:
        return {'default': None, 'list': [], 'error': None}

    def disconnect(self, targetInterface:str | None = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> Tuple[bool, str]:
        pass

    def connectToAP(self, targetSSID:str , targetPassword: str | None = None, targetSecurity: YYWIFISecurityMode | None = None, findSSIDBeforeConnect:bool = False, targetInterface: str | None = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> Tuple[bool, str]:
        pass

    def scanToGetAPList(self, targetInterface:str | None = None) -> Dict[str, Any]:
        pass

    def scanToGetAPListInJSON(self, targetInterface: str | None = None) -> str:
        pass

class YYWIFIHelper:
    def __init__(self):
        # 初始化基本屬性
        self._platform = platform.system().lower()
        self._supportPlatform = ['darwin']
        self._platformInfo = {}
        self._helper = None
        self._support = False
        self._missing_dependencies = []
        self._init_error = None
        self.eventHandler = None
        
        # Windows 平台支援
        if self._platform == 'windows':
            try:
                print("Checking required modules...")
                import comtypes
                import pywifi
                print("Initializing WiFi...")
                test_wifi = pywifi.PyWiFi()
                self._supportPlatform.append('windows')
                self._support = True
            except ImportError as e:
                self._missing_dependencies.append(('dependency', str(e)))
                print(f"[ERROR] Missing dependency: {str(e)}")
            except Exception as e:
                self._init_error = str(e)
                print(f"[ERROR] Initialization error: {str(e)}")
        
        # Linux/Ubuntu 平台支援
        elif self._platform == 'linux':
            if os.path.isfile('/etc/lsb-release'):
                for line in open('/etc/lsb-release').read().split('\n'):
                    keyValue = line.split('=')
                    if len(keyValue) == 2:
                        self._platformInfo[keyValue[0].strip().lower()] = keyValue[1].strip().lower()

            if 'distrib_id' in self._platformInfo:
                if self._platformInfo['distrib_id'] == 'ubuntu' and 'distrib_release' in self._platformInfo:
                    try:
                        if float(self._platformInfo['distrib_release']) >= 22.04:
                            from shutil import which
                            cliCheckPass = True
                            cliList = ['nmcli']
                            for cli in cliList:
                                if which(cli) is None:
                                    print(f"[INFO] cli not found: {cli}")
                                    cliCheckPass = False
    
                            if cliCheckPass:
                                self._supportPlatform.append('ubuntu')
                                self._platform = 'ubuntu'
                                self._support = True
                    except Exception as e:
                        self._init_error = str(e)
                        print(f"[ERROR] {str(e)}")
        
        # macOS 平台支援
        elif self._platform == 'darwin':
            try:
                import objc
                import CoreWLAN
                self._support = True
            except ImportError as e:
                self._missing_dependencies.append(('CoreWLAN', str(e)))
                print(f"[ERROR] {str(e)}")

        # 初始化對應平台的 helper
        if self._support:
            try:
                if self._platform == 'darwin':
                    from . import my_macos_helper
                    self._helper = my_macos_helper.YYMacOSWIFIHelper()
                elif self._platform == 'ubuntu':
                    from . import my_ubuntu_helper
                    self._helper = my_ubuntu_helper.YYUbuntuWIFIHelper()
                elif self._platform == 'windows':
                    from . import my_windows_helper
                    print("Initializing Windows WiFi Helper...")
                    self._helper = my_windows_helper.YYWindowsWIFIHelper()
            except Exception as e:
                self._support = False
                self._init_error = f"Helper initialization failed: {str(e)}"
                print(f"[ERROR] {self._init_error}")

    def eventCallback(self, info: Dict | None = None):
        if self.eventHandler and callable(self.eventHandler):
            self.eventHandler(info)

    def enableEventHandler(self, handlerFunc: None):
        if not self._support:
            print(f"Platform not supported: {self._platform}")
            return
        self.eventHandler = handlerFunc
        if self._helper:
            self._helper.enableEventHandler(self)

    def disableEventHandler(self):
        if not self._support:
            print(f"Platform not supported: {self._platform}")
            return
        if self._helper:
            self._helper.disableEventHandler()
        self.eventHandler = None

    def getInterface(self) -> Dict[str, Any]:
        if not self._support:
            error_msg = []
            if self._init_error:
                error_msg.append(self._init_error)
            if self._missing_dependencies:
                for dep, err in self._missing_dependencies:
                    error_msg.append(f"Missing {dep}: {err}")
            if not error_msg:
                error_msg.append(f"Platform {self._platform} not supported")
                
            return {
                'default': None,
                'list': [],
                'error': error_msg
            }
        
        if not self._helper:
            return {
                'default': None,
                'list': [],
                'error': ['Helper not initialized']
            }
            
        return self._helper.getInterface()

    def getAPList(self, name: Optional[str] = None) -> Dict[str, Any]:
        if not self._support:
            print(f"Platform not supported: {self._platform}")
            return {'status': False, 'list': [], 'error': ['Platform not supported']}
        if not self._helper:
            return {'status': False, 'list': [], 'error': ['Helper not initialized']}
        return self._helper.scanToGetAPList(name)

    def getAPListInJSON(self, name: Optional[str] = None) -> str:
        if not self._support:
            print(f"Platform not supported: {self._platform}")
            return json.dumps({'status': False, 'list': [], 'error': ['Platform not supported']})
        if not self._helper:
            return json.dumps({'status': False, 'list': [], 'error': ['Helper not initialized']})
        return self._helper.scanToGetAPListInJSON(name)

    def getConnectedAPSSID(self, targetInterface: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        if not self._support:
            print(f"Platform not supported: {self._platform}")
            return (False, None, 'Platform not supported')
        if not self._helper:
            return (False, None, 'Helper not initialized')
        return self._helper.getConnectedAPSSID(targetInterface)

    def disconnect(self, targetInterface: Optional[str] = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> Tuple[bool, str]:
        if not self._support:
            print(f"Platform not supported: {self._platform}")
            return (False, 'Platform not supported')
        if not self._helper:
            return (False, 'Helper not initialized')
        return self._helper.disconnect(targetInterface, asyncMode, asyncWaitTimeout)

    def connectToAP(self, targetSSID: str, targetPassword: Optional[str] = None, targetSecurity: Optional[str] = None, findSSIDBeforeConnect: bool = False, targetInterface: Optional[str] = None, asyncMode: bool = False, asyncWaitTimeout: int = 15) -> Tuple[bool, str]:
        if not self._support:
            print(f"Platform not supported: {self._platform}")
            return (False, 'Platform not supported')
        if not self._helper:
            return (False, 'Helper not initialized')
        return self._helper.connectToAP(targetSSID, targetPassword, targetSecurity, findSSIDBeforeConnect, targetInterface, asyncMode, asyncWaitTimeout)

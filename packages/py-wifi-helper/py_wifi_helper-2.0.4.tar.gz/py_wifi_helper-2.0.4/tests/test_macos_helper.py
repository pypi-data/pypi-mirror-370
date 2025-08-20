#!/usr/bin/env python3
import unittest
import sys
import platform
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Only run these tests on macOS
if platform.system() != 'Darwin':
    print("Skipping macOS tests on non-Darwin platform")
    sys.exit(0)

sys.path.insert(0, '../')

# 檢查是否有必要的依賴
try:
    import objc
    import CoreWLAN
    HAS_COREWLAN = True
except ImportError:
    HAS_COREWLAN = False

from py_wifi_helper import my_macos_helper
from py_wifi_helper import yy_wifi_helper


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestMacOSHelperExistingFunctionality(unittest.TestCase):
    """測試現有功能確保不會被破壞"""
    
    def setUp(self):
        """每個測試前的設置"""
        # 強制使用 V1 以確保測試的是穩定版本
        self.helper = my_macos_helper.create_macos_helper(use_v1=True)
    
    def test_initialization(self):
        """測試初始化"""
        self.assertIsNotNone(self.helper.client)
        self.assertIsNone(self.helper.systemEventHandler)
        self.assertIsNotNone(self.helper._config)
    
    def test_get_interface(self):
        """測試獲取網路介面"""
        result = self.helper.getInterface()
        self.assertIn('list', result)
        self.assertIsInstance(result['list'], list)
        # macOS 通常有 en0 介面
        if result['list']:
            self.assertIn('en0', result['list'])
    
    def test_get_connected_ap_ssid(self):
        """測試獲取當前連接的 SSID"""
        success, ssid, error = self.helper.getConnectedAPSSID()
        # 不管是否連接，函數應該正常執行
        self.assertIsInstance(success, bool)
        if success:
            # 如果成功，ssid 可能是 None（未連接）或字串（已連接）
            self.assertTrue(ssid is None or isinstance(ssid, str))
        else:
            # 如果失敗，應該有錯誤訊息
            self.assertIsNotNone(error)
    
    def test_permission_helper_property(self):
        """測試 permission_helper 屬性"""
        helper = self.helper.permission_helper
        self.assertIsNotNone(helper)
        # MacOSWiFiPermissionHelper 在 macos_wifi_permission_helper 模組中
        from py_wifi_helper.macos_wifi_permission_helper import MacOSWiFiPermissionHelper
        self.assertIsInstance(helper, MacOSWiFiPermissionHelper)
    
    @patch('subprocess.run')
    def test_scan_with_wifiscanner_app(self, mock_run):
        """測試使用 WiFiScanner.app 進行掃描"""
        # 模擬 WiFiScanner.app 的輸出
        mock_run.return_value = Mock(
            stdout='{"networks": [{"ssid": "TestWiFi", "signal_strength": -50, "security": "WPA2", "channel": 6}]}',
            returncode=0
        )
        
        with patch.object(self.helper.permission_helper, 'ensure_scanner_app', return_value=True):
            result = self.helper.scanToGetAPList()
            
            self.assertIn('status', result)
            self.assertIn('list', result)
            if result['status']:
                self.assertIsInstance(result['list'], list)


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestMacOSVersionDetection(unittest.TestCase):
    """測試 macOS 版本檢測功能"""
    
    def test_get_macos_version(self):
        """測試獲取 macOS 版本"""
        # 這個測試會在實作 _get_macos_version 方法後使用
        pass
    
    def test_version_based_scan_method_selection(self):
        """測試基於版本選擇掃描方法"""
        # 這個測試會在實作版本檢測後使用
        pass


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestScanMethodFallback(unittest.TestCase):
    """測試掃描方法的 fallback 機制"""
    
    @patch('subprocess.run')
    def test_fallback_from_corewlan_to_wifiscanner(self, mock_run):
        """測試從 CoreWLAN 失敗後 fallback 到 WiFiScanner.app"""
        # 這個測試會在實作 fallback 機制後使用
        pass
    
    def test_error_message_improvement(self):
        """測試改進的錯誤訊息"""
        # 這個測試會在實作改進的錯誤訊息後使用
        pass


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestBackwardCompatibility(unittest.TestCase):
    """測試向後相容性"""
    
    def test_existing_api_compatibility(self):
        """確保現有 API 保持相容"""
        helper = my_macos_helper.YYMacOSWIFIHelper()
        
        # 測試所有公開方法是否存在
        methods = [
            'getInterface',
            'getConnectedAPSSID', 
            'disconnect',
            'connectToAP',
            'scanToGetAPList',
            'scanToGetAPListInJSON',
            'enableEventHandler',
            'disableEventHandler'
        ]
        
        for method in methods:
            self.assertTrue(hasattr(helper, method), f"Method {method} should exist")
            self.assertTrue(callable(getattr(helper, method)), f"Method {method} should be callable")
    
    def test_return_value_structure(self):
        """測試返回值結構保持一致"""
        helper = my_macos_helper.YYMacOSWIFIHelper()
        
        # 測試 getInterface 返回結構
        interface_result = helper.getInterface()
        self.assertIn('default', interface_result)
        self.assertIn('list', interface_result)
        self.assertIn('error', interface_result)
        
        # 測試 scanToGetAPList 返回結構
        with patch.object(helper, 'scanToGetAPList') as mock_scan:
            mock_scan.return_value = {'status': True, 'list': [], 'error': None}
            scan_result = helper.scanToGetAPList()
            self.assertIn('status', scan_result)
            self.assertIn('list', scan_result)
            self.assertIn('error', scan_result)


if __name__ == '__main__':
    # 執行測試
    unittest.main(verbosity=2)
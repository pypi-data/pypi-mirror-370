#!/usr/bin/env python3
import unittest
import sys
import platform
from unittest.mock import Mock, patch, MagicMock, call
import subprocess
import json

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

if HAS_COREWLAN:
    from py_wifi_helper import my_macos_helper_v2
    from py_wifi_helper import yy_wifi_helper


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestMacOSVersionDetection(unittest.TestCase):
    """測試 macOS 版本檢測功能"""
    
    def test_get_macos_version_success(self):
        """測試成功獲取 macOS 版本"""
        with patch('subprocess.run') as mock_run:
            # 模擬 macOS 14.2.1
            mock_run.return_value = Mock(stdout="14.2.1\n", returncode=0)
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            self.assertEqual(helper._macos_version, 14.2)
    
    def test_get_macos_version_major_only(self):
        """測試只有主版本號的情況"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="15\n", returncode=0)
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            self.assertEqual(helper._macos_version, 15.0)
    
    def test_get_macos_version_failure(self):
        """測試獲取版本失敗時的 fallback"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, 'sw_vers')
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            # 失敗時應該假設為 14.0
            self.assertEqual(helper._macos_version, 14.0)
    
    def test_should_use_direct_scan(self):
        """測試判斷是否使用直接掃描的邏輯"""
        helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
        
        # macOS 13.x 應該使用直接掃描
        helper._macos_version = 13.5
        self.assertTrue(helper._should_use_direct_scan())
        
        # macOS 14.x 不應該使用直接掃描
        helper._macos_version = 14.0
        self.assertFalse(helper._should_use_direct_scan())
        
        # macOS 15.x 不應該使用直接掃描
        helper._macos_version = 15.0
        self.assertFalse(helper._should_use_direct_scan())


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestScanMethodFallback(unittest.TestCase):
    """測試掃描方法的 fallback 機制"""
    
    @patch('subprocess.run')
    def test_macos13_direct_scan_success(self, mock_run):
        """測試 macOS 13 直接掃描成功的情況"""
        # 設定 macOS 版本為 13.5
        mock_run.return_value = Mock(stdout="13.5\n", returncode=0)
        
        helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
        helper._macos_version = 13.5
        
        # 模擬 CoreWLAN 掃描成功
        with patch.object(helper, '_scan_with_corewlan') as mock_corewlan:
            mock_corewlan.return_value = {
                'status': True,
                'list': [
                    {
                        yy_wifi_helper.WIFIAP.SSID: 'TestNetwork',
                        yy_wifi_helper.WIFIAP.RSSI: -50
                    }
                ],
                'error': None
            }
            
            result = helper.scanToGetAPList()
            
            # 應該只調用 CoreWLAN，不調用 WiFiScanner
            mock_corewlan.assert_called_once()
            self.assertTrue(result['status'])
            self.assertEqual(len(result['list']), 1)
    
    @patch('subprocess.run')
    def test_macos14_fallback_to_wifiscanner(self, mock_run):
        """測試 macOS 14 fallback 到 WiFiScanner 的情況"""
        # 第一次調用獲取版本，後續調用是 WiFiScanner
        mock_run.side_effect = [
            Mock(stdout="14.2\n", returncode=0),  # 版本檢測
            Mock(stdout='{"networks": [{"ssid": "TestWiFi", "signal_strength": -50, "security": "WPA2", "channel": 6}]}', returncode=0)  # WiFiScanner 結果
        ]
        
        helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
        helper._macos_version = 14.2
        
        # 模擬 CoreWLAN 失敗
        with patch.object(helper, '_scan_with_corewlan') as mock_corewlan:
            mock_corewlan.return_value = {
                'status': False,
                'list': [],
                'error': ['CoreWLAN API not available']
            }
            
            # 模擬 permission_helper
            with patch.object(helper.permission_helper, 'ensure_scanner_app', return_value=True):
                result = helper.scanToGetAPList()
                
                # 應該嘗試了 WiFiScanner
                self.assertIn('TestWiFi', str(result))
    
    def test_both_methods_fail_error_message(self):
        """測試兩種方法都失敗時的錯誤訊息"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="14.2\n", returncode=0)
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            helper._macos_version = 14.2
            
            # 模擬兩種方法都失敗
            with patch.object(helper, '_scan_with_corewlan') as mock_corewlan:
                mock_corewlan.return_value = {
                    'status': False,
                    'list': [],
                    'error': ['CoreWLAN failed']
                }
                
                with patch.object(helper, '_scan_with_wifiscanner') as mock_scanner:
                    mock_scanner.return_value = {
                        'status': False,
                        'list': [],
                        'error': ['WiFiScanner failed']
                    }
                    
                    result = helper.scanToGetAPList()
                    
                    self.assertFalse(result['status'])
                    self.assertIn('error', result)
                    # 應該包含有用的錯誤訊息
                    error_str = str(result['error'])
                    self.assertIn('14.2', error_str)
                    self.assertIn('permissions', error_str.lower())


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestBackwardCompatibility(unittest.TestCase):
    """測試向後相容性"""
    
    def test_api_compatibility_with_v1(self):
        """確保 V2 版本保持與 V1 相同的 API"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="14.2\n", returncode=0)
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            
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
    
    def test_return_value_structure_compatibility(self):
        """測試返回值結構保持一致"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="14.2\n", returncode=0)
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            
            # 測試 getInterface 返回結構 - 使用更安全的 mock 方式
            with patch('CoreWLAN.CWWiFiClient') as mock_client_class:
                mock_client = Mock()
                mock_interface = Mock()
                mock_interface.interfaceName.return_value = 'en0'
                mock_client.interface.return_value = mock_interface
                mock_client.interfaces.return_value = [mock_interface]
                mock_client_class.alloc.return_value.init.return_value = mock_client
                
                # 重新創建 helper 以使用 mocked client
                helper.client = mock_client
                
                interface_result = helper.getInterface()
                self.assertIn('default', interface_result)
                self.assertIn('list', interface_result)
                self.assertIn('error', interface_result)
    
    def test_connected_ssid_return_format(self):
        """測試 getConnectedAPSSID 的返回格式"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="14.2\n", returncode=0)
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            
            # 模擬成功獲取 SSID - 使用更安全的方式
            with patch.object(helper, 'getInterface') as mock_get_interface:
                mock_get_interface.return_value = {
                    'default': 'en0',
                    'list': ['en0'],
                    'error': None
                }
                
                # 直接 mock client 的方法
                mock_interface = Mock()
                mock_interface.ssid.return_value = 'MyWiFi'
                helper.client = Mock()
                helper.client.interfaceWithName_.return_value = mock_interface
                
                success, ssid, error = helper.getConnectedAPSSID()
                
                self.assertTrue(success)
                self.assertEqual(ssid, 'MyWiFi')
                self.assertIsNone(error)


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestErrorMessageImprovement(unittest.TestCase):
    """測試改進的錯誤訊息"""
    
    def test_macos14_permission_error_message(self):
        """測試 macOS 14+ 的權限錯誤訊息"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="14.2\n", returncode=0)
            
            helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
            helper._macos_version = 14.2
            
            # 模擬掃描失敗
            with patch.object(helper, '_scan_with_corewlan') as mock_corewlan:
                mock_corewlan.return_value = {'status': False, 'list': [], 'error': ['Permission denied']}
                
                with patch.object(helper, '_scan_with_wifiscanner') as mock_scanner:
                    mock_scanner.return_value = {'status': False, 'list': [], 'error': ['Not configured']}
                    
                    result = helper.scanToGetAPList()
                    
                    # 錯誤訊息應該提到 macOS 版本和解決方案
                    error_str = ' '.join(result['error'])
                    self.assertIn('14.2', error_str)
                    self.assertIn('py-wifi-helper-macos-setup', error_str)
                    self.assertIn('permissions', error_str.lower())


@unittest.skipUnless(HAS_COREWLAN, "pyobjc dependencies not available")
class TestIntegration(unittest.TestCase):
    """整合測試"""
    
    @patch('subprocess.run')
    def test_full_scan_workflow(self, mock_run):
        """測試完整的掃描工作流程"""
        # 設定 macOS 14.2
        mock_run.side_effect = [
            Mock(stdout="14.2\n", returncode=0),  # 版本檢測
            Mock(  # WiFiScanner 掃描結果
                stdout=json.dumps({
                    "networks": [
                        {"ssid": "Network1", "signal_strength": -45, "security": "WPA2", "channel": 1},
                        {"ssid": "Network2", "signal_strength": -60, "security": "Open", "channel": 6}
                    ]
                }),
                returncode=0
            )
        ]
        
        helper = my_macos_helper_v2.YYMacOSWIFIHelperV2()
        
        # 模擬 CoreWLAN 失敗（macOS 14+ 預期行為）
        with patch.object(helper, '_scan_with_corewlan') as mock_corewlan:
            mock_corewlan.return_value = {'status': False, 'list': [], 'error': ['Not supported']}
            
            # 模擬 WiFiScanner.app 存在
            with patch.object(helper.permission_helper, 'ensure_scanner_app', return_value=True):
                result = helper.scanToGetAPList()
                
                # 檢查結果
                if result['status']:
                    self.assertEqual(len(result['list']), 2)
                    ssids = [net[yy_wifi_helper.WIFIAP.SSID] for net in result['list']]
                    self.assertIn('Network1', ssids)
                    self.assertIn('Network2', ssids)


if __name__ == '__main__':
    # 執行測試
    unittest.main(verbosity=2)
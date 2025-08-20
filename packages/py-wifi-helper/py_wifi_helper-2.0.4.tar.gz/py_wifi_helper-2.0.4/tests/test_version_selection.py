#!/usr/bin/env python3
"""
測試版本選擇功能（不需要 pyobjc 依賴）
"""
import unittest
import sys
import os
import platform

# Only run these tests on macOS
if platform.system() != 'Darwin':
    print("Skipping macOS tests on non-Darwin platform")
    sys.exit(0)

sys.path.insert(0, '../')
from py_wifi_helper.my_macos_helper import get_helper_version


class TestVersionSelection(unittest.TestCase):
    """測試版本選擇邏輯（不依賴 pyobjc）"""
    
    def setUp(self):
        """保存原始環境變數"""
        self.original_env = os.environ.get('PY_WIFI_HELPER_USE_V1', None)
    
    def tearDown(self):
        """恢復原始環境變數"""
        if self.original_env is not None:
            os.environ['PY_WIFI_HELPER_USE_V1'] = self.original_env
        else:
            os.environ.pop('PY_WIFI_HELPER_USE_V1', None)
    
    def test_default_version_is_v2(self):
        """測試預設版本是 V2"""
        # 清除環境變數
        os.environ.pop('PY_WIFI_HELPER_USE_V1', None)
        
        version = get_helper_version()
        self.assertEqual(version, 'v2')
    
    def test_environment_variable_v1_true(self):
        """測試環境變數設為 true 時使用 V1"""
        os.environ['PY_WIFI_HELPER_USE_V1'] = 'true'
        
        version = get_helper_version()
        self.assertEqual(version, 'v1')
    
    def test_environment_variable_v1_1(self):
        """測試環境變數設為 1 時使用 V1"""
        os.environ['PY_WIFI_HELPER_USE_V1'] = '1'
        
        version = get_helper_version()
        self.assertEqual(version, 'v1')
    
    def test_environment_variable_v1_yes(self):
        """測試環境變數設為 yes 時使用 V1"""
        os.environ['PY_WIFI_HELPER_USE_V1'] = 'yes'
        
        version = get_helper_version()
        self.assertEqual(version, 'v1')
    
    def test_environment_variable_v1_false(self):
        """測試環境變數設為 false 時使用 V2"""
        os.environ['PY_WIFI_HELPER_USE_V1'] = 'false'
        
        version = get_helper_version()
        self.assertEqual(version, 'v2')
    
    def test_environment_variable_v1_0(self):
        """測試環境變數設為 0 時使用 V2"""
        os.environ['PY_WIFI_HELPER_USE_V1'] = '0'
        
        version = get_helper_version()
        self.assertEqual(version, 'v2')
    
    def test_environment_variable_case_insensitive(self):
        """測試環境變數不區分大小寫"""
        os.environ['PY_WIFI_HELPER_USE_V1'] = 'TRUE'
        
        version = get_helper_version()
        self.assertEqual(version, 'v1')
        
        os.environ['PY_WIFI_HELPER_USE_V1'] = 'False'
        
        version = get_helper_version()
        self.assertEqual(version, 'v2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
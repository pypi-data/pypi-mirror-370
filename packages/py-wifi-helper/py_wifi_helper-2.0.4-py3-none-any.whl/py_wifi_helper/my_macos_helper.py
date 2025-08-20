# -*- encoding: utf-8 -*-
"""
macOS WiFi Helper 統一入口點

此模組提供統一的 macOS WiFi 助手介面，支援兩個版本：
- V2（預設）：改進版，具有版本檢測和智慧 fallback
- V1（相容）：原始版本，穩定可靠

使用方式：
1. 環境變數：PY_WIFI_HELPER_USE_V1=true
2. 程式碼：create_macos_helper(use_v1=True)
"""

import os
import logging

def create_macos_helper(use_v1=None, debug=False):
    """
    建立 macOS WiFi Helper
    
    Args:
        use_v1 (bool, optional): 強制使用 V1，None 表示使用預設邏輯
        debug (bool): 啟用除錯模式
    
    Returns:
        YYMacOSWIFIHelper: WiFi helper 實例
    """
    if use_v1 is None:
        # 檢查環境變數
        use_v1 = os.getenv('PY_WIFI_HELPER_USE_V1', 'false').lower() in ['true', '1', 'yes']
    
    logger = logging.getLogger(__name__)
    
    if use_v1:
        if debug:
            logger.info("🔄 Using macOS WiFi Helper V1 (compatibility mode)")
        try:
            from .my_macos_helper_v1 import YYMacOSWIFIHelper
        except ImportError:
            import my_macos_helper_v1
            YYMacOSWIFIHelper = my_macos_helper_v1.YYMacOSWIFIHelper
        return YYMacOSWIFIHelper()
    else:
        if debug:
            logger.info("🚀 Using macOS WiFi Helper V2 (enhanced mode)")
        try:
            from .my_macos_helper_v2 import YYMacOSWIFIHelperV2
        except ImportError:
            import my_macos_helper_v2
            YYMacOSWIFIHelperV2 = my_macos_helper_v2.YYMacOSWIFIHelperV2
        return YYMacOSWIFIHelperV2()

def get_helper_version():
    """
    獲取當前使用的 helper 版本
    
    Returns:
        str: "v1" 或 "v2"
    """
    use_v1 = os.getenv('PY_WIFI_HELPER_USE_V1', 'false').lower() in ['true', '1', 'yes']
    return "v1" if use_v1 else "v2"

# 向後相容性：提供舊的類別名稱
# 預設使用 V2，但可透過環境變數切換
class YYMacOSWIFIHelper:
    """
    macOS WiFi Helper 向後相容包裝器
    
    此類別會根據設定自動選擇 V1 或 V2 實作
    """
    
    def __new__(cls):
        # 根據設定回傳對應的實例
        return create_macos_helper()

# 明確匯出兩個版本的類別名稱
def get_v1_helper():
    """獲取 V1 版本的 helper"""
    try:
        from .my_macos_helper_v1 import YYMacOSWIFIHelper as V1Helper
    except ImportError:
        import my_macos_helper_v1
        V1Helper = my_macos_helper_v1.YYMacOSWIFIHelper
    return V1Helper()

def get_v2_helper():
    """獲取 V2 版本的 helper"""
    try:
        from .my_macos_helper_v2 import YYMacOSWIFIHelperV2 as V2Helper
    except ImportError:
        import my_macos_helper_v2
        V2Helper = my_macos_helper_v2.YYMacOSWIFIHelperV2
    return V2Helper()

# 延遲載入 CoreWLAN Helper，避免啟動時 import 錯誤
def _get_corewlan_helper():
    """延遲載入 CoreWLAN Helper"""
    try:
        from .my_macos_helper_v1 import YYMacOSCoreWLANHelper
        return YYMacOSCoreWLANHelper
    except ImportError:
        try:
            import my_macos_helper_v1
            return my_macos_helper_v1.YYMacOSCoreWLANHelper
        except ImportError:
            return None

# 提供向後相容的存取方式
class _CoreWLANHelperProxy:
    def __new__(cls):
        helper_class = _get_corewlan_helper()
        if helper_class:
            return helper_class()
        else:
            raise ImportError("CoreWLAN dependencies not available")

YYMacOSCoreWLANHelper = _CoreWLANHelperProxy

# 主要匯出
__all__ = [
    'YYMacOSWIFIHelper',
    'YYMacOSCoreWLANHelper', 
    'create_macos_helper',
    'get_helper_version',
    'get_v1_helper',
    'get_v2_helper'
]
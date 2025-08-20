import os
import sys
import argparse
import logging
from .macos_wifi_permission_helper import MacOSWiFiPermissionHelper
from .config import WiFiScannerConfig

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s'
    )

def handle_macos_permission(force=False, debug=False, target_path=None):
    setup_logging(debug)
    
    config = WiFiScannerConfig()
    
    if target_path is None:
        default_path = config.scanner_app_path or os.getcwd()
        user_input = input(f"Enter path for WiFiScanner.app [default: {default_path}]: ").strip()
        target_path = user_input if user_input else default_path

    # 確保路徑是絕對路徑
    target_path = os.path.expanduser(target_path)
    config.scanner_app_path = target_path
    
    helper = MacOSWiFiPermissionHelper(debug=debug, app_path=target_path)
    
    logging.info("Checking macOS WiFi permissions...")
    if not force and helper.check_permissions():
        logging.info("✓ WiFi scanning permissions are already granted")
        return 0

    logging.info("× WiFi scanning permissions not found")
    logging.info(f"\nGenerating WiFiScanner.app at: {target_path}")
    
    if not helper.ensure_scanner_app(force):
        logging.error("\n× Failed to generate WiFiScanner.app")
        return 1

    logging.info("\nInitiating permission request...")
    if not helper.request_permissions():
        logging.error("\n× Failed to complete permission setup")
        logging.error("Please try running 'py-wifi-helper-macos-setup' again")
        return 1

    if not helper.check_permissions():
        logging.error("\n× Permission verification failed")
        logging.error("If you haven't seen the permission request:")
        logging.error("1. Try running 'py-wifi-helper-macos-setup' again")
        logging.error("2. Or manually enable Location Services for WiFiScanner in System Settings")
        return 1

    logging.info("\n✓ Setup completed successfully!")
    logging.info("You can now use 'py-wifi-helper --action scan' to scan for networks")
    return 0

def main():
    parser = argparse.ArgumentParser(description='macOS WiFi Permission Setup')
    parser.add_argument('--force', action='store_true', 
                      help='Force regenerate WiFiScanner.app')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    parser.add_argument('--target-path', 
                      help='Target path for WiFiScanner.app')
    args = parser.parse_args()
    
    if sys.platform != 'darwin':
        print("This command is only for macOS systems")
        return 1
        
    try:
        return handle_macos_permission(args.force, args.debug, args.target_path)
    except KeyboardInterrupt:
        print("\n× Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n× Setup failed with error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

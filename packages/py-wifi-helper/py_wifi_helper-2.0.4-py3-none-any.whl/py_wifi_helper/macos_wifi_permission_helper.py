import os
import subprocess
import json
from pathlib import Path
import time
import logging
import sys
import traceback

class MacOSWiFiPermissionHelper:
    def __init__(self, app_name="WiFiScanner", debug=False, app_path=None):
        """Initialize the WiFi permission helper."""
        self.debug = debug
        
        # 設定 app 路徑
        if app_path:
            self.app_path = Path(os.path.expanduser(app_path))
            if self.app_path.name.endswith('.app'):
                self.app_name = self.app_path.stem  # 從路徑獲取名稱
            else:
                self.app_name = app_name
                self.app_path = self.app_path / f"{app_name}.app"
        else:
            self.app_name = app_name
            self.app_path = Path(os.getcwd()) / f"{app_name}.app"
            
        # 確保父目錄存在
        self.app_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.cli_path = self.app_path / "Contents/MacOS/wifiscan"
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    def ensure_scanner_app(self, force=False):
        """Ensure WiFiScanner.app exists and is properly signed."""
        try:
            if self.debug:
                self.logger.debug(f"Expected app path: {self.app_path}")
                self.logger.debug(f"Current working directory: {os.getcwd()}")
            
            if force and self.app_path.exists():
                if self.debug:
                    self.logger.debug(f"Removing existing app at: {self.app_path}")
                import shutil
                shutil.rmtree(self.app_path)
            
            if not self.app_path.exists():
                if self.debug:
                    self.logger.debug("Generating new app...")
                    
                from .macos_app_generator import generate_app
                success, message = generate_app(
                    self.app_name,
                    quiet=not self.debug,
                    target_dir=str(self.app_path),  # 直接傳遞完整的 .app 路徑
                    debug=self.debug
                )
                
                if not success:
                    self.logger.error(f"App generation failed: {message}")
                    return False
                
                if not self.app_path.exists():
                    self.logger.error(f"App was not created at: {self.app_path}")
                    if self.debug:
                        self.logger.debug(f"Directory writable: {os.access(self.app_path.parent, os.W_OK)}")
                        self.logger.debug(f"Directory listing: {os.listdir(self.app_path.parent)}")
                    return False
            
            if self.debug:
                self.logger.debug(f"App exists: {self.app_path.exists()}")
                self.logger.debug(f"CLI exists: {self.cli_path.exists()}")
            
            return self.app_path.exists() and self.cli_path.exists()
            
        except Exception as e:
            self.logger.error(f"Failed to generate scanner app: {e}")
            if self.debug:
                self.logger.debug(traceback.format_exc())
            return False

    def check_permissions(self):
        """Check if we have required permissions by attempting a scan."""
        if not self.cli_path.exists():
            if self.debug:
                self.logger.debug(f"CLI tool not found at: {self.cli_path}")
            return False
            
        try:
            result = subprocess.run(
                [str(self.cli_path), '--json'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            try:
                data = json.loads(result.stdout)
                has_networks = 'networks' in data and len(data['networks']) > 0
                if self.debug:
                    self.logger.debug(f"Scan result: {has_networks}, networks count: {len(data.get('networks', []))}")
                return has_networks
            except json.JSONDecodeError:
                if self.debug:
                    self.logger.debug(f"Failed to parse JSON response: {result.stdout}")
                return False
                
        except subprocess.CalledProcessError as e:
            if self.debug:
                self.logger.debug(f"Command failed: {e}")
            return False
        except Exception as e:
            if self.debug:
                self.logger.debug(f"Permission check failed: {e}")
            return False
    
    def request_permissions(self):
        """Request WiFi scanning permissions by opening the app."""
        if not self.app_path.exists():
            self.logger.error("WiFiScanner.app not found")
            if self.debug:
                self.logger.debug(f"Expected path: {self.app_path}")
            return False
            
        try:
            self.logger.info("\nOpening WiFiScanner.app to request permissions...")
            result = subprocess.run(['open', str(self.app_path)], 
                                  capture_output=True, 
                                  text=True,
                                  check=True)
            
            if self.debug:
                self.logger.debug(f"Open command output: {result.stdout}")
            
            self.logger.info("\nPlease check your notification center for permission requests.")
            self.logger.info("You might need to:")
            self.logger.info("1. Allow Location Services access when prompted")
            self.logger.info("2. Go to System Settings > Privacy & Security > Location Services")
            self.logger.info("3. Find and enable WiFiScanner in the list")
            
            self.logger.info("\nWaiting for permission response...")
            for i in range(6):  # 30 seconds total
                if self.check_permissions():
                    self.logger.info("\n✓ Permissions successfully granted!")
                    return True
                if i < 5:
                    self.logger.info("Still waiting for permissions... (press Ctrl+C to cancel)")
                time.sleep(5)
            
            self.logger.info("\n× Permission request timed out")
            self.logger.info("If you haven't seen the permission request:")
            self.logger.info("1. Try running 'py-wifi-helper-macos-setup --force'")
            self.logger.info("2. Or manually enable Location Services for WiFiScanner in System Settings")
            return False
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"\n× Error opening WiFiScanner.app: {e}")
            if self.debug:
                self.logger.debug(f"Command output: {e.output if hasattr(e, 'output') else 'No output'}")
            return False
        except KeyboardInterrupt:
            self.logger.info("\n× Setup cancelled by user")
            self.logger.info("You can run 'py-wifi-helper-macos-setup' again at any time")
            return False
        except Exception as e:
            self.logger.error(f"\n× Unexpected error: {e}")
            if self.debug:
                self.logger.debug(traceback.format_exc())
            return False

    def scan_wifi(self):
        """Scan WiFi networks using the CLI tool."""
        if not self.cli_path.exists():
            self.logger.error("WiFiScanner CLI tool not found")
            return None
            
        try:
            result = subprocess.run(
                [str(self.cli_path), '--json'],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Scan failed: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse scan results: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during scan: {e}")
            if self.debug:
                self.logger.debug(traceback.format_exc())
            return None

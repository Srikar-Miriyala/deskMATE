import webbrowser
import os
import platform
import subprocess
from typing import Dict, Any

class SystemControlPlugin:
    """Plugin for system automation tasks like opening URLs, apps, and files"""
    
    def __init__(self):
        self.system = platform.system()
        
    def open_url(self, url: str) -> Dict[str, Any]:
        """Open a URL in the default browser with smart fallback"""
        try:
            # Smart URL Registry
            url_map = {
                "gemini": "https://gemini.google.com",
                "chatgpt": "https://chat.openai.com",
                "perplexity": "https://perplexity.ai",
                "claude": "https://claude.ai",
                "youtube": "https://youtube.com",
                "google": "https://google.com",
                "amazon": "https://www.amazon.in", # Updated to .in for India
                "netflix": "https://netflix.com",
                "github": "https://github.com",
                "stackoverflow": "https://stackoverflow.com",
                "woxsen": "https://woxsen.edu.in",
                "gmail": "https://mail.google.com",
                "whatsapp": "https://web.whatsapp.com",
                "spotify": "https://open.spotify.com",
            }
            
            # Search Query Templates
            search_templates = {
                "google": "https://www.google.com/search?q={}",
                "youtube": "https://www.youtube.com/results?search_query={}",
                "amazon": "https://www.amazon.in/s?k={}", # Updated to .in
                "bing": "https://www.bing.com/search?q={}",
                "duckduckgo": "https://duckduckgo.com/?q={}",
                "github": "https://github.com/search?q={}",
                "stackoverflow": "https://stackoverflow.com/search?q={}",
                "perplexity": "https://www.perplexity.ai/search?q={}",
            }

            url_lower = url.lower().strip()
            
            # 1. Check exact map
            if url_lower in url_map:
                final_url = url_map[url_lower]
            # 2. Check if it's a "search X on Y" pattern handled by the caller, 
            #    but if passed as a raw string like "amazon search iphone", try to parse
            elif "search" in url_lower and any(k in url_lower for k in search_templates):
                # Simple heuristic: find which platform and what query
                for platform, template in search_templates.items():
                    if platform in url_lower:
                        # Strip common words to get clean query
                        query = url_lower.replace(platform, "").replace("search", "").replace("for", "").replace("on", "").strip()
                        final_url = template.format(query.replace(" ", "+"))
                        break
                else:
                    final_url = url # Fallback
            # 3. Check if it's a "play X on Y" pattern (specifically for YouTube)
            elif "play" in url_lower and "youtube" in url_lower:
                 query = url_lower.replace("youtube", "").replace("play", "").replace("on", "").strip()
                 final_url = search_templates["youtube"].format(query.replace(" ", "+"))
            # 4. Check if it's a valid URL
            elif url.startswith(('http://', 'https://')):
                final_url = url
            # 5. Assume it's a domain if it has a dot
            elif '.' in url:
                final_url = 'https://' + url
            # 6. Fallback: Google Search or Direct Map
            else:
                # Try to guess domain
                final_url = f"https://{url}.com"

            print(f"🌐 Opening: {final_url}")
            webbrowser.open(final_url)
            
            return {
                "success": True,
                "output": f"Opened: {final_url}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Failed to open URL: {str(e)}"
            }

    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Open a common application"""
        try:
            app_map = {
                'chrome': 'chrome',
                'notepad': 'notepad',
                'calc': 'calc',
                'calculator': 'calc',
                'explorer': 'explorer',
                'file explorer': 'explorer', # Added alias
                'cmd': 'cmd',
                'powershell': 'powershell',
                'code': 'code',
                'vscode': 'code',
                'spotify': 'spotify',
                'discord': 'discord',
                'slack': 'slack',
                'teams': 'msteams',
                'word': 'winword',
                'excel': 'excel',
                'powerpoint': 'powerpnt'
            }
            
            cmd = app_map.get(app_name.lower(), app_name)
            
            if self.system == 'Windows':
                subprocess.Popen(f"start {cmd}", shell=True)
            elif self.system == 'Darwin': # macOS
                subprocess.Popen(['open', '-a', cmd])
            else: # Linux
                subprocess.Popen([cmd])
                
            return {
                "success": True,
                "output": f"Launched application: {app_name}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Failed to open application: {str(e)}"
            }

    def open_file_explorer(self, path: str = None) -> Dict[str, Any]:
        """Open file explorer at specific path"""
        try:
            if path is None or path == ".":
                path = os.path.expanduser("~")
            
            path = os.path.abspath(path)
            if not os.path.exists(path):
                return {
                    "success": False,
                    "output": None,
                    "error": f"Path does not exist: {path}"
                }

            if self.system == 'Windows':
                os.startfile(path)
            elif self.system == 'Darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
                
            return {
                "success": True,
                "output": f"Opened file explorer at: {path}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Failed to open file explorer: {str(e)}"
            }

    def create_folder(self, path: str) -> Dict[str, Any]:
        """Create a new folder with explicit path feedback"""
        try:
            # Handle absolute paths vs relative paths
            if not os.path.isabs(path):
                # Default to Desktop for relative paths, fallback to Home if Desktop not found
                home = os.path.expanduser("~")
                desktop = os.path.join(home, "Desktop")
                base_dir = desktop if os.path.exists(desktop) else home
                
                final_path = os.path.join(base_dir, path)
            else:
                final_path = path
            
            # Normalize path separators
            final_path = os.path.normpath(final_path)
            
            os.makedirs(final_path, exist_ok=True)
            
            return {
                "success": True,
                "output": f"Created folder at: {final_path}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Failed to create folder: {str(e)}"
            }

    def create_file(self, path: str, content: str = "") -> Dict[str, Any]:
        """Create a new file with explicit path feedback"""
        try:
            if not path or path.strip() == "":
                path = "new_file.txt"
                
            if not os.path.isabs(path):
                home = os.path.expanduser("~")
                desktop = os.path.join(home, "Desktop")
                base_dir = desktop if os.path.exists(desktop) else home
                
                final_path = os.path.join(base_dir, path)
            else:
                final_path = path
                
            final_path = os.path.normpath(final_path)
            
            # Check if final_path is a directory
            if os.path.isdir(final_path):
                final_path = os.path.join(final_path, "new_file.txt")
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
                
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {
                "success": True,
                "output": f"Created file at: {final_path}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Failed to create file: {str(e)}"
            }

    def open_terminal(self, path: str = None) -> Dict[str, Any]:
        """Open a new terminal window"""
        try:
            if path is None:
                path = os.path.expanduser("~")
                
            if self.system == 'Windows':
                # Use start cmd /K to keep window open
                subprocess.Popen(f'start cmd /K "cd /d {path}"', shell=True)
            elif self.system == 'Darwin':
                subprocess.Popen(['open', '-a', 'Terminal', path])
            else:
                subprocess.Popen(['gnome-terminal', '--working-directory', path])
                
            return {
                "success": True,
                "output": f"Opened terminal at {path}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Failed to open terminal: {str(e)}"
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information including RAM, storage, CPU"""
        try:
            import sys
            import shutil
            
            # Detect Windows 11 properly
            os_name = platform.system()
            os_release = platform.release()
            os_version = platform.version()
            
            # Windows 11 detection: Check build number
            if os_name == "Windows" and os_release == "10":
                # Windows 11 has build number >= 22000
                build_number = int(os_version.split('.')[-1]) if os_version else 0
                if build_number >= 22000:
                    os_display = "Windows 11"
                else:
                    os_display = "Windows 10"
            else:
                os_display = f"{os_name} {os_release}"
            
            # Get processor info
            machine = platform.machine()
            processor = platform.processor()
            
            # Simplify processor name if too long
            if len(processor) > 50:
                processor = processor.split(',')[0]
            
            # Try to get detailed info with psutil
            try:
                import psutil
                
                # CPU info
                cpu_count = psutil.cpu_count(logical=False)  # Physical cores
                cpu_count_logical = psutil.cpu_count(logical=True)  # Logical cores
                cpu_freq = psutil.cpu_freq()
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # RAM info
                ram = psutil.virtual_memory()
                ram_total_gb = ram.total / (1024**3)
                ram_used_gb = ram.used / (1024**3)
                ram_available_gb = ram.available / (1024**3)
                ram_percent = ram.percent
                
                # Storage info (C: drive on Windows, / on Unix)
                disk_path = "C:\\" if os_name == "Windows" else "/"
                disk = psutil.disk_usage(disk_path)
                disk_total_gb = disk.total / (1024**3)
                disk_used_gb = disk.used / (1024**3)
                disk_free_gb = disk.free / (1024**3)
                disk_percent = disk.percent
                
                info = {
                    "system": os_display,
                    "release": os_release,
                    "version": os_version,
                    "machine": machine,
                    "processor": processor,
                    "python_version": platform.python_version(),
                    "architecture": "64-bit" if sys.maxsize > 2**32 else "32-bit",
                    "cpu": {
                        "cores": cpu_count,
                        "logical_cores": cpu_count_logical,
                        "frequency_mhz": round(cpu_freq.current) if cpu_freq else 0,
                        "max_frequency_mhz": round(cpu_freq.max) if cpu_freq else 0,
                        "usage_percent": round(cpu_percent, 1)
                    },
                    "ram": {
                        "total_gb": round(ram_total_gb, 2),
                        "used_gb": round(ram_used_gb, 2),
                        "available_gb": round(ram_available_gb, 2),
                        "percent": round(ram_percent, 1)
                    },
                    "storage": {
                        "drive": disk_path,
                        "total_gb": round(disk_total_gb, 2),
                        "used_gb": round(disk_used_gb, 2),
                        "free_gb": round(disk_free_gb, 2),
                        "percent": round(disk_percent, 1)
                    }
                }
            except ImportError:
                # Fallback if psutil not available
                info = {
                    "system": os_display,
                    "release": os_release,
                    "version": os_version,
                    "machine": machine,
                    "processor": processor,
                    "python_version": platform.python_version(),
                    "architecture": "64-bit" if sys.maxsize > 2**32 else "32-bit",
                    "note": "Install psutil for detailed RAM/CPU/Storage info"
                }
            
            return {
                "success": True,
                "output": info,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Failed to get system info: {str(e)}"
            }

    def get_time(self) -> Dict[str, Any]:
        """Get current local time"""
        from datetime import datetime
        now = datetime.now()
        return {
            "success": True,
            "output": now.strftime("%Y-%m-%d %H:%M:%S"),
            "error": None
        }

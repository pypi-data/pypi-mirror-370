"""
Core functionality for ModelSensor
"""

import os
import platform
import psutil
import socket
import time
import datetime
import json
import subprocess
import sys
from typing import Dict, Any, Optional
import requests
from pathlib import Path


class ModelSensor:
    """Main class for detecting system information and environment"""
    
    def __init__(self):
        self.data = {}
        
    def get_time_info(self) -> Dict[str, Any]:
        """Get current time information"""
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        
        return {
            "current_time": now.isoformat(),
            "utc_time": utc_now.isoformat(),
            "timestamp": int(time.time()),
            "timezone": str(now.astimezone().tzinfo),
            "weekday": now.strftime("%A"),
            "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_location_info(self) -> Dict[str, Any]:
        """Get approximate location information using IP geolocation"""
        try:
            # Try to get public IP
            ip_response = requests.get("https://api.ipify.org", timeout=5)
            public_ip = ip_response.text
            
            # Get location from IP
            geo_response = requests.get(f"http://ip-api.com/json/{public_ip}", timeout=5)
            geo_data = geo_response.json()
            
            if geo_data.get("status") == "success":
                return {
                    "public_ip": public_ip,
                    "country": geo_data.get("country"),
                    "country_code": geo_data.get("countryCode"),
                    "region": geo_data.get("regionName"),
                    "city": geo_data.get("city"),
                    "latitude": geo_data.get("lat"),
                    "longitude": geo_data.get("lon"),
                    "timezone": geo_data.get("timezone"),
                    "isp": geo_data.get("isp")
                }
        except Exception as e:
            return {
                "error": f"Unable to detect location: {str(e)}",
                "public_ip": "unknown"
            }
        
        return {"error": "Location detection failed"}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system configuration information"""
        uname = platform.uname()
        
        return {
            "system": uname.system,
            "node_name": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor,
            "platform": platform.platform(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "architecture": platform.architecture(),
            "hostname": socket.gethostname(),
            "user": os.getenv("USER") or os.getenv("USERNAME") or "unknown"
        }
    
    def get_resource_info(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk information
        if platform.system() == "Windows":
            disk_usage = psutil.disk_usage('C:\\')
        else:
            disk_usage = psutil.disk_usage('/')
        
        # Network information
        network_io = psutil.net_io_counters()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "physical_cores": psutil.cpu_count(logical=False),
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None
                } if cpu_freq else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percentage": memory.percent,
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2)
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "percentage": swap.percent
            },
            "disk": {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percentage": (disk_usage.used / disk_usage.total) * 100,
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2)
            },
            "network": {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            }
        }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment and runtime information"""
        import tempfile
        
        env_info = {
            "working_directory": os.getcwd(),
            "home_directory": str(Path.home()),
            "temp_directory": tempfile.gettempdir(),
            "path_separator": os.pathsep,
            "line_separator": os.linesep,
            "environment_variables": dict(os.environ),
            "shell": os.getenv("SHELL") or os.getenv("COMSPEC") or "unknown"
        }
        
        # Try to detect if running in various environments
        runtime_context = {
            "is_docker": os.path.exists("/.dockerenv"),
            "is_virtual_env": hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
            "is_conda": 'conda' in sys.version or 'Continuum' in sys.version,
            "is_jupyter": 'ipykernel' in sys.modules,
            "is_colab": 'google.colab' in sys.modules
        }
        
        env_info["runtime_context"] = runtime_context
        
        return env_info
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        interfaces = []
        
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            interface_info = {
                "name": interface_name,
                "addresses": []
            }
            
            for address in interface_addresses:
                addr_info = {
                    "family": str(address.family),
                    "address": address.address,
                    "netmask": address.netmask,
                    "broadcast": address.broadcast
                }
                interface_info["addresses"].append(addr_info)
            
            interfaces.append(interface_info)
        
        return {
            "interfaces": interfaces,
            "default_gateway": self._get_default_gateway()
        }
    
    def _get_default_gateway(self) -> Optional[str]:
        """Get default gateway IP address"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["route", "print", "0.0.0.0"], 
                                      capture_output=True, text=True)
                # Parse Windows route output
                for line in result.stdout.split('\n'):
                    if '0.0.0.0' in line and 'Gateway' not in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
            else:
                result = subprocess.run(["ip", "route", "show", "default"], 
                                      capture_output=True, text=True)
                if result.stdout:
                    parts = result.stdout.split()
                    if "via" in parts:
                        return parts[parts.index("via") + 1]
        except Exception:
            pass
        return None
    
    def collect_all_data(self, include_location: bool = False) -> Dict[str, Any]:
        """Collect all system information"""
        data = {
            "sensor_info": {
                "library": "modelsensor",
                "version": "1.1.1",
                "collection_time": datetime.datetime.now().isoformat()
            },
            "time": self.get_time_info(),
            "system": self.get_system_info(),
            "resources": self.get_resource_info(),
            "environment": self.get_environment_info(),
            "network": self.get_network_info()
        }
        
        if include_location:
            data["location"] = self.get_location_info()
        
        self.data = data
        return data
    
    def to_json(self, indent: int = 2, include_location: bool = False, mode: str = "brief") -> str:
        """Return data as JSON string"""
        if not self.data or (include_location and "location" not in self.data):
            self.collect_all_data(include_location=include_location)
        
        if mode == "full":
            payload = self.data
        else:
            # Build brief payload: only date, time, and (optional) geo coordinates
            time_info = self.data.get("time") or self.get_time_info()
            formatted = time_info.get("formatted_time")
            if formatted and " " in formatted:
                date_part, time_part = formatted.split(" ", 1)
            else:
                current_iso = time_info.get("current_time")
                try:
                    dt = datetime.datetime.fromisoformat(current_iso) if current_iso else datetime.datetime.now()
                except Exception:
                    dt = datetime.datetime.now()
                date_part = dt.strftime("%Y-%m-%d")
                time_part = dt.strftime("%H:%M:%S")
            
            payload = {
                "time": {
                    "date": date_part,
                    "time": time_part
                }
            }
            
            if include_location:
                loc = self.data.get("location") or {}
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if lat is not None and lon is not None:
                    payload["location"] = {"latitude": lat, "longitude": lon}
        
        return json.dumps(payload, indent=indent, ensure_ascii=False)
    
    def to_dict(self, include_location: bool = False, mode: str = "brief") -> Dict[str, Any]:
        """Return data as dictionary"""
        if not self.data or (include_location and "location" not in self.data):
            self.collect_all_data(include_location=include_location)
        
        if mode == "full":
            return self.data
        
        # Build brief dict: only date, time, and (optional) geo coordinates
        time_info = self.data.get("time") or self.get_time_info()
        formatted = time_info.get("formatted_time")
        if formatted and " " in formatted:
            date_part, time_part = formatted.split(" ", 1)
        else:
            current_iso = time_info.get("current_time")
            try:
                dt = datetime.datetime.fromisoformat(current_iso) if current_iso else datetime.datetime.now()
            except Exception:
                dt = datetime.datetime.now()
            date_part = dt.strftime("%Y-%m-%d")
            time_part = dt.strftime("%H:%M:%S")
        
        brief = {
            "time": {
                "date": date_part,
                "time": time_part
            }
        }
        
        if include_location:
            loc = self.data.get("location") or {}
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if lat is not None and lon is not None:
                brief["location"] = {"latitude": lat, "longitude": lon}
        
        return brief
import platform
import psutil
import os
import re
import subprocess
from pynvml import (
    nvmlInit,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetUtilizationRates,
    nvmlDeviceGetCount,
    nvmlDeviceGetMemoryInfo,
    nvmlDeviceGetTemperature,
    nvmlShutdown,
    NVML_TEMPERATURE_GPU,
)


class SystemMonitor:
    def __init__(self):
        """
        Initialize the System Monitor.
        """
        try:
            nvmlInit()  # Initialize NVIDIA Management Library
            self.gpu_available = True
            self.gpu_count = nvmlDeviceGetCount()  # Get the number of GPUs
        except Exception:
            self.gpu_available = False
            self.gpu_count = 0

        # Detect platform (Windows, Linux, macOS, Jetson, etc.)
        self.system = platform.system().lower()
        self.is_jetson = self._detect_jetson()

        # Jetson always have gpu
        if self.is_jetson:
            self.gpu_available = True
            self.gpu_count = 1 


    def get_cpu_usage(self):
        """
        Get CPU usage percentage.
        """
        return psutil.cpu_percent(interval=1)

    def get_cpu_temperature(self):
        """
        Get CPU temperature (if supported).
        """
        try:
            if self.system == "windows":
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")  # Use OpenHardwareMonitor
                    sensors = w.Sensor()
                    cpu_temps = [s.Value for s in sensors if s.SensorType == "Temperature" and "CPU" in s.Name]
                    return cpu_temps[0]
                except Exception:
                    return 0

            elif self.is_jetson:
                # For NVIDIA Jetson, read CPU temperature from thermal zones
                with open("/sys/class/thermal/thermal_zone1/temp", "r") as f:
                    return float(f.read().strip()) / 1000  # Convert millidegree to Celsius
            elif self.system == "darwin":  # macOS
                try:
                    temp = subprocess.check_output(["osx-cpu-temp"], text=True).strip()
                    return float(temp.replace("°C", ""))
                except FileNotFoundError:
                    return {"error": "Install 'osx-cpu-temp' for macOS temperature monitoring"}
                except ValueError:
                    return {"error": "Invalid temperature value retrieved from osx-cpu-temp"}
            else:  # Linux
                sensors = psutil.sensors_temperatures()
                if "coretemp" in sensors:
                    core_temps = sensors["coretemp"]
                    return [temp.current for temp in core_temps if hasattr(temp, "current")]
                elif "cpu-thermal" in sensors:
                    return [sensors["cpu-thermal"][0].current]
                else:
                    return {"error": "CPU temperature sensor not found"}
        except Exception as e:
            return {"error": str(e)}

    def get_ram_usage(self):
        """
        Get refined RAM usage details for macOS.
        """
        memory = psutil.virtual_memory()
        cached_memory = memory.cached if hasattr(memory, "cached") else 0  # Check if cached memory is available

        # Adjust "used" to exclude cached memory on macOS
        adjusted_used = memory.used - cached_memory if self.system == "darwin" else memory.used
        adjusted_free = memory.total - adjusted_used if self.system == "darwin" else memory.available

        return {
            "total": memory.total,
            "used": adjusted_used,
            "free": adjusted_free,
            "percent": round((adjusted_used / memory.total) * 100, 2),
        }

    def get_gpu_usage(self):
        """
        Get usage details for all available GPUs.
        """
        if self.is_jetson:
            return self.get_jetson_gpu_usage()  # Use Jetson-specific method

        if not self.gpu_available:
            return {"error": "GPU monitoring is not supported on this system."}

        gpu_data = []
        try:
            for i in range(self.gpu_count):
                handle = nvmlDeviceGetHandleByIndex(i)
                utilization = nvmlDeviceGetUtilizationRates(handle)
                memory = nvmlDeviceGetMemoryInfo(handle)
                temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)

                gpu_data.append({
                    "gpu_index": i,
                    "gpu_usage_percent": utilization.gpu,
                    "memory_usage_percent": (memory.used / memory.total) * 100 if memory.total > 0 else 0,
                    "temperature_celsius": temperature,
                    "total_memory": memory.total,
                    "used_memory": memory.used,
                    "free_memory": memory.free,
                })
        except Exception as e:
            return {"error": str(e)}

        return gpu_data

    def get_system_usage(self):
        """
        Get combined system usage (CPU, RAM, GPU, and temperatures).
        """
        system_usage = {
            "cpu": {
                "usage_percent": self.get_cpu_usage(),
                "temperature_celsius": self.get_cpu_temperature(),
            },
            "ram": self.get_ram_usage(),
        }

        if self.gpu_available:
            system_usage["gpu"] = self.get_gpu_usage()
        else:
            system_usage["gpu"] = []

        return system_usage

    def print_usage(self):
        """
        Print the system usage details (CPU, RAM, GPU).
        """
        usage = self.get_system_usage()

        # CPU Usage
        print("CPU Usage:")
        print(f"  Usage Percent: {usage['cpu']['usage_percent']}%")
        cpu_temp = usage['cpu']['temperature_celsius']
        if isinstance(cpu_temp, dict) and "error" in cpu_temp:
            print(f"  Temperature: {cpu_temp['error']}")
        else:
            print(f"  Temperature: {cpu_temp}°C")

        # RAM Usage
        print("RAM Usage:")
        ram = usage['ram']
        print(f"  Total: {ram['total'] / (1024**3):.2f} GB")
        print(f"  Used: {ram['used'] / (1024**3):.2f} GB")
        print(f"  Free: {ram['free'] / (1024**3):.2f} GB")
        print(f"  Usage Percent: {ram['percent']}%")

        # GPU Usage
        gpu = usage.get("gpu", {})
        if isinstance(gpu, list):
            for gpu_info in gpu:
                print(f"GPU {gpu_info['gpu_index']} Usage:")
                print(f"  GPU Utilization: {gpu_info['gpu_usage_percent']}%")
                print(f"  Memory Usage Percent: {gpu_info['memory_usage_percent']:.2f}%")
                print(f"  Temperature: {gpu_info['temperature_celsius']}°C")
                print(f"  Total Memory: {gpu_info['total_memory'] / (1024**2):.2f} MB")
                print(f"  Used Memory: {gpu_info['used_memory'] / (1024**2):.2f} MB")
                print(f"  Free Memory: {gpu_info['free_memory'] / (1024**2):.2f} MB")
        else:
            print("GPU Usage:")
            print(f"  {gpu}")

    def shutdown(self):
        """
        Shutdown the NVIDIA Management Library (for cleanup).
        """
        if self.gpu_available:
            try:
                nvmlShutdown()
            except Exception:
                pass  # Ignore shutdown errors

    def _detect_jetson(self):
        """
        Check if the system is an NVIDIA Jetson by reading /proc/device-tree/compatible.
        """
        try:
            if os.path.exists("/proc/device-tree/compatible"):
                with open("/proc/device-tree/compatible", "r") as f:
                    compatible = f.read().lower()
                    return "nvidia,jetson" in compatible or "tegra" in compatible
        except Exception:
            pass
        return False

    def _get_jetson_gpu_stats(self):
        """
        Get Jetson GPU utilization, memory usage, and temperature using 'tegrastats'.
        """
        try:
            process = subprocess.Popen("tegrastats", shell=True, stdout=subprocess.PIPE, text=True)
            output = process.stdout.readline().strip()  # Read only the first line
            process.terminate()  # Stop the process

            # Extract GPU Utilization from "GR3D_FREQ X%"
            gpu_match = re.search(r"GR3D_FREQ\s+(\d+)%", output)
            gpu_usage_percent = float(gpu_match.group(1)) if gpu_match else 0.0

            # Extract GPU Memory Usage from "RAM X/YMB"
            mem_match = re.search(r"RAM\s+(\d+)/(\d+)MB", output)
            if mem_match:
                used_memory = int(mem_match.group(1)) * 1024 * 1024  # Convert MB to Bytes
                total_memory = int(mem_match.group(2)) * 1024 * 1024  # Convert MB to Bytes
                free_memory = total_memory - used_memory
                memory_usage_percent = (used_memory / total_memory) * 100 if total_memory > 0 else 0
            else:
                total_memory = used_memory = free_memory = memory_usage_percent = 0

            # Extract GPU Temperature from "GPU@XXC"
            temp_match = re.search(r"GPU@(\d+\.?\d*)C", output)
            temperature_celsius = float(temp_match.group(1)) if temp_match else 0.0

            return {
                "gpu_index": 0,  # Jetson has only 1 integrated GPU
                "gpu_usage_percent": gpu_usage_percent,
                "memory_usage_percent": memory_usage_percent,
                "temperature_celsius": temperature_celsius,
                "total_memory": total_memory,
                "used_memory": used_memory,
                "free_memory": free_memory,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_jetson_gpu_usage(self):
        """
        Get Jetson GPU usage percentage, memory usage, and temperature using 'tegrastats'.
        """
        try:
            gpu_stats = self._get_jetson_gpu_stats()
            return [gpu_stats]  # Return as a list
        except Exception as e:
            return [{"error": str(e)}]


    def _get_jetson_memory_usage(self):
        """
        Get Jetson GPU memory usage using 'jtop' (if installed).
        """
        try:
            from jtop import jtop
            with jtop() as jetson:
                ram_info = jetson.memory["RAM"]
                return {
                    "total": ram_info["tot"],  # Total RAM in KB
                    "used": ram_info["used"],  # Used RAM in KB
                    "free": ram_info["free"],  # Free RAM in KB
                }
        except ImportError:
            return {"error": "Install 'jtop' using: pip install jtop"}
        except Exception as e:
            return {"error": str(e)}

    def _get_jetson_gpu_temperature(self):
        """
        Get GPU temperature from 'tegrastats'.
        """
        try:
            process = subprocess.Popen("tegrastats", shell=True, stdout=subprocess.PIPE, text=True)
            output = process.stdout.readline().strip()  # Read only one line
            process.terminate()

            # Extract GPU temperature
            match = re.search(r"GPU@(\d+\.?\d*)C", output)
            if match:
                return float(match.group(1))
            return 0.0  # Default if temperature not found
        except Exception as e:
            return {"error": str(e)}

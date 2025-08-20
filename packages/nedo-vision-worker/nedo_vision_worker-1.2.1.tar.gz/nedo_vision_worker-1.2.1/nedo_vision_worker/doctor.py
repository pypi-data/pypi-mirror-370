import subprocess
import sys
import platform
import shutil
import os
import time
import socket
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health check status levels."""
    EXCELLENT = ("🎉", "Excellent")
    GOOD = ("✅", "Good")
    WARNING = ("⚠️ ", "Warning")
    CRITICAL = ("❌", "Critical")
    INFO = ("ℹ️ ", "Info")


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    details: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    is_blocking: bool = False  # Prevents service from running
    performance_impact: str = "None"  # None, Low, Medium, High


class WorkerServiceDoctor:
    """Comprehensive health checker for Nedo Vision Worker Service."""
    
    def __init__(self):
        self.results: List[HealthCheck] = []
        self.start_time = time.time()
        self.system_info = self._gather_system_info()
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information."""
        return {
            'os': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_executable': sys.executable,
            'is_arm': platform.machine() in ["aarch64", "armv7l", "arm64"],
            'is_jetson': self._detect_jetson(),
            'is_container': self._detect_container(),
        }
    
    def _detect_jetson(self) -> bool:
        """Detect if running on NVIDIA Jetson device."""
        jetson_indicators = [
            Path("/sys/firmware/devicetree/base/model"),
            Path("/proc/device-tree/model"),
            Path("/etc/nv_tegra_release")
        ]
        
        for indicator in jetson_indicators:
            try:
                if indicator.exists():
                    content = indicator.read_text().lower()
                    if any(keyword in content for keyword in ["jetson", "tegra", "nvidia"]):
                        return True
            except (OSError, UnicodeDecodeError):
                continue
        return False
    
    def _detect_container(self) -> Dict[str, bool]:
        """Detect containerized environment."""
        return {
            'docker': Path("/.dockerenv").exists(),
            'kubernetes': bool(os.environ.get("KUBERNETES_SERVICE_HOST")),
            'any': Path("/.dockerenv").exists() or bool(os.environ.get("KUBERNETES_SERVICE_HOST"))
        }
    
    def _add_result(self, result: HealthCheck) -> None:
        """Add a health check result."""
        self.results.append(result)
    
    def check_python_environment(self) -> None:
        """Comprehensive Python environment validation."""
        version = sys.version_info
        min_version = (3, 8)
        recommended_version = (3, 9)
        
        details = [
            f"Python {version.major}.{version.minor}.{version.micro}",
            f"Executable: {sys.executable}",
            f"Platform: {platform.python_implementation()}"
        ]
        
        # Check virtual environment
        if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
            details.append("Virtual environment: Active ✓")
            venv_status = HealthStatus.GOOD
        else:
            details.append("Virtual environment: Not detected")
            venv_status = HealthStatus.WARNING
        
        recommendations = []
        
        if version < min_version:
            status = HealthStatus.CRITICAL
            message = f"Python {version.major}.{version.minor} - Too old"
            recommendations.extend([
                f"Upgrade to Python >= {min_version[0]}.{min_version[1]}",
                "Use pyenv, conda, or system package manager",
                "Consider using the latest stable Python version"
            ])
            is_blocking = True
            performance_impact = "High"
        elif version < recommended_version:
            status = HealthStatus.WARNING
            message = f"Python {version.major}.{version.minor} - Works but outdated"
            recommendations.append(f"Consider upgrading to Python >= {recommended_version[0]}.{recommended_version[1]} for better performance")
            is_blocking = False
            performance_impact = "Low"
        elif version >= (3, 11):
            status = HealthStatus.EXCELLENT
            message = f"Python {version.major}.{version.minor} - Excellent (Latest features)"
            performance_impact = "None"
            is_blocking = False
        else:
            status = HealthStatus.GOOD
            message = f"Python {version.major}.{version.minor} - Good"
            performance_impact = "None"
            is_blocking = False
        
        if venv_status == HealthStatus.WARNING:
            recommendations.append("Use virtual environment to avoid dependency conflicts")
        
        self._add_result(HealthCheck(
            name="Python Environment",
            status=status,
            message=message,
            details=details,
            recommendations=recommendations if recommendations else None,
            is_blocking=is_blocking,
            performance_impact=performance_impact
        ))
    
    def check_ffmpeg_installation(self) -> None:
        """Comprehensive FFmpeg installation and capability check."""
        details = []
        recommendations = []
        
        # Check if FFmpeg is available
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            status = HealthStatus.CRITICAL
            message = "FFmpeg not found"
            details.append("FFmpeg executable not found in PATH")
            recommendations.extend([
                "Install FFmpeg using your system package manager",
                self._get_ffmpeg_install_cmd(),
                "Ensure FFmpeg is added to system PATH"
            ])
            is_blocking = True
            performance_impact = "High"
        else:
            try:
                # Get FFmpeg version and build info
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version_lines = result.stdout.split('\n')
                    version_info = version_lines[0] if version_lines else "Unknown version"
                    
                    details.extend([
                        f"Location: {ffmpeg_path}",
                        f"Version: {version_info}",
                    ])
                    
                    # Check for hardware acceleration support
                    build_info = result.stdout
                    hw_accelerations = []
                    
                    hw_checks = {
                        'nvidia': 'NVIDIA GPU acceleration',
                        'cuda': 'CUDA acceleration', 
                        'nvenc': 'NVIDIA encoding',
                        'vaapi': 'VA-API acceleration',
                        'libx264': 'H.264 encoding',
                        'libx265': 'H.265/HEVC encoding'
                    }
                    
                    for hw_key, hw_desc in hw_checks.items():
                        if hw_key in build_info.lower():
                            hw_accelerations.append(hw_desc)
                    
                    if hw_accelerations:
                        details.append(f"Hardware support: {', '.join(hw_accelerations)}")
                        status = HealthStatus.EXCELLENT
                        message = "FFmpeg with hardware acceleration"
                        performance_impact = "None"
                    else:
                        details.append("Hardware support: Software-only")
                        status = HealthStatus.GOOD
                        message = "FFmpeg installed (software-only)"
                        performance_impact = "Medium"
                        recommendations.append("Consider FFmpeg build with hardware acceleration for better performance")
                    
                    is_blocking = False
                    
                else:
                    status = HealthStatus.WARNING
                    message = "FFmpeg found but version check failed"
                    details.append(f"Location: {ffmpeg_path}")
                    details.append("Version check returned error")
                    is_blocking = False
                    performance_impact = "Unknown"
                    recommendations.append("Verify FFmpeg installation integrity")
                
            except subprocess.TimeoutExpired:
                status = HealthStatus.WARNING
                message = "FFmpeg found but unresponsive"
                details.append(f"Location: {ffmpeg_path}")
                details.append("Version check timed out")
                is_blocking = False
                performance_impact = "Unknown"
                recommendations.append("Check FFmpeg installation - may be corrupted")
            except Exception as e:
                status = HealthStatus.WARNING
                message = "FFmpeg check failed"
                details.append(f"Location: {ffmpeg_path}")
                details.append(f"Error: {str(e)}")
                is_blocking = False
                performance_impact = "Unknown"
        
        self._add_result(HealthCheck(
            name="FFmpeg Media Processing",
            status=status,
            message=message,
            details=details,
            recommendations=recommendations if recommendations else None,
            is_blocking=is_blocking,
            performance_impact=performance_impact
        ))
    
    def _get_ffmpeg_install_cmd(self) -> str:
        """Get platform-specific FFmpeg installation command."""
        system = self.system_info['os']
        if system == "Windows":
            return "Windows: choco install ffmpeg OR winget install FFmpeg"
        elif system == "Darwin":
            return "macOS: brew install ffmpeg"
        else:  # Linux
            if self.system_info['is_jetson']:
                return "Jetson: sudo apt install ffmpeg (usually pre-installed)"
            else:
                return "Linux: sudo apt install ffmpeg (Ubuntu/Debian) OR sudo yum install ffmpeg (CentOS/RHEL)"
    
    def check_opencv_installation(self) -> None:
        """Comprehensive OpenCV installation and optimization check."""
        details = []
        recommendations = []
        
        try:
            import cv2
            version = cv2.__version__
            build_info = cv2.getBuildInformation()
            
            details.append(f"OpenCV version: {version}")
            
            # Check build optimizations
            optimizations = []
            performance_flags = {
                'CUDA': 'NVIDIA GPU acceleration',
                'OpenMP': 'Multi-threading optimization',
                'TBB': 'Intel Threading Building Blocks',
                'EIGEN': 'Eigen library optimization',
                'LAPACK': 'Linear algebra optimization'
            }
            
            # ARM-specific optimizations
            if self.system_info['is_arm']:
                performance_flags.update({
                    'NEON': 'ARM NEON SIMD optimization',
                    'VFPV3': 'ARM floating-point optimization'
                })
            
            for flag, description in performance_flags.items():
                if flag in build_info:
                    optimizations.append(description)
            
            if optimizations:
                details.append(f"Optimizations: {', '.join(optimizations)}")
            else:
                details.append("Optimizations: Basic build (no advanced optimizations)")
                recommendations.append("Consider installing optimized OpenCV build for better performance")
            
            # Test basic functionality
            try:
                import numpy as np
                test_img = np.zeros((100, 100, 3), dtype=np.uint8)
                
                # Test image encoding/decoding
                success, encoded = cv2.imencode('.jpg', test_img)
                if success:
                    decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
                    if decoded is not None:
                        details.append("Functionality: Encoding/decoding ✓")
                        
                        # Additional functional tests
                        if self._test_opencv_advanced_features():
                            details.append("Advanced features: Available ✓")
                            status = HealthStatus.EXCELLENT if optimizations else HealthStatus.GOOD
                            message = "OpenCV fully functional" + (" with optimizations" if optimizations else "")
                        else:
                            details.append("Advanced features: Limited")
                            status = HealthStatus.WARNING
                            message = "OpenCV basic functionality only"
                            recommendations.append("Some OpenCV features may be unavailable")
                    else:
                        raise Exception("Image decoding failed")
                else:
                    raise Exception("Image encoding failed")
                
                performance_impact = "None" if optimizations else "Low"
                is_blocking = False
                
            except Exception as e:
                status = HealthStatus.WARNING
                message = "OpenCV installed but functionality limited"
                details.append(f"Functionality test failed: {str(e)}")
                performance_impact = "Medium"
                is_blocking = False
                recommendations.append("Reinstall OpenCV or check dependencies")
        
        except ImportError:
            status = HealthStatus.CRITICAL
            message = "OpenCV not installed"
            details.append("cv2 module not found")
            recommendations.extend([
                "Install OpenCV: pip install opencv-python",
                "For servers: pip install opencv-python-headless",
                "For ARM devices: Consider building from source for optimizations"
            ])
            if self.system_info['is_jetson']:
                recommendations.append("Jetson: Use 'sudo apt install python3-opencv' for GPU-optimized version")
            
            performance_impact = "High"
            is_blocking = True
        
        except Exception as e:
            status = HealthStatus.WARNING
            message = "OpenCV check failed"
            details.append(f"Import error: {str(e)}")
            performance_impact = "Unknown"
            is_blocking = True
            recommendations.append("Check OpenCV installation and dependencies")
        
        self._add_result(HealthCheck(
            name="OpenCV Computer Vision",
            status=status,
            message=message,
            details=details,
            recommendations=recommendations if recommendations else None,
            is_blocking=is_blocking,
            performance_impact=performance_impact
        ))
    
    def _test_opencv_advanced_features(self) -> bool:
        """Test advanced OpenCV features."""
        try:
            import cv2
            import numpy as np
            
            # Test advanced operations
            img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            
            # Test filter operations
            blurred = cv2.GaussianBlur(img, (5, 5), 0)
            
            # Test feature detection (if available)
            try:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                orb = cv2.ORB_create()
                keypoints = orb.detect(gray, None)
                return True
            except:
                return True  # Basic operations work
            
        except Exception:
            return False
    
    def check_gpu_capabilities(self) -> None:
        """Comprehensive GPU detection and capability assessment."""
        details = []
        recommendations = []
        gpu_found = False
        
        # Check NVIDIA GPUs via pynvml
        nvidia_info = self._check_nvidia_gpu()
        if nvidia_info:
            details.extend(nvidia_info['details'])
            gpu_found = True
            if nvidia_info['status'] == 'excellent':
                status = HealthStatus.EXCELLENT
                message = "High-performance NVIDIA GPU detected"
            else:
                status = HealthStatus.GOOD
                message = "NVIDIA GPU available"
        
        # Check for integrated/other GPUs
        integrated_info = self._check_integrated_gpu()
        if integrated_info and not gpu_found:
            details.extend(integrated_info)
            gpu_found = True
            status = HealthStatus.INFO
            message = "Integrated GPU detected"
            recommendations.append("Integrated GPU has limited ML performance compared to dedicated GPUs")
        
        # ARM-specific GPU checks
        if self.system_info['is_arm'] and not gpu_found:
            arm_gpu_info = self._check_arm_gpu()
            if arm_gpu_info:
                details.extend(arm_gpu_info)
                gpu_found = True
                status = HealthStatus.INFO
                message = "ARM GPU detected"
        
        if not gpu_found:
            status = HealthStatus.WARNING
            message = "No GPU detected - CPU processing only"
            details.append("No GPU acceleration available")
            recommendations.extend([
                "GPU acceleration will significantly improve performance",
                "Consider cloud instances with GPU (AWS, GCP, Azure)",
                "For local development: NVIDIA RTX series recommended"
            ])
            performance_impact = "High"
        else:
            performance_impact = "None" if status == HealthStatus.EXCELLENT else "Low"
        
        # Add general GPU recommendations
        if gpu_found and not any("NVIDIA" in detail for detail in details):
            recommendations.append("For optimal ML performance, NVIDIA GPUs with CUDA support are recommended")
        
        self._add_result(HealthCheck(
            name="GPU Acceleration",
            status=status,
            message=message,
            details=details,
            recommendations=recommendations if recommendations else None,
            is_blocking=False,
            performance_impact=performance_impact
        ))
    
    def _check_nvidia_gpu(self) -> Optional[Dict]:
        """Check NVIDIA GPU via pynvml."""
        try:
            import pynvml
            pynvml.nvmlInit()
            
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count == 0:
                return None
            
            details = []
            gpu_status = 'good'
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                
                # Handle both string and bytes return types
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                
                gpu_info = [f"GPU {i}: {name}"]
                
                try:
                    # Memory information
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    memory_total_gb = memory_info.total / (1024**3)
                    memory_used_gb = memory_info.used / (1024**3)
                    memory_free_gb = memory_info.free / (1024**3)
                    
                    gpu_info.append(f"  Memory: {memory_total_gb:.1f}GB total, {memory_free_gb:.1f}GB free")
                    
                    # Assess GPU capability
                    if memory_total_gb >= 24:
                        gpu_info.append("  Capability: Excellent for large models")
                        gpu_status = 'excellent'
                    elif memory_total_gb >= 8:
                        gpu_info.append("  Capability: Good for most models")
                    elif memory_total_gb >= 4:
                        gpu_info.append("  Capability: Suitable for smaller models")
                    else:
                        gpu_info.append("  Capability: Limited VRAM - small models only")
                    
                    # Compute capability
                    try:
                        major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                        compute_cap = f"{major}.{minor}"
                        gpu_info.append(f"  Compute Capability: {compute_cap}")
                        
                        if major >= 7:  # Volta, Turing, Ampere, or newer
                            gpu_info.append("  Architecture: Modern (excellent ML support)")
                        elif major >= 6:  # Pascal
                            gpu_info.append("  Architecture: Good ML support")
                        else:
                            gpu_info.append("  Architecture: Limited ML performance")
                    except:
                        gpu_info.append("  Compute Capability: Unknown")
                    
                    # Temperature and power
                    try:
                        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                        gpu_info.append(f"  Temperature: {temp}°C")
                        
                        if temp > 80:
                            gpu_info.append("  Status: High temperature - check cooling")
                        elif temp > 70:
                            gpu_info.append("  Status: Warm but normal")
                        else:
                            gpu_info.append("  Status: Good temperature")
                    except:
                        pass
                
                except Exception as e:
                    gpu_info.append(f"  Info: Limited details ({str(e)})")
                
                details.extend(gpu_info)
            
            return {
                'details': details,
                'status': gpu_status,
                'count': device_count
            }
        
        except ImportError:
            return None
        except Exception:
            return None
    
    def _check_integrated_gpu(self) -> Optional[List[str]]:
        """Check for integrated GPU on Linux."""
        if self.system_info['os'] != 'Linux':
            return None
        
        try:
            result = subprocess.run(
                ["lspci", "-nn"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                gpu_lines = []
                for line in result.stdout.split('\n'):
                    if any(keyword in line.lower() for keyword in ['vga', 'display', '3d']):
                        if any(vendor in line.lower() for vendor in ['intel', 'amd', 'ati']):
                            gpu_lines.append(f"Integrated GPU: {line.split(':')[-1].strip()}")
                
                return gpu_lines if gpu_lines else None
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def _check_arm_gpu(self) -> Optional[List[str]]:
        """Check for ARM-specific GPU information."""
        if not self.system_info['is_arm']:
            return None
        
        gpu_info = []
        
        # Check for Mali GPU
        mali_paths = [
            "/sys/class/misc/mali0",
            "/dev/mali0",
            "/sys/kernel/debug/mali"
        ]
        
        for path in mali_paths:
            if Path(path).exists():
                gpu_info.append("ARM Mali GPU detected")
                break
        
        # Check for Adreno GPU (Qualcomm)
        if Path("/sys/class/kgsl").exists():
            gpu_info.append("Qualcomm Adreno GPU detected")
        
        # Jetson-specific GPU info
        if self.system_info['is_jetson']:
            gpu_info.append("NVIDIA Tegra integrated GPU")
            
            # Try to get detailed Jetson info
            try:
                result = subprocess.run(
                    ["tegrastats", "--interval", "100", "--logfile", "/dev/stdout"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 and "GPU" in result.stdout:
                    gpu_info.append("Jetson GPU active and monitored")
            except:
                pass
        
        return gpu_info if gpu_info else None
    
    def check_storage_and_permissions(self) -> None:
        """Comprehensive storage and permission validation."""
        details = []
        recommendations = []
        
        try:
            # Test storage permissions
            test_dirs = ["data", "models", "logs", "temp"]
            successful_dirs = []
            failed_dirs = []
            
            for dir_name in test_dirs:
                test_path = Path(dir_name) / "health_check"
                try:
                    test_path.mkdir(parents=True, exist_ok=True)
                    
                    # Test file operations
                    test_file = test_path / "test.json"
                    test_content = '{"test": true, "timestamp": "' + str(time.time()) + '"}'
                    test_file.write_text(test_content)
                    
                    # Read back
                    read_content = test_file.read_text()
                    
                    # Cleanup
                    test_file.unlink()
                    test_path.rmdir()
                    
                    if read_content == test_content:
                        successful_dirs.append(dir_name)
                    else:
                        failed_dirs.append(f"{dir_name} (read/write mismatch)")
                
                except Exception as e:
                    failed_dirs.append(f"{dir_name} ({str(e)})")
            
            # Check disk space
            disk_info = self._check_disk_space()
            details.extend(disk_info['details'])
            
            # Determine overall status
            if failed_dirs:
                status = HealthStatus.CRITICAL
                message = f"Storage permission issues in {len(failed_dirs)} directories"
                details.append(f"Failed directories: {', '.join(failed_dirs)}")
                recommendations.extend([
                    "Check directory permissions and ownership",
                    "Ensure write access to working directory",
                    "Consider running with appropriate user privileges"
                ])
                is_blocking = True
                performance_impact = "High"
            elif disk_info['status'] == 'critical':
                status = HealthStatus.CRITICAL
                message = "Critical disk space shortage"
                is_blocking = True
                performance_impact = "High"
            elif disk_info['status'] == 'warning':
                status = HealthStatus.WARNING
                message = "Storage OK with warnings"
                recommendations.extend(disk_info.get('recommendations', []))
                is_blocking = False
                performance_impact = "Low"
            else:
                status = HealthStatus.GOOD
                message = "Storage permissions and space OK"
                details.append(f"Tested directories: {', '.join(successful_dirs)}")
                is_blocking = False
                performance_impact = "None"
        
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = "Storage check failed"
            details.append(f"Unexpected error: {str(e)}")
            recommendations.append("Investigate storage system issues")
            is_blocking = True
            performance_impact = "High"
        
        self._add_result(HealthCheck(
            name="Storage & Permissions",
            status=status,
            message=message,
            details=details,
            recommendations=recommendations if recommendations else None,
            is_blocking=is_blocking,
            performance_impact=performance_impact
        ))
    
    def _check_disk_space(self) -> Dict:
        """Check available disk space with ML-specific thresholds."""
        try:
            current_dir = Path.cwd()
            disk_usage = shutil.disk_usage(current_dir)
            
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            used_gb = (disk_usage.total - disk_usage.free) / (1024**3)
            free_percent = (free_gb / total_gb) * 100
            
            details = [
                f"Total space: {total_gb:.1f}GB",
                f"Used space: {used_gb:.1f}GB",
                f"Free space: {free_gb:.1f}GB ({free_percent:.1f}%)"
            ]
            
            recommendations = []
            
            if free_gb < 1:
                status = 'critical'
                details.append("Status: Critical - Immediate action required")
                recommendations.extend([
                    "Free up disk space immediately",
                    "Service may fail to start or crash during operation",
                    "Consider moving to system with more storage"
                ])
            elif free_gb < 5:
                status = 'warning'
                details.append("Status: Low - Monitor closely")
                recommendations.extend([
                    "Free up disk space soon",
                    "Model downloads and processing may fail",
                    "ML models typically require 2-20GB+ storage"
                ])
            elif free_gb < 20:
                status = 'warning'
                details.append("Status: Adequate for small models")
                recommendations.append("Large models may require additional space")
            else:
                status = 'good'
                details.append("Status: Good - Sufficient for most operations")
            
            return {
                'status': status,
                'details': details,
                'recommendations': recommendations
            }
        
        except Exception as e:
            return {
                'status': 'unknown',
                'details': [f"Disk space check failed: {str(e)}"],
                'recommendations': ["Manually verify available disk space"]
            }
    
    def check_system_resources(self) -> None:
        """Check system resources and performance characteristics."""
        details = []
        recommendations = []
        
        try:
            # Try to get detailed system info
            try:
                import psutil
                
                # CPU information
                cpu_count_physical = psutil.cpu_count(logical=False)
                cpu_count_logical = psutil.cpu_count(logical=True)
                cpu_freq = psutil.cpu_freq()
                
                details.append(f"CPU cores: {cpu_count_physical} physical, {cpu_count_logical} logical")
                
                if cpu_freq:
                    details.append(f"CPU frequency: {cpu_freq.current:.0f} MHz (max: {cpu_freq.max:.0f} MHz)")
                
                # Memory information
                memory = psutil.virtual_memory()
                memory_gb = memory.total / (1024**3)
                memory_available_gb = memory.available / (1024**3)
                memory_percent = memory.percent
                
                details.append(f"RAM: {memory_gb:.1f}GB total, {memory_available_gb:.1f}GB available ({100-memory_percent:.1f}% free)")
                
                # Memory recommendations
                memory_status = "good"
                if memory_gb < 4:
                    memory_status = "critical"
                    recommendations.extend([
                        "Insufficient RAM for ML workloads",
                        "Consider upgrading to at least 8GB RAM",
                        "ML models may fail to load or crash"
                    ])
                elif memory_gb < 8:
                    memory_status = "warning"
                    recommendations.append("8GB+ RAM recommended for better performance")
                elif memory_gb >= 32:
                    details.append("RAM: Excellent for large model processing")
                
                # Swap information
                try:
                    swap = psutil.swap_memory()
                    if swap.total > 0:
                        swap_gb = swap.total / (1024**3)
                        details.append(f"Swap: {swap_gb:.1f}GB")
                    else:
                        details.append("Swap: Not configured")
                        if memory_gb < 16:
                            recommendations.append("Consider configuring swap space for memory-intensive operations")
                except:
                    pass
                
                # CPU usage check (brief sample)
                cpu_percent = psutil.cpu_percent(interval=1)
                details.append(f"CPU usage: {cpu_percent:.1f}%")
                
                if cpu_percent > 80:
                    recommendations.append("High CPU usage detected - check for background processes")
                
            except ImportError:
                # Fallback without psutil
                import multiprocessing
                cpu_count = multiprocessing.cpu_count()
                details.append(f"CPU cores: {cpu_count} (detected)")
                details.append("Install 'psutil' for detailed system monitoring")
                recommendations.append("pip install psutil for enhanced system monitoring")
                memory_status = "unknown"
            
            # Platform-specific optimizations
            if self.system_info['is_arm']:
                details.append("Platform: ARM architecture")
                if self.system_info['is_jetson']:
                    details.append("Optimization: Jetson-specific optimizations available")
                    recommendations.append("Use Jetson-optimized libraries when available")
                else:
                    recommendations.append("Consider ARM-optimized ML libraries")
            
            # Container considerations
            container_info = self._detect_container()
            if container_info['any']:
                container_types = []
                if container_info['docker']:
                    container_types.append("Docker")
                if container_info['kubernetes']:
                    container_types.append("Kubernetes")
                
                details.append(f"Environment: Containerized ({', '.join(container_types)})")
                recommendations.extend([
                    "Ensure container has adequate resource limits",
                    "Consider GPU passthrough for ML acceleration"
                ])
            
            # Determine status
            if memory_status == "critical":
                status = HealthStatus.CRITICAL
                message = "Insufficient system resources"
                is_blocking = True
                performance_impact = "High"
            elif memory_status == "warning":
                status = HealthStatus.WARNING
                message = "Limited system resources"
                is_blocking = False
                performance_impact = "Medium"
            else:
                status = HealthStatus.GOOD
                message = "System resources adequate"
                is_blocking = False
                performance_impact = "None"
        
        except Exception as e:
            status = HealthStatus.WARNING
            message = "System resource check failed"
            details.append(f"Error: {str(e)}")
            recommendations.append("Manual system resource verification recommended")
            is_blocking = False
            performance_impact = "Unknown"
        
        self._add_result(HealthCheck(
            name="System Resources",
            status=status,
            message=message,
            details=details,
            recommendations=recommendations if recommendations else None,
            is_blocking=is_blocking,
            performance_impact=performance_impact
        ))
    
    def run_comprehensive_health_check(self) -> List[HealthCheck]:
        """Execute all health checks with progress indication."""
        print("🏥 Nedo Vision Worker Service - Comprehensive Health Check")
        print("=" * 65)
        
        # Display system summary
        self._print_system_summary()
        print()
        
        # Define all health checks
        health_checks = [
            ("Python Environment", self.check_python_environment),
            ("System Resources", self.check_system_resources),
            ("Storage & Permissions", self.check_storage_and_permissions),
            ("FFmpeg Media Processing", self.check_ffmpeg_installation),
            ("OpenCV Computer Vision", self.check_opencv_installation),
            ("GPU Acceleration", self.check_gpu_capabilities),
        ]
        
        print(f"🔍 Running {len(health_checks)} comprehensive health checks...")
        print("-" * 50)
        
        # Execute checks with progress indication
        for i, (check_name, check_function) in enumerate(health_checks, 1):
            print(f"[{i:2d}/{len(health_checks)}] {check_name:<30} ", end="", flush=True)
            
            try:
                start_time = time.time()
                check_function()
                duration = time.time() - start_time
                print(f"✓ ({duration:.1f}s)")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                # Add error result
                self._add_result(HealthCheck(
                    name=check_name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    is_blocking=True,
                    performance_impact="High"
                ))
            
            time.sleep(0.1)  # Brief pause for better UX
        
        return self.results
    
    def _print_system_summary(self) -> None:
        """Print concise system information summary."""
        info = self.system_info
        
        print("💻 System Summary:")
        print(f"   OS: {info['os']} {info['release']}")
        print(f"   Architecture: {info['machine']}")
        print(f"   Python: {info['python_version']}")
        
        if info['is_jetson']:
            print("   Platform: NVIDIA Jetson Device")
        elif info['is_arm']:
            print("   Platform: ARM-based Device")
        
        container_info = self._detect_container()
        if container_info['any']:
            environments = []
            if container_info['docker']:
                environments.append("Docker")
            if container_info['kubernetes']:
                environments.append("Kubernetes")
            print(f"   Environment: {', '.join(environments)}")
    
    def generate_detailed_report(self) -> bool:
        """Generate comprehensive health report with recommendations."""
        elapsed_time = time.time() - self.start_time
        
        print(f"\n{'='*65}")
        print("📊 COMPREHENSIVE HEALTH REPORT")
        print(f"{'='*65}")
        print(f"⏱️  Scan completed in {elapsed_time:.1f} seconds")
        print(f"🔍 {len(self.results)} health checks performed")
        
        # Categorize results
        excellent = [r for r in self.results if r.status == HealthStatus.EXCELLENT]
        good = [r for r in self.results if r.status == HealthStatus.GOOD]
        warnings = [r for r in self.results if r.status in [HealthStatus.WARNING, HealthStatus.INFO]]
        critical = [r for r in self.results if r.status == HealthStatus.CRITICAL]
        blocking = [r for r in self.results if r.is_blocking]
        
        # Print detailed results
        print(f"\n{'─'*65}")
        print("📋 DETAILED RESULTS")
        print(f"{'─'*65}")
        
        for result in self.results:
            icon, status_text = result.status.value
            print(f"\n{icon} {result.name}")
            print(f"   Status: {result.message}")
            
            if result.details:
                print("   Details:")
                for detail in result.details:
                    print(f"     • {detail}")
            
            if result.performance_impact != "None":
                print(f"   Performance Impact: {result.performance_impact}")
            
            if result.recommendations:
                print("   💡 Recommendations:")
                for rec in result.recommendations:
                    print(f"     ▶ {rec}")
        
        # Generate executive summary
        print(f"\n{'='*65}")
        print("📈 EXECUTIVE SUMMARY")
        print(f"{'='*65}")
        
        print(f"🎉 Excellent: {len(excellent)}")
        print(f"✅ Good: {len(good)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        print(f"❌ Critical: {len(critical)}")
        
        # Service readiness assessment
        print(f"\n{'─'*40}")
        if blocking:
            print("🚫 SERVICE STATUS: NOT READY")
            print(f"   {len(blocking)} blocking issues must be resolved")
            print("\n🔧 REQUIRED ACTIONS:")
            for issue in blocking:
                print(f"   ❌ Fix: {issue.name} - {issue.message}")
                if issue.recommendations:
                    for rec in issue.recommendations[:2]:  # Show top 2 recommendations
                        print(f"      ▶ {rec}")
        elif critical:
            print("⚠️  SERVICE STATUS: DEGRADED")
            print("   Service may work but with significant limitations")
            print(f"   {len(critical)} critical issues detected")
        elif warnings:
            print("✅ SERVICE STATUS: READY WITH RECOMMENDATIONS")
            print("   Service should work well with minor optimizations available")
        else:
            print("🎉 SERVICE STATUS: OPTIMAL")
            print("   All systems green - maximum performance expected")
        
        # Performance optimization summary
        high_impact = [r for r in self.results if r.performance_impact == "High"]
        medium_impact = [r for r in self.results if r.performance_impact == "Medium"]
        
        if high_impact or medium_impact:
            print(f"\n⚡ PERFORMANCE OPTIMIZATION OPPORTUNITIES:")
            if high_impact:
                print(f"   High Impact ({len(high_impact)}): ", end="")
                print(", ".join([r.name for r in high_impact]))
            if medium_impact:
                print(f"   Medium Impact ({len(medium_impact)}): ", end="")
                print(", ".join([r.name for r in medium_impact]))
        
        # Installation help
        if blocking or critical:
            print(f"\n{'='*65}")
            print("📚 INSTALLATION GUIDE")
            print(f"{'='*65}")
            self._print_installation_guide()
        
        print(f"{'='*65}")
        
        return len(blocking) == 0
    
    def _print_installation_guide(self) -> None:
        """Print comprehensive installation guide."""
        system = self.system_info['os']
        is_arm = self.system_info['is_arm']
        is_jetson = self.system_info['is_jetson']
        
        print("\n🎬 FFmpeg Installation:")
        if system == "Windows":
            print("   • Chocolatey: choco install ffmpeg")
            print("   • Winget: winget install FFmpeg")
            print("   • Manual: https://ffmpeg.org/download.html")
        elif system == "Darwin":
            print("   • Homebrew: brew install ffmpeg")
            print("   • MacPorts: sudo port install ffmpeg")
        else:  # Linux
            if is_jetson:
                print("   • Jetson: Usually pre-installed with JetPack")
                print("   • If missing: sudo apt install ffmpeg")
            else:
                print("   • Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
                print("   • CentOS/RHEL: sudo yum install ffmpeg")
                print("   • Fedora: sudo dnf install ffmpeg")
        
        print("\n🐍 Python Dependencies:")
        print("   • Core packages: pip install opencv-python grpcio protobuf")
        print("   • GPU support: pip install pynvml")
        print("   • System monitoring: pip install psutil")
        
        if is_arm:
            print("   • ARM optimizations:")
            if is_jetson:
                print("     - OpenCV: sudo apt install python3-opencv (GPU-optimized)")
                print("     - JetPack SDK includes optimized libraries")
            else:
                print("     - Consider: opencv-python-headless for servers")
                print("     - ARM wheels: --extra-index-url https://www.piwheels.org/simple/")
        
        print("\n🎮 GPU Setup:")
        if is_jetson:
            print("   • Jetson devices:")
            print("     - Install JetPack SDK")
            print("     - Verify: sudo /usr/bin/tegrastats")
            print("     - Check CUDA: nvcc --version")
        else:
            print("   • NVIDIA GPUs:")
            print("     - Install drivers: https://www.nvidia.com/drivers/")
            print("     - CUDA toolkit for development")
            print("     - Verify: nvidia-smi")
        
        print("\n💾 Storage Requirements:")
        print("   • Minimum 5GB free space")
        print("   • 20GB+ recommended for model storage")
        print("   • Write permissions in working directory")


def main() -> int:
    """Main entry point for worker service health check."""
    try:
        doctor = WorkerServiceDoctor()
        results = doctor.run_comprehensive_health_check()
        is_ready = doctor.generate_detailed_report()
        return 0 if is_ready else 1
    
    except KeyboardInterrupt:
        print("\n\n🛑 Health check interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n\n💥 Unexpected error during health check: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
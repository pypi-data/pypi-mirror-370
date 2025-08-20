import os
import platform

class PlatformDetector:
    """
    A class to detect whether the application is running on a Jetson device or a PC.
    """

    @staticmethod
    def is_jetson():
        """
        Determines if the platform is an NVIDIA Jetson device.

        Returns:
            bool: True if running on a Jetson device, False otherwise.
        """
        try:
            # Check for Jetson-specific device tree file
            if os.path.exists("/proc/device-tree/model"):
                with open("/proc/device-tree/model", "r") as f:
                    model = f.read().strip()
                    if "NVIDIA Jetson" in model:
                        return True

            # Check for Jetson-specific libraries
            jetson_libraries = ["/usr/lib/aarch64-linux-gnu/tegra"]
            if any(os.path.exists(lib) for lib in jetson_libraries):
                return True

            # Check architecture
            arch = platform.machine()
            if arch == "aarch64":  # Jetson typically runs on ARM64 (aarch64)
                return True

        except Exception as e:
            print(f"Error detecting Jetson platform: {e}")

        return False

    @staticmethod
    def get_platform_type():
        """
        Gets the platform type as a string.

        Returns:
            str: "Jetson" if running on an NVIDIA Jetson device, "PC" otherwise.
        """
        if PlatformDetector.is_jetson():
            return "jetson"
        return "pc"

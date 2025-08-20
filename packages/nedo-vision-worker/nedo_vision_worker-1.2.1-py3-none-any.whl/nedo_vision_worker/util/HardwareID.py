import os
import platform
import subprocess
import uuid

class HardwareID:
    @staticmethod
    def get_unique_id():
        """Returns a unique hardware identifier based on the OS."""
        system = platform.system().lower()
        try:
            if system == "windows":
                return HardwareID._get_windows_uuid()
            elif system == "darwin":
                return HardwareID._get_mac_uuid()
            elif system == "linux":
                return HardwareID._get_linux_uuid()
            else:
                return HardwareID._get_fallback_uuid()
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def _get_windows_uuid():
        """Fetches the hardware UUID from Windows using WMIC."""
        try:
            # First attempt: Use wmic
            output = subprocess.check_output("wmic csproduct get UUID", shell=True)
            uuid_str = output.decode().split("\n")[1].strip()
            if uuid_str:
                return uuid_str
            else:
                # Fallback: Machine GUID from Registry
                output = subprocess.check_output("reg query HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography /v MachineGuid", shell=True)
                return HardwareID.convert_to_uuid(output.decode().split()[-1])
        except subprocess.CalledProcessError:
            try:
                # Fallback attempt: Use PowerShell if wmic fails
                output = subprocess.check_output(['powershell', 'Get-WmiObject -Class Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID'], shell=True, text=True)
                return output.strip()  # Clean up the result
            except subprocess.CalledProcessError:
                # Both methods failed, return fallback UUID
                return HardwareID._get_fallback_uuid()

    @staticmethod
    def _get_mac_uuid():
        """Fetches the hardware UUID from macOS using ioreg."""
        try:
            output = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/ { print $3; }'", shell=True)
            return output.decode().strip().replace('"', '')
        except:
            return HardwareID._get_fallback_uuid()

    @staticmethod
    def _get_linux_uuid():
        """Fetches the hardware UUID from Linux or NVIDIA Jetson."""
        try:
            # Check for Jetson Serial Number
            if os.path.exists("/sys/devices/soc0/serial_number"):
                with open("/sys/devices/soc0/serial_number", "r") as f:
                    return HardwareID.convert_to_uuid(f.read().strip())
            elif os.path.exists("/proc/device-tree/serial-number"):
                with open("/proc/device-tree/serial-number", "r") as f:
                    return HardwareID.convert_to_uuid(f.read().strip())

            # Standard Linux machine-id
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    return HardwareID.convert_to_uuid(f.read().strip())
            elif os.path.exists("/var/lib/dbus/machine-id"):
                with open("/var/lib/dbus/machine-id", "r") as f:
                    return HardwareID.convert_to_uuid(f.read().strip())
            
            # Fallback to DMI Product UUID
            output = subprocess.check_output("cat /sys/class/dmi/id/product_uuid", shell=True)
            return HardwareID.convert_to_uuid(output.decode().strip())
        except:
            return HardwareID._get_fallback_uuid()

    @staticmethod
    def _get_fallback_uuid():
        """Fallback method using MAC address hash."""
        return str(uuid.getnode())
    
    @staticmethod
    def convert_to_uuid(hardware_id: str) -> str:
        """
        Converts a hardware ID to a valid UUID format.
        
        Args:
            hardware_id (str): The raw hardware ID string.
        
        Returns:
            str: A valid UUID string.
        """
        # Remove null characters and non-printable characters
        cleaned_id = hardware_id.strip().replace("\x00", "")
        
        # Ensure the length is 32 characters (UUID hex format)
        hex_id = cleaned_id.ljust(32, "0")[:32]  # Pad with zeros if needed
        
        # Convert to UUID format
        return str(uuid.UUID(hex_id))


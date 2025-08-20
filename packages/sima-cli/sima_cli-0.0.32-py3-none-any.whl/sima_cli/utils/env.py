import os
import subprocess
import platform
import shutil
from typing import Tuple

# Utility functions to determine the environment:
# - Whether we are running on a SiMa board
# - Or from a PCIe host (e.g., a developer workstation)

def is_sima_board() -> bool:
    """
    Detect if running on a SiMa board.

    This is done by checking for the existence of known build info files
    (/etc/build or /etc/buildinfo) and looking for specific identifiers like 
    SIMA_BUILD_VERSION and MACHINE.

    Returns:
        bool: True if running on a SiMa board, False otherwise.
    """
    build_file_paths = ["/etc/build", "/etc/buildinfo"]

    for path in build_file_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    content = f.read()
                    if "SIMA_BUILD_VERSION" in content and "MACHINE" in content:
                        return True
            except Exception:
                continue

    return False

def is_pcie_host() -> bool:
    """
    Detect if running from a PCIe host (typically a Linux or macOS dev machine).

    This assumes a PCIe host is not a SiMa board and is running on a standard Linux platform.

    Returns:
        bool: True if likely a PCIe host, False otherwise.
    """
    import platform
    return not is_sima_board() and platform.system() in ["Linux"]

def get_sima_board_type() -> str:
    """
    If running on a SiMa board, extract the board type from the MACHINE field
    in /etc/build or /etc/buildinfo.

    Returns:
        str: The board type (e.g., "modalix", "davinci"), or an empty string if not found or not a SiMa board.
    """
    build_file_paths = ["/etc/build", "/etc/buildinfo"]

    for path in build_file_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("MACHINE"):
                            # Format: MACHINE = modalix
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                return parts[1].strip()
            except Exception:
                continue

    return ""

def is_modalix_devkit() -> bool:
    """
    Determines whether the current system is a Modalix DevKit (SOM)
    by checking if 'fdt_name=modalix-som.dtb' is present in fw_printenv output.

    Returns:
        bool: True if running on a Modalix DevKit, False otherwise.
    """
    if not shutil.which("fw_printenv"):
        return False

    try:
        output = subprocess.check_output(["fw_printenv"], text=True)
        for line in output.splitlines():
            if line.strip().startswith("fdt_name="):
                return "modalix-som.dtb" in line
    except subprocess.CalledProcessError:
        return False

    return False

def get_exact_devkit_type() -> str:
    """
    Extracts the exact devkit type from 'fdt_name' in fw_printenv output.

    Returns:
        str: The value of fdt_name (e.g., "modalix-som"), or an empty string if not found or unavailable.
    """
    if not shutil.which("fw_printenv"):
        return ""

    try:
        output = subprocess.check_output(["fw_printenv"], text=True)
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("fdt_name="):
                _, value = line.split("=", 1)
                return value.strip().replace('.dtb','')
    except subprocess.CalledProcessError:
        return ""
    except Exception:
        return ""

    return ""

def is_board_running_full_image() -> bool:
    """
    Heuristic: return True if the 'full' image appears to be installed.
    We detect this by checking for the NVMe CLI ('nvme'), which is bundled
    with the full image but not the headless image.

    Returns:
        bool: True if nvme binary is found, else False.
    """
    try:
        # Ensure sbin dirs are in search path (non-root shells often miss these)
        search_path = os.environ.get("PATH", "")
        sbin = "/usr/sbin:/sbin"
        if search_path:
            search_path = f"{search_path}:{sbin}"
        else:
            search_path = sbin

        nvme_path = shutil.which("nvme", path=search_path)
        if nvme_path and os.path.exists(nvme_path):
            return True

        # Fallback: direct checks (in case PATH is unusual)
        for p in ("/usr/sbin/nvme", "/sbin/nvme", "/usr/bin/nvme", "/bin/nvme"):
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return True

        return False
    except Exception:
        return False

def is_palette_sdk() -> bool:
    """
    Check if the environment is running inside the Palette SDK container.

    This is detected by checking for the /etc/sdk-release file and verifying
    it contains the string 'Palette_SDK'.

    Returns:
        bool: True if running in Palette SDK, False otherwise.
    """
    sdk_release_path = "/etc/sdk-release"
    if not os.path.exists(sdk_release_path):
        return False

    try:
        with open(sdk_release_path, "r") as f:
            content = f.read()
            return "Palette_SDK" in content
    except Exception:
        return False

def get_environment_type() -> Tuple[str, str]:
    """
    Return the environment type and subtype as a tuple.

    Returns:
        tuple:
            - env_type (str): "board", "sdk", or "host"
            - env_subtype (str): board type (e.g., "modalix"), "palette", or host OS (e.g., "mac", "linux", "windows")
    """
    if is_palette_sdk():
        return "sdk", "palette"

    if is_sima_board():
        board_type = get_sima_board_type()
        return "board", board_type or "unknown"

    import platform
    system = platform.system().lower()
    if system == "darwin":
        return "host", "mac"
    elif system == "linux":
        return "host", "linux"
    elif system == "windows":
        return "host", "windows"

    return "host", "unknown"

def check_pcie_card_installation() -> Tuple[bool, str]:
    """
    Check whether the PCIe SiMa card is properly installed on a supported Linux host.

    Returns:
        tuple:
            - success (bool): True if all checks pass, False otherwise.
            - message (str): Summary of results or error message.
    """
    # Platform check
    if platform.system().lower() != "linux":
        return False, "❌ This check is only supported on Linux hosts."

    if is_sima_board():
        return False, "❌ This check is not applicable when running on a SiMa board."

    if is_palette_sdk():
        return False, "❌ This check is not applicable inside the Palette SDK container."

    try:
        # Check GStreamer plugin
        gst_result = subprocess.run(
            ["gst-inspect-1.0", "pciehost"],
            capture_output=True, text=True
        )
        if gst_result.returncode != 0 or "pciehost" not in gst_result.stdout:
            return False, "❌ GStreamer plugin 'pciehost' not found."

        # Check kernel module
        modinfo_result = subprocess.run(
            ["modinfo", "sima_mla_drv"],
            capture_output=True, text=True
        )
        if modinfo_result.returncode != 0 or "sima_mla_drv" not in modinfo_result.stdout:
            return False, "❌ sima_mla_drv kernel module not found or not loaded."

        # Check PCI device presence
        lspci_result = subprocess.run(
            ["lspci", "-vd", "1f06:abcd"],
            capture_output=True, text=True
        )
        if lspci_result.returncode != 0 or "Device 1f06:abcd" not in lspci_result.stdout:
            return False, "❌ PCIe SiMa card not detected."

        return True, "✅ PCIe SiMa card is properly installed and recognized."

    except FileNotFoundError as e:
        return False, f"❌ Required system tool not found: {e.filename}"

    except Exception as e:
        return False, f"❌ Unexpected error: {str(e)}"


if __name__ == "__main__":
    env_type, env_subtype = get_environment_type()
    print(f"Environment Type: {env_type}")
    print(f"Environment Subtype: {env_subtype}")
import json
import platform
import psutil
import shutil
import subprocess
import sys
import re
try:
    from packaging import version
except ImportError:
    version = None

def load_requirements(file_path='system_requirements.json'):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Requirements file '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'.")
        sys.exit(1)

def check_cpu_cores(required_cores):
    actual_cores = psutil.cpu_count(logical=False)
    return actual_cores >= required_cores, f"CPU Cores: {actual_cores} (Required: {required_cores})"

def check_memory(required_memory_gb):
    actual_memory = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GB
    return actual_memory >= required_memory_gb, f"Memory: {actual_memory:.2f} GB (Required: {required_memory_gb} GB)"

def check_storage(required_storage_gb):
    _, _, free = shutil.disk_usage('/')
    free_gb = free / (1024 ** 3)  # Convert bytes to GB
    return free_gb >= required_storage_gb, f"Free Storage: {free_gb:.2f} GB (Required: {required_storage_gb} GB)"

def check_os(supported_os):
    current_os = platform.system()
    current_version = platform.version()
    system_name = current_os.lower()
    
    if system_name == "linux":
        if "Ubuntu 22.04" in supported_os:
            try:
                with open('/etc/os-release') as f:
                    os_info = f.read()
                if "Ubuntu 22.04" in os_info:
                    return True, "OS: Ubuntu 22.04 (Supported)"
            except FileNotFoundError:
                pass
    elif system_name == "windows":
        if "10" in current_version and "Windows 10" in supported_os:
            return True, "OS: Windows 10 (Supported)"
        if "11" in current_version and "Windows 11" in supported_os:
            return True, "OS: Windows 11 (Supported)"
    
    return False, f"OS: {current_os} {current_version} (Not supported)"

def check_docker_version(required_version):
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
        if not match:
            return False, "Docker: Could not parse version"
        current_version = match.group(1)
        current_os = platform.system().lower()
        required = required_version.get(current_os, None)
        if required is None:
            return True, f"Docker: {current_version} (No version requirement for {current_os})"
        if version:
            result = version.parse(current_version) >= version.parse(required)
        else:
            current_parts = tuple(map(int, current_version.split('.')))
            required_parts = tuple(map(int, required.split('.')))
            result = current_parts >= required_parts
        return result, f"Docker: {current_version} (Required: {required})"
    except FileNotFoundError:
        return False, "Docker: Not installed"

def check_python_version(required_version):
    current_version = platform.python_version()
    if version:
        # Use packaging.version for proper version comparison
        result = version.parse(current_version) >= version.parse(required_version)
    else:
        # Fallback to tuple comparison if packaging is not available
        current_parts = tuple(map(int, current_version.split('.')))
        required_parts = tuple(map(int, required_version.split('.')))
        result = current_parts >= required_parts
    return result, f"Python: {current_version} (Required: {required_version})"

def main():
    requirements = load_requirements()
    
    checks = [
        check_cpu_cores(requirements['cpu_cores']),
        check_memory(requirements['memory_gb']),
        check_storage(requirements['storage_gb']),
        check_os(requirements['supported_os']),
        check_docker_version(requirements['docker_version']),
        check_python_version(requirements['python_min_version'])
    ]
    
    print("System Check Results:")
    print("-" * 50)
    all_passed = True
    
    for passed, message in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {message}")
        if not passed:
            all_passed = False
    
    print("-" * 50)
    print("System Check: " + ("PASSED" if all_passed else "FAILED"))
    if not all_passed:
        print("Please address the failed requirements.")

if __name__ == "__main__":
    main()
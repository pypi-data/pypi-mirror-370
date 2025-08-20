import click
import subprocess
import platform
import shutil
import sys
import os
import time

from sima_cli.update.bootimg import list_removable_devices, unmount_device, _require_sudo
from sima_cli.utils.env import is_sima_board

def get_partition_path(device: str) -> str:
    """For Linux: partition is device + '1'"""
    return device + "1"


def find_mkfs_ext4() -> str:
    """Find mkfs.ext4 on Linux"""
    mkfs_path = shutil.which("mkfs.ext4")
    if mkfs_path and os.path.exists(mkfs_path):
        return mkfs_path
    return None


def wipe_existing_partitions(device_path: str):
    """
    Fully wipe all partition entries using sgdisk or dd to ensure a clean disk.
    """
    click.echo(f"💣 Wiping partition table on {device_path}")
    subprocess.run(["sudo", "sgdisk", "--zap-all", device_path], check=False)
    subprocess.run(["sudo", "wipefs", "--all", device_path], check=False)

    # Optional: clear first 1MB and last 1MB
    subprocess.run(["sudo", "dd", "if=/dev/zero", f"of={device_path}", "bs=1M", "count=1"], check=False)
    subprocess.run(["sudo", "blockdev", "--rereadpt", device_path], check=False)

def kill_partition_users(device_path: str):
    """
    Unmount all mounted partitions of the device, and kill only real user processes if needed.
    """
    try:
        # List all partitions of the device (e.g., /dev/sda1, /dev/sda2)
        output = subprocess.check_output(["lsblk", "-n", "-o", "NAME", device_path]).decode().strip().splitlines()
        partitions = [f"/dev/{line.strip()}" for line in output if line.strip() and f"/dev/{line.strip()}" != device_path]

        for part in partitions:
            # Check if the partition is mounted
            mountpoint = subprocess.run(["findmnt", "-n", "-o", "TARGET", part],
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if mountpoint.returncode == 0 and mountpoint.stdout.strip():
                # It's mounted — unmount it
                click.echo(f"🛑 Unmounting mounted partition {part}")
                subprocess.run(["sudo", "umount", part], check=False)

            # Optionally kill any real user-space processes using the partition
            try:
                users = subprocess.check_output(["sudo", "lsof", part], stderr=subprocess.DEVNULL).decode().splitlines()
                pids = {line.split()[1] for line in users[1:] if line.strip()}
                for pid in pids:
                    click.echo(f"🔪 Killing PID {pid} using {part}")
                    subprocess.run(["sudo", "kill", "-9", pid], check=False)
            except subprocess.CalledProcessError:
                pass

        time.sleep(1)

    except Exception as e:
        click.echo(f"⚠️ Could not resolve partition users: {e}")

def create_partition_table(device_path: str):
    """Linux: create a GPT partition table with one ext4 partition"""
    click.echo(f"🧹 Wiping and partitioning {device_path} using parted (Linux)")
    subprocess.run(["sudo", "parted", "-s", device_path, "mklabel", "gpt"], check=True)
    subprocess.run(["sudo", "parted", "-s", device_path, "mkpart", "primary", "ext4", "0%", "100%"], check=True)
    subprocess.run(["sudo", "partprobe", device_path], check=True)


def force_release_device(device_path: str):
    """
    Try to forcefully release a device by killing users and removing mappings.
    """
    # Ensure partitions like /dev/sdc1 don't block parted
    subprocess.run(["sudo", "umount", device_path + "1"], stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "dmsetup", "remove", device_path], stderr=subprocess.DEVNULL)

    # Try lsof to find open handles
    try:
        out = subprocess.check_output(["sudo", "lsof", device_path], stderr=subprocess.DEVNULL).decode()
        for line in out.splitlines()[1:]:
            pid = line.split()[1]
            subprocess.run(["sudo", "kill", "-9", pid], check=False)
    except subprocess.CalledProcessError:
        # Likely no users
        pass

    # Final probe reset
    subprocess.run(["sudo", "partprobe"], stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "udevadm", "settle"], stderr=subprocess.DEVNULL)


def sdcard_format():
    """Linux-only SD card formatter for ext4."""

    if platform.system() != "Linux":
        click.echo("❌ This command only supports Desktop Linux.")
        sys.exit(1)

    if is_sima_board():
        click.echo("❌ This command does not run on the DevKit due to lack of mkfs.ext4 support.")

    mkfs_path = find_mkfs_ext4()
    if not mkfs_path:
        click.echo("❌ mkfs.ext4 not found on this platform.")
        sys.exit(1)

    devices = list_removable_devices()
    if not devices:
        click.echo("⚠️  No removable SD card found.")
        return

    click.echo("\n🔍 Detected removable devices:")
    for i, d in enumerate(devices):
        click.echo(f"[{i}] {d['path']} - {d['size']} - {d['name']}")

    selected_path = None
    if len(devices) == 1:
        if click.confirm(f"\n✅ Use device {devices[0]['path']}?"):
            selected_path = devices[0]['path']
    else:
        choice = click.prompt("Enter the number of the device to format", type=int)
        if 0 <= choice < len(devices):
            selected_path = devices[choice]['path']

    if not selected_path:
        click.echo("❌ No device selected. Operation cancelled.")
        return

    click.echo(f"\n🚨 WARNING: This will ERASE ALL DATA on {selected_path}")
    if not click.confirm("Are you sure you want to continue?"):
        click.echo("❌ Aborted by user.")
        return

    _require_sudo()
    unmount_device(selected_path)
    force_release_device(selected_path)
    kill_partition_users(selected_path)
    wipe_existing_partitions(selected_path)

    try:
        create_partition_table(selected_path)
        partition_path = get_partition_path(selected_path)

        click.echo(f"🧱 Formatting partition {partition_path} as ext4 using {mkfs_path}")
        subprocess.run(["sudo", mkfs_path, "-F", partition_path], check=True)

        click.echo(f"✅ Successfully formatted {partition_path} as ext4, insert this SD card into MLSoC or Modalix Early Access Kit")

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Formatting failed: {e}")
        sys.exit(1)

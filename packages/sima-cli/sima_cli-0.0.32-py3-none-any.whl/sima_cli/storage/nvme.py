import subprocess
import click
import re

from sima_cli.utils.env import is_modalix_devkit

def scan_nvme():
    try:
        nvme_list = subprocess.check_output("sudo nvme list", shell=True, text=True).strip()
        if "/dev/nvme0n1" in nvme_list:
            return nvme_list
    except subprocess.CalledProcessError:
        pass
    return None

def get_lba_format_index():
    try:
        lba_output = subprocess.check_output("sudo nvme id-ns -H /dev/nvme0n1 | grep 'Relative Performance'", shell=True, text=True)
        lbaf_line = lba_output.strip().split(":")[0]
        lbaf_index = lbaf_line.split()[-1]
        return lbaf_index
    except Exception:
        return None

def format_nvme(lbaf_index):
    cmds = [
        f"sudo nvme format /dev/nvme0n1 --lbaf={lbaf_index}",
        "sudo parted -a optimal /dev/nvme0n1 mklabel gpt",
        "sudo parted -a optimal /dev/nvme0n1 mkpart primary ext4 0% 100%",
        "sudo mkfs.ext4 /dev/nvme0n1p1",
        "sudo nvme smart-log -H /dev/nvme0n1"
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True, check=True)

def add_nvme_to_fstab():
    """
    Add UUID-based entry for /dev/nvme0n1p1 to /etc/fstab for persistent mounting at /media/nvme.
    Only appends if the entry does not already exist.
    Requires root permission to run blkid and modify /etc/fstab.
    """
    device = "/dev/nvme0n1p1"
    fstab_path = "/etc/fstab"

    try:
        # Get UUID and filesystem type using blkid
        blkid_output = subprocess.check_output(["sudo", "blkid", device], text=True)
        uuid_match = re.search(r'UUID="([^"]+)"', blkid_output)
        type_match = re.search(r'TYPE="([^"]+)"', blkid_output)

        if not uuid_match or not type_match:
            click.echo("❌ Could not extract UUID or TYPE from blkid output.")
            return

        uuid = uuid_match.group(1)
        fs_type = type_match.group(1)

        # Construct the fstab line
        fstab_entry = f"UUID={uuid}  /media/nvme  {fs_type}  defaults,noatime  0 0"

        # Check if entry already exists
        with open(fstab_path, "r") as f:
            for line in f:
                if uuid in line or "/media/nvme" in line:
                    click.echo("ℹ️  NVMe UUID or mount point already exists in /etc/fstab.")
                    return

        # Append the entry to fstab
        append_cmd = f"echo '{fstab_entry}' | sudo tee -a {fstab_path} > /dev/null"
        subprocess.run(append_cmd, shell=True, check=True)
        click.echo(f"✅ Added NVMe UUID entry to /etc/fstab:\n{fstab_entry}")

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to run blkid or append to fstab: {e}")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")

def mount_nvme():
    try:
        # Create mount point
        subprocess.run("sudo mkdir -p /media/nvme", shell=True, check=True)

        # Mount the NVMe partition
        subprocess.run("sudo mount /dev/nvme0n1p1 /media/nvme", shell=True, check=True)

        add_nvme_to_fstab()

        subprocess.run("sudo mount -a", shell=True, check=True)
        
        # Change ownership to user 'sima'
        subprocess.run("sudo chown sima:sima /media/nvme", shell=True, check=True)

        subprocess.run("sudo chmod 755 /media/nvme", shell=True, check=True)


        print("✅ NVMe mounted and write permission granted to user 'sima'.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error during NVMe mount: {e}")

def nvme_format():
    nvme_info = scan_nvme()
    if not nvme_info:
        click.echo("❌  No NVMe drive detected.")
        return
    click.echo(nvme_info)

    lbaf_index = get_lba_format_index()
    if lbaf_index is None:
        click.echo("❌  Failed to detect LBA format index.")
        return
    click.echo(f"ℹ️  Detected LBA format index: {lbaf_index}")

    if not click.confirm("⚠️  Are you sure you want to format /dev/nvme0n1? This will erase all data."):
        click.echo("❌ Aborted by user.")
        return

    try:
        # Unmount before formatting, ignore error if not mounted
        subprocess.run("sudo umount /media/nvme", shell=True, check=False)

        # Format and mount
        format_nvme(lbaf_index)
        mount_nvme()
        click.echo("✅  NVMe drive formatted and mounted at /media/nvme.")
    except subprocess.CalledProcessError:
        click.echo("❌ Formatting process failed.")


def nvme_remount():
    if not is_modalix_devkit():
        click.echo("❌ This command can only be run on the Modalix DevKit.")
        return

    try:
        mount_nvme()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to remount NVMe: {e}")
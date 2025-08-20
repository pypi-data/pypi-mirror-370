import os
import click
from sima_cli.utils.env import get_environment_type
from sima_cli.update.updater import perform_update
from sima_cli.model_zoo.model import list_models, download_model, describe_model
from sima_cli.utils.config_loader import internal_resource_exists
from sima_cli.mla.meminfo import monitor_simaai_mem_chart
from sima_cli.__version__ import __version__ 
from sima_cli.utils.config import CONFIG_PATH
from sima_cli.install.optiview import install_optiview
from sima_cli.install.hostdriver import install_hostdriver
from sima_cli.install.metadata_installer import install_from_metadata, metadata_resolver
from sima_cli.serial.serial import connect_serial
from sima_cli.storage.nvme import nvme_format, nvme_remount
from sima_cli.storage.sdcard import sdcard_format
from sima_cli.network.network import network_menu
from sima_cli.utils.pkg_update_check import check_for_update

# Entry point for the CLI tool using Click's command group decorator
@click.group()
@click.option('-i', '--internal', is_flag=True, help="Use internal Artifactory resources, Authorized Sima employees only")
@click.pass_context
def main(ctx, internal):
    """
    sima-cli – SiMa Developer Portal CLI Tool

    Global Options:
      --internal  Use internal Artifactory resources (can also be set via env variable SIMA_CLI_INTERNAL=1)
    """
    check_for_update('sima-cli')
    ctx.ensure_object(dict)

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    # Allow env override if --internal not explicitly passed
    if not internal:
        internal = os.getenv("SIMA_CLI_INTERNAL", "0") in ("1", "true", "yes")

    if internal and not internal_resource_exists():
        click.echo("❌ You have specified -i or --internal argument to access internal resources, but you do not have an internal resource map configured.")        
        click.echo("Refer to the confluence page to find out how to configure internal resource map.")
        exit(0)        

    ctx.obj["internal"] = internal

    env_type, env_subtype = get_environment_type()

    if internal:
        click.echo(f"🔧 Environment: {env_type} ({env_subtype}) | Internal: {internal}")
    else:
        click.echo(f"🔧 Environment: {env_type} ({env_subtype})")

# ----------------------
# Authentication Command
# ----------------------
@main.command()
@click.pass_context
def login(ctx):
    """Authenticate with the SiMa Developer Portal."""

    from sima_cli.auth import login as perform_login

    internal = ctx.obj.get("internal", False)
    perform_login.login("internal" if internal else "external")

# ----------------------
# Version Command
# ----------------------
@main.command(name="version")
def version_cmd():
    """Show the version of the CLI tool."""
    click.echo(f"SiMa CLI version: {__version__}")

# ----------------------
# Logout Command
# ----------------------
@main.command(name="logout")
@click.pass_context
def logout_cmd(ctx):
    """Log out by deleting cached credentials and config files."""
    sima_cli_dir = os.path.expanduser("~/.sima-cli")
    internal = ctx.obj.get("internal", False)
    deleted_any = False

    if not os.path.isdir(sima_cli_dir):
        click.echo("⚠️ No ~/.sima-cli directory found.")
        return

    if internal:
        target_files = ["config.json"]
    else:
        target_files = [".sima-cli-cookies.txt", ".sima-cli-csrf.json"]

    for filename in target_files:
        full_path = os.path.join(sima_cli_dir, filename)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                deleted_any = True
            except Exception as e:
                click.echo(f"⚠️ Failed to delete {full_path}: {e}", err=True)

    click.echo("✅ Logged out successfully.")

# ----------------------
# Download Command
# ----------------------
@main.command(name="download")
@click.argument('url')  # Accept both file and folder URLs
@click.option('-d', '--dest', type=click.Path(), default='.', help="Target download directory")
@click.pass_context
def download(ctx, url, dest):
    """Download a file or a whole folder from a given URL."""
    from sima_cli.download.downloader import download_file_from_url, download_folder_from_url

    internal = ctx.obj.get("internal", False)

    # First, try to download as a file
    try:
        click.echo("🔍 Checking if URL is a direct file...")
        path = download_file_from_url(url, dest, internal)
        click.echo(f"\n✅ File downloaded successfully to: {path}")
        return
    except Exception as e:
        click.echo(f"❌ Failed to download as file {e}")
        pass

    # If that fails, try to treat as a folder and download all files
    try:
        click.echo("🔍 Attempting folder download...")
        paths = download_folder_from_url(url, dest, internal)
        if not paths:
            raise RuntimeError("No files were downloaded.")
        click.echo(f"\n✅ Folder download completed. {len(paths)} files saved to: {dest}")
    except Exception as e:
        click.echo(f"\n❌ Failed to download as folder: {e}", err=True)

# ----------------------
# Update Command
# ----------------------
@main.command(name="update")
@click.argument('version_or_url')
@click.option('--ip', help="Target device IP address for remote firmware update.")
@click.option(
    '-y', '--yes',
    is_flag=True,
    help="Skip confirmation after firmware file is downloaded."
)
@click.option(
    '-p', '--passwd',
    default='edgeai',
    help="Optional SSH password for remote board (default is 'edgeai')."
)
@click.option("-f", "--flavor", type=click.Choice(["headless",  "full"], case_sensitive=False), default="headless", show_default=True, help="firmware flavor, full image supports NVMe, GUI on Modalix DevKit.")
@click.pass_context
def update(ctx, version_or_url, ip, yes, passwd, flavor):
    """
    Run system update across different environments.
    Downloads and applies firmware updates for PCIe host or SiMa board.

    version_or_url: The version string (e.g. '1.5.0') or a direct URL to the firmware package.
    """
    internal = ctx.obj.get("internal", False)
    perform_update(version_or_url, ip, internal, passwd=passwd, auto_confirm=yes, flavor=flavor)

# ----------------------
# Model Zoo Subcommands
# ----------------------
@main.group()
@click.option('--ver', default="1.6.0", show_default=True, help="SDK version, minimum and default is 1.6.0")
@click.pass_context
def modelzoo(ctx, ver):
    """Access models from the Model Zoo."""
    ctx.ensure_object(dict)
    ctx.obj['ver'] = ver
    internal = ctx.obj.get("internal", False)
    if not internal:
        click.echo(f"Public developer portal environment is not supported yet..")
        exit(0)

    pass

@modelzoo.command("list")
@click.pass_context
def list_models_cmd(ctx):
    """List available models."""
    internal = ctx.obj.get("internal", False)
    version = ctx.obj.get("ver")
    click.echo(f"Listing models for version: {version}")
    list_models(internal, version)

@modelzoo.command("get")
@click.argument('model_name') 
@click.pass_context
def get_model(ctx, model_name):
    """Download a specific model."""
    ver = ctx.obj.get("ver")
    internal = ctx.obj.get("internal", False)
    click.echo(f"Getting model '{model_name}' for version: {ver}")
    download_model(internal, ver, model_name)

@modelzoo.command("describe")
@click.argument('model_name') 
@click.pass_context
def get_model(ctx, model_name):
    """Download a specific model."""
    ver = ctx.obj.get("ver")
    internal = ctx.obj.get("internal", False)
    click.echo(f"Getting model '{model_name}' for version: {ver}")
    describe_model(internal, ver, model_name)

# ----------------------
# Authentication Command
# ----------------------
@main.group()
@click.pass_context
def mla(ctx):
    """Machine Learning Accelerator Utilities."""
    env_type, _ = get_environment_type()
    if env_type != 'board':
        click.echo("❌ This command can only be executed on the SiMa board.")
    pass

@mla.command("meminfo")
@click.pass_context
def show_mla_memory_usage(ctx):
    """Show MLA Memory usage overtime."""
    monitor_simaai_mem_chart()
    pass


# ----------------------
# bootimg Command
# ----------------------
@main.command(name="bootimg")
@click.option("-v", "--version", required=True, help="Firmware version to download and write (e.g., 1.6.0)")
@click.option("-b", "--boardtype", type=click.Choice(["modalix",  "mlsoc"], case_sensitive=False), default="mlsoc", show_default=True, help="Target board type.")
@click.option("-t", "--fwtype", type=click.Choice(["yocto",  "elxr"], case_sensitive=False), default="yocto", show_default=True, help="Target firmware type.")
@click.option("-n", "--netboot", is_flag=True, default=False, show_default=True, help="Prepare image for network boot and launch TFTP server.")
@click.option("-r", "--rootfs", required=False, help="Custom root fs folders (internal use only)")
@click.option("-a", "--autoflash", is_flag=True, default=False, show_default=True, help="Net boot the DevKit and automatically flash the internal storage - TBD")
@click.pass_context
def bootimg_cmd(ctx, version, boardtype, netboot, autoflash, fwtype, rootfs):
    """
    Download and burn a removable media or setup TFTP boot.

    Only supports headless image
    
    Examples:
      sima-cli bootimg -v 1.6.0
      sima-cli bootimg -v 1.6.0 --boardtype mlsoc
      sima-cli bootimg -v 1.6.0 --boardtype mlsoc
      sima-cli bootimg -v 1.6.0 --boardtype modalix --netboot
      sima-cli bootimg -v 1.6.0 --boardtype modalix --autoflash
    """

    from sima_cli.update.bootimg import write_image
    from sima_cli.update.netboot import setup_netboot

    internal = ctx.obj.get("internal", False)

    click.echo(f"📦 Preparing boot image:")
    click.echo(f"   🔹 Version   : {version}")
    click.echo(f"   🔹 Board Type: {boardtype}")
    click.echo(f"   🔹 F/W Type  : {fwtype}")
    click.echo(f"   🔹 F/W Flavor: headless")
    click.echo(f"   🔹 Custom RootFS: {rootfs}")
    
    try:
        boardtype = boardtype if boardtype != 'mlsoc' else 'davinci'
        if netboot or autoflash:
            setup_netboot(version, boardtype, internal, autoflash, flavor='headless', rootfs=rootfs)
            click.echo("✅ Netboot image prepared and TFTP server is running.")
        else:
            write_image(version, boardtype, fwtype, internal, flavor='headless')
            click.echo("✅ Boot image successfully written.")
        click.echo("✅ Boot image successfully written.")
    except Exception as e:
        click.echo(f"❌ Failed to write boot image: {e}", err=True)
        ctx.exit(1)

# ----------------------
# install Command
# ----------------------
SDK_DEPENDENT_COMPONENTS = {"palette", "hostdriver"}
SDK_INDEPENDENT_COMPONENTS = {"optiview"}
ALL_COMPONENTS = SDK_DEPENDENT_COMPONENTS | SDK_INDEPENDENT_COMPONENTS

@main.command(name="install")
@click.argument("component", required=False)
@click.option("-v", "--version", help="SDK version (required for SDK-dependent components unless --metadata is provided)")
@click.option("-m", "--mirror", help="URL to a metadata.json file for generic installation")
@click.option("-t", "--tag", help="Tag of the package (optional)")
@click.pass_context
def install_cmd(ctx, component, version, mirror, tag):
    """
    Install supported components such as SDKs, tools, or generic packages via metadata.

    Examples:

        sima-cli install hostdriver -v 1.6.0

        sima-cli install optiview

        sima-cli install -m https://custom-server/packages/foo/metadata.json

        sima-cli install samples/llima -v 1.7.0
    """
    internal = ctx.obj.get("internal", False)

    # Metadata-based installation path
    if mirror:
        if component:
            click.echo(f"⚠️ Component '{component}' is ignored when using --metadata. Proceeding with metadata-based installation.")
        click.echo(f"🔧 Installing generic component from metadata URL: {mirror}")
        if install_from_metadata(metadata_url=mirror, internal=internal):
            click.echo("✅ Installation complete.")
        return

    # No component and no metadata: error
    if not component:
        click.echo("❌ You must specify either a component name or provide --metadata.")
        ctx.exit(1)

    component = component.lower()

    # Validate version requirement
    if component in SDK_DEPENDENT_COMPONENTS and not version:
        click.echo(f"❌ The component '{component}' requires a specific SDK version. Please provide one using -v.")
        ctx.exit(1)

    if component in SDK_INDEPENDENT_COMPONENTS and version:
        click.echo(f"ℹ️ The component '{component}' does not require an SDK version. Ignoring -v {version}.")

    # Hardcoded component installation
    if component == "palette":
        click.echo(f"🔧 Installing SDK component 'palette' for version {version} is not implemented yet...")
    elif component == "hostdriver":
        click.echo(f"🔧 Installing SDK component 'hostdriver' for version {version}...")
        install_hostdriver(version=version, internal=internal)
    elif component == "optiview":
        click.echo("🔧 Installing tool 'optiview'...")
        install_optiview()
    else:
        # Case 4: Try to resolve metadata URL from version + tag
        try:
            metadata_url = metadata_resolver(component, version, tag)
            click.echo(f"🔧 Installing '{component}' from resolved metadata: {metadata_url}")
            if install_from_metadata(metadata_url=metadata_url, internal=internal):
                click.echo("✅ Installation complete.")
        except Exception as e:
            click.echo(f"❌ Failed to resolve metadata for component '{component}': {e}")
            ctx.exit(1)

    click.echo("✅ Installation complete.")


# ----------------------
# Serial Subcommands
# ----------------------
@main.command(name="serial")
@click.option("-b", "--baud", default=115200, show_default=True, help="Baud rate for the serial connection")
@click.pass_context
def serial_cmd(ctx, baud):
    """
    Connect to the UART serial console of the DevKit.

    Automatically detects the serial port and launches a terminal emulator:

    - macOS: uses 'picocom'
    
    - Linux: uses 'picocom'
    
    - Windows: shows PuTTY/Tera Term setup instructions
    """
    connect_serial(ctx, baud)

# ----------------------
# Network Subcommands
# ----------------------
@main.command(name="network")
@click.pass_context
def network_cmd(ctx):
    """
    Setup Network IP address on the DevKit

    This command only works on the DevKit. It allows user to switch between DHCP and Static (Default addresses) IP.

    """
    network_menu()

# ----------------------
# NVME Subcommands
# ----------------------
NVME_OPERATIONS = {"format", "remount"}
@main.command(name="nvme")
@click.argument("operation", type=click.Choice(NVME_OPERATIONS, case_sensitive=False))
@click.pass_context
def nvme_cmd(ctx, operation):
    """
    Perform NVMe operations on the Modalix DevKit.

    Available operations:

      format   - Format the NVMe drive and mount it to /media/nvme

      remount  - Remount the existing NVMe partition to /media/nvme

    Example:
      sima-cli nvme format

      sima-cli nvme remount
    """
    operation = operation.lower()

    if operation == "format":
        nvme_format()

    elif operation == "remount":
        try:
            nvme_remount()
        except Exception as e:
            click.echo(f"❌ Failed to remount NVMe drive: {e}")
            ctx.exit(1)

    else:
        click.echo(f"❌ Unsupported NVMe operation: {operation}")
        ctx.exit(1)

# ----------------------
# NVME Subcommands
# ----------------------
NVME_OPERATIONS = {"format"}
@main.command(name="sdcard")
@click.argument("operation", type=click.Choice(NVME_OPERATIONS, case_sensitive=False))
@click.pass_context
def sdcard_cmd(ctx, operation):
    """
    Prepare the SD Card as a data storage device for MLSoc DevKit or Modalix Early Access Unit

    Available operations:

      format   - Format the SD Card

    Example:
      sima-cli sdcard format
    """
    operation = operation.lower()

    if operation == "format":
        sdcard_format()



# ----------------------
# App Zoo Subcommands
# ----------------------
# @main.group()
# @click.pass_context
# def app_zoo(ctx):
#     """Access apps from the App Zoo."""
#     pass

# @app_zoo.command("list")
# @click.option('--ver', help="SDK version")
# @click.pass_context
# def list_apps(ctx, ver):
#     """List available apps."""
#     # Placeholder: Call API to list apps
#     click.echo(f"Listing apps for version: {ver or 'latest'}")

# @app_zoo.command("get")
# @click.argument('app_name')  # Required: app name
# @click.option('--ver', help="SDK version")
# @click.pass_context
# def get_app(ctx, app_name, ver):
#     """Download a specific app."""
#     # Placeholder: Download and validate app
#     click.echo(f"Getting app '{app_name}' for version: {ver or 'latest'}")

# ----------------------
# Entry point for direct execution
# ----------------------
if __name__ == "__main__":
    main()

import click
import getpass
import requests
from sima_cli.utils.config import set_auth_token, get_auth_token
from sima_cli.utils.config_loader import load_resource_config, artifactory_url
from sima_cli.utils.artifactory import exchange_identity_token, validate_token
from sima_cli.auth.basic_auth import login_external

def login(method: str = "external"):
    """
    Dispatch login based on the specified method.

    Args:
        method (str): 'external' (public developer portal) or 'internal' (Artifactory).
    """
    try:
        if method == "internal":
            return login_internal()
        else:
            return login_external()
    except Exception as e:
        print(f'Unable to login: {e}')

def login_internal():
    """
    Internal login using a manually provided identity token.

    Flow:
    1. Prompt for identity token.
    2. Validate the token using the configured validation URL.
    3. If valid, exchange it for a short-lived access token.
    4. Save the short-lived token to local config.
    """

    cfg = load_resource_config()
    auth_cfg = cfg.get("internal", {}).get("auth", {})
    base_url = artifactory_url()
    validate_url = auth_cfg.get("validate_url")
    internal_url = auth_cfg.get("internal_url")
    validate_url = f"{base_url}/{validate_url}"
    exchange_url = f"{base_url}/{internal_url}"

    # Check for required config values
    if not validate_url or not exchange_url:
        click.echo("❌ Missing 'validate_url' or 'internal_url' in internal auth config.")
        click.echo("👉 Please check ~/.sima-cli/resources_internal.yaml")
        return

    # Prompt for identity token
    click.echo("🔐 Paste your Artifactory identity token below.")
    identity_token = click.prompt("Identity Token", hide_input=True)

    if not identity_token or len(identity_token.strip()) < 10:
        return click.echo("❌ Invalid or empty token.")

    # Step 1: Validate the identity token
    is_valid, username = validate_token(identity_token, validate_url)
    if not is_valid:
        return click.echo("❌ Token validation failed. Please check your identity token.")

    click.echo(f"✅ Identity token is valid")

    # Step 2: Exchange for a short-lived access token (default: 7 days)
    access_token, user_name = exchange_identity_token(identity_token, exchange_url, expires_in=1209600)

    if not access_token:
        return click.echo("❌ Failed to acquire short-lived access token.")

    # Step 3: Save token to internal auth config
    set_auth_token(access_token, internal=True)
    click.echo(f"💾 Short-lived access token saved successfully for {user_name} (valid for 14 days).")


def _login_external():
    """
    External login using Developer Portal endpoint defined in the 'public' section of YAML config.
    Prompts for username/password and retrieves access token.
    """
    
    cfg = load_resource_config()
    auth_url = cfg.get("public", {}).get("auth", {}).get("auth_url")

    if not auth_url:
        click.echo("❌ External auth URL not configured in YAML.")
        return

    click.echo("🌐 Logging in using external Developer Portal...")

    # Prompt for credentials
    username = click.prompt("Email or Username")
    password = getpass.getpass("Password: ")

    data = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(auth_url, json=data)
        response.raise_for_status()

        token = response.json().get("access_token")
        if not token:
            return click.echo("❌ Failed to retrieve access token.")

        set_auth_token(token)
        click.echo("✅ External login successful.")

    except requests.RequestException as e:
        click.echo(f"❌ External login failed: {e}")

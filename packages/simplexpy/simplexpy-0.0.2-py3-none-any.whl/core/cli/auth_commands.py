import click
from simplex.core.auth.device_flow import get_access_token

@click.group()
@click.help_option('-h', '--help')
def auth_cli():
    """Authentication commands"""
    pass

@auth_cli.command()
@click.option("--no-browser", is_flag=True, help="Do not automatically open the login URL in a browser.")
def login(no_browser):
    """Log in using Device Authorization Flow"""
    from simplex.core.auth.device_flow import login as do_login
    do_login(auto_open_browser=not no_browser)

@auth_cli.command()
def logout():
    """Clear the access token"""
    from simplex.core.auth.device_flow import logout as do_logout
    do_logout()

@auth_cli.command()
def who_am_i():
    """Show login status"""
    try:
        token = get_access_token()
        print("✅ Token found")
        print(f"Access Token: {token}")
    except Exception as e:
        print(str(e))
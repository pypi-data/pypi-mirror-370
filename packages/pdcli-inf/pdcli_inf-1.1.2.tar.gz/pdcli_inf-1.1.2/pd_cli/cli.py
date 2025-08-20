
import click
from rich.console import Console
import os
import json
import subprocess
import configparser
import questionary
import boto3
CONFIG_DIR = os.path.expanduser("~/.pd-cli")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
CREDENTIALS_FILE_PATH = os.path.expanduser("~/.aws/credentials")
ENVIRONMENTS = ['test','staging','production']
DUO_MFA_OPTIONS = {
    'push': 'Duo Push',
    'pass': 'Passcode',
}
class PdCli:
    def __init__(self):
        self.console = Console()
        self.keys = None

    def load_keys(self):
        try:
            self.ensure_config_dir()
            self.console.print('Loading configuration...',CONFIG_FILE)
            with open(CONFIG_FILE, 'r') as f:
                content = json.load(f)
                self.keys = content
                return 1
        except Exception as e:
            self.console.print(f"[red]Error loading configuration: {str(e)}[/red]")
            return None
    def validate_dependencies(self):
        """Check if required CLI tools are installed"""
        missing_deps = self.check_dependencies()
        if missing_deps:
            self.console.print(f"[red]Error: Missing required dependencies: {', '.join(missing_deps)}[/red]")
            return False

        return True
    def check_dependencies(self):
        """Check if required CLI tools are installed"""
        dependencies = ['aws', 'saml2aws']
        missing_deps = []

        for dep in dependencies:
            try:
                # Using 'which' command on Unix-like systems or 'where' on Windows
                if os.name == 'nt':  # Windows
                    result = subprocess.run(['where', dep], capture_output=True, text=True)
                else:  # Unix-like
                    result = subprocess.run(['which', dep], capture_output=True, text=True)

                if result.returncode != 0:
                    missing_deps.append(dep)
            except Exception:
                missing_deps.append(dep)

        return missing_deps
    def ensure_config_dir(self):
        """Ensure ~/.pd-cli directory exists"""
        self.console.print('Ensuring configuration directory exists...',CONFIG_DIR)
        if not os.path.exists(CONFIG_DIR):
            self.console.print('Creating configuration directory...')
            os.makedirs(CONFIG_DIR)

    def read_saml2aws_config(self):
        """Read SAML2AWS configuration file"""
        try:
            config = configparser.ConfigParser()
            config_path = os.path.expanduser("~/.saml2aws")

            if not os.path.exists(config_path):
                self.console.print("[red]No SAML2AWS configuration file found[/red]")
                return None

            config.read(config_path)
            return config
        except Exception as e:
            self.console.print(f"[red]Error reading SAML2AWS configuration: {str(e)}[/red]")
            return None


    def load_config(self):
        """Load saved configuration"""
        if not os.path.exists(CONFIG_FILE):
            self.console.print("[yellow]No configuration found. Please run 'pdcli-inf config' first.[/yellow]")
            return None

        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.console.print(f"[red]Error loading configuration: {str(e)}[/red]")
            return None
    def login(self):
        if self.keys is None:
            self.load_keys()
        if self.keys['profile'] is None or self.keys['profile'] == '':
            self.console.print("[red]No profile found in configuration. Please run 'pdcli-inf config' first.[/red]")
            return
        cmd = [
            "aws","sso", "login",
            "--profile",
            self.keys['profile']
        ]

        # Execute saml2aws login
        # result = None
        result = subprocess.run(cmd, capture_output=True, text=True)
        # if duo_mfa_option == DUO_MFA_OPTIONS['push']:
        # elif duo_mfa_option == DUO_MFA_OPTIONS['pass']:
        #     result = subprocess.run(cmd, check=True)

        if result is None:
            raise Exception("Invalid Login option")

        if result.returncode != 0:
            raise Exception(f"SSO login failed: {result.stderr}")

        self.console.print(f"[green]Successfully logged in as {self.keys['profile']} ![/green]")

pd_cli:PdCli|None = None

@click.group()
def cli():
    """Enterprise CLI Tool"""
    global pd_cli
    pd_cli = PdCli()

@cli.command()
def list():
    """List all resources"""
    pd_cli.console.print("Listing resources...")

@cli.command()
def audit():
    """Validate dependencies"""
    if pd_cli.validate_dependencies():
        pd_cli.console.print("[green]All dependencies are installed[/green]")
    if not os.path.exists(CONFIG_DIR):
        pd_cli.console.print("[red]No configuration found. Please run 'pdcli-inf config' first.[/red]")
    if pd_cli.keys is None:
        pd_cli.console.print("[red]No configuration found. Please run 'pdcli-inf config' first.[/red]")
    config_saml = pd_cli.read_saml2aws_config()
    if config_saml is None:
        pd_cli.console.print("[red]No SAML2AWS configuration found. Please run 'pdcli-inf config' [/red]")
    if config_saml['default'].get('role_arn') is None:
        pd_cli.console.print("[red]No role_arn found in SAML2AWS configuration. Please run 'pdcli-inf config' [/red]")

@cli.command()
@click.option('--secret-id',
              default='',
              prompt='Enter Secret Manager ARN',
              help='AWS Secrets Manager ARN')
@click.option('--region',
              default='us-east-2',
              prompt='Enter AWS Region',
              help='AWS Region')
def config(secret_id,region):
    """Fetch and store Secrets Manager configuration locally"""
    try:
        # config_saml = pd_cli.read_saml2aws_config()
        # cmd = [
        #     'saml2aws', 'configure'
        # ]
        # if config_saml is None:
        #     result = subprocess.run(cmd, check=True)
        #
        # if config_saml['default'].get('role_arn') is None:
        #     result = subprocess.run(cmd, check=True)
        #
        # if secret_id == '':
        #     pd_cli.console.print("[red]Error: Secret ID cannot be empty. Please run 'pdcli-inf config' [/red]")
        #     return
        #
        # # Ensure config directory exists
        # pd_cli.ensure_config_dir()
        #
        # pd_cli.console.print(f"[yellow]Fetching configuration from Secret Manager...[/yellow]")

        # Initialize AWS Secrets Manager client
        session = boto3.Session(region_name=region)
        secrets_client = session.client('secretsmanager')

        try:
            # Get secret value
            response = secrets_client.get_secret_value(SecretId=secret_id)
            secret_content = json.loads(response['SecretString'])

            # Save configuration locally
            config_data = {
                'secret_id': secret_id,
                'region': region,
                'profile': '',
                'connections': secret_content
            }

            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=2)

            pd_cli.console.print(f"[green]Configuration successfully saved to {CONFIG_FILE}[/green]")

            # Show summary of saved configuration
            pd_cli.console.print("\n[blue]Configuration Summary:[/blue]")
            pd_cli.console.print(f"Secret ID: {secret_id}")
            pd_cli.console.print(f"Region: {region}")
            if 'ssh' in secret_content:
                pd_cli.console.print("SSH Services:", ", ".join(secret_content['ssh']['services'].keys()))
            if 'database' in secret_content:
                pd_cli.console.print("Database Services:", ", ".join(secret_content['database']['services'].keys()))

        except secrets_client.exceptions.ResourceNotFoundException:
            pd_cli.console.print(f"[red]Error: Secret {secret_id} not found[/red]")
        except secrets_client.exceptions.InvalidParameterException:
            pd_cli.console.print(f"[red]Error: Invalid Secret ID format[/red]")
        except Exception as e:
            pd_cli.console.print(f"[red]Error accessing Secret Manager: {str(e)}[/red]")

    except Exception as e:
        pd_cli.console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.option('--duo-mfa-option', default=DUO_MFA_OPTIONS['push'], help='Duo MFA option')
@click.option('--role',default='', help='AWS role ARN')
def login(duo_mfa_option, role):
    """Login using saml2aws and configure credentials"""
    try:
        # Print shell information
        pd_cli.console.print(f"Running SSO login...")
        # config_saml=pd_cli.read_saml2aws_config()
        # if config_saml["default"].get('role_arn') is not None:
        #     pd_cli.console.print('Theres is a global config')
        #     role=config_saml["default"].get('role_arn')
        #     pd_cli.console.print(f'Role: {role}')
        #     pd_cli.console.print(f'Duo MFA Option: {duo_mfa_option}')
        #     pd_cli.console.print('If you want to change the MFA option, you can do it with the --duo-mfa-option flag')
        pd_cli.login()
    except Exception as e:
        pd_cli.console.print(f"[red]Error during login: {str(e)}[/red]")
        return 1

    return 0


@cli.command()
def connect():
    pd_cli.load_keys()
    pd_cli.console.print("Connecting to AWS...")

    service = questionary.select(
        "Select a service",
        choices=[
            "Database",
            "SSH"
        ]
    ).ask()

    if not service:
        pd_cli.console.print("[red]No service selected[/red]")
        return

    list_instances = [service for service in pd_cli.keys['connections']['database']['services'].keys()] if service == "Database" else [ service for service in pd_cli.keys['connections']['ssh']['services'].keys()]
    instance = questionary.select(
        "Select an instance",
        choices=list_instances
    ).ask()

    if not instance:
        pd_cli.console.print("[red]No instance selected[/red]")
        return

    environment = questionary.select(
        "Select an environment",
        choices=ENVIRONMENTS
    ).ask()

    if not environment:
        pd_cli.console.print("[red]No environment selected[/red]")
        return

    if pd_cli.keys is None:
        pd_cli.load_keys()
    keys = pd_cli.keys['connections']
    if service == "Database":
        host = keys["database"]["services"][instance]["hosts"][environment]
        local_port = keys["database"]["services"][instance]["ports"][environment]
        remote_port = keys["database"]["services"][instance]["ports"]["local"]
        instance_tunnel_id = keys["database"]["services"][instance]["instances"][environment]
        secret = keys["database"]["services"][instance]["secrets"][environment]
        pd_cli.console.print(f"Connecting to database {instance} in {environment} environment...")
        pd_cli.console.print(f"Host: {host}")
        pd_cli.console.print(f"Local Port: {local_port}")
        pd_cli.console.print(f"Remote Port: {remote_port}")
        pd_cli.console.print(f"Tunnel Instance ID: {instance_tunnel_id}")
        parameters = f'host="{host}",portNumber="{remote_port}",localPortNumber="{local_port}"'

        manual_command = f'aws ssm start-session --target {instance_tunnel_id} --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters {parameters} --profile {pd_cli.keys["profile"]}'
        result = subprocess.run(manual_command,shell=True,capture_output=False)
        if result.returncode != 0:
            pd_cli.console.print(f"[red]Error starting tunnel: {result.stderr}[/red]")
            return 1
        pd_cli.console.print(f"[green]Tunnel started successfully![/green]")
    elif service == "SSH":

        instance_id = keys["ssh"]["services"][instance]["instances"][environment]
        pd_cli.console.print(f"Connecting to SSH instance {instance} in {environment} environment...")
        pd_cli.console.print(f"Instance ID: {instance_id}")
        cmd = [
            "aws", "ssm", "start-session",
            "--target", instance_id,
            "--profile", pd_cli.keys['profile']
        ]
        result = subprocess.run(cmd, check=True)
        if result.returncode != 0:
            pd_cli.console.print(f"[red]Error starting session: {result.stderr}[/red]")
            return 1
        pd_cli.console.print(f"[green]Session started successfully![/green]")


if __name__ == '__main__':
    cli()
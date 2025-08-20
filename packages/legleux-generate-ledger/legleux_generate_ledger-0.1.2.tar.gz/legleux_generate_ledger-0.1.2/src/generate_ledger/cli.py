import sys
from generate_ledger.gen import write_ledger_file
from generate_ledger.compose import generate_compose_file
from generate_ledger.rippled_config import generate_config
import click
import os
from platformdirs import user_config_path
from generate_ledger.utils import get_config_file
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("generate_ledger")
    __name__ = "generate_ledger"
except PackageNotFoundError:
    __version__ = "0.0.0"
cfg_path = get_config_file("generate_ledger")
# print("Config will live at:", cfg_path)

# This gives you the right base path for configs on Linux/macOS/Windows
# config_path = user_config_path("myapp", appauthor=False) / "config.yaml"


DEFAULT_NUM_VALIDATORS = 5
DEFAULT_NUM_ACCOUNTS   = 20
DEFAULT_NUM_VALIDATORS = os.environ.get("NUM_VALIDATORS", DEFAULT_NUM_VALIDATORS)
DEFAULT_NUM_ACCOUNTS   = os.environ.get("NUM_ACCOUNTS", DEFAULT_NUM_ACCOUNTS)
DEFAULT_NETWORK_NAME   = os.environ.get("NETWORK_NAME", "xrpld_net")

def compose(num_validators, network_name, include_services):
    # print("Generating compose.yml")
    generate_compose_file(num_validators, network_name, include_services)
    # print("Generated compose.yml")

def ledger(num_accounts):
    # print("Generating ledger.json")
    write_ledger_file(num_accounts)

def config():
    # print("Generating rippled.cfg")
    generate_config()

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-n", "--network_name", default=DEFAULT_NETWORK_NAME, type=str)
@click.option("-v", "--num_validators", default=DEFAULT_NUM_VALIDATORS, type=int)
@click.option("-s", "--include_services", multiple=True)
@click.option("-a", "--num_accounts", default=DEFAULT_NUM_ACCOUNTS, type=int)
@click.option("--config_only", default=True)
def main(num_validators, network_name, include_services, num_accounts, config_only):

    compose(num_validators, network_name, include_services)
    generate_config(num_validators)
    if not config_only:
        write_ledger_file(num_accounts)

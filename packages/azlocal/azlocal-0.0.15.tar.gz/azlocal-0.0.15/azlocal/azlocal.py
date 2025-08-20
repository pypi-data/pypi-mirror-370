#!/usr/bin/env python

"""
Thin wrapper around the "az" command line interface (CLI) for use
with LocalStack.

The "azlocal" CLI allows you to easily interact with your local Azure services
without having to configure anything.

Example:
Instead of the following command ...
HTTPS_PROXY=... REQUESTS_CA_BUNDLE=... az storage account list
... you can simply use this:
azlocal storage account list

Options:
  Run "azlocal help" for more details on the Azure CLI subcommands.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

from .constants import AZURE_CONFIG_DIR_ENV
from .shared import prepare_environment, get_proxy_endpoint, get_proxy_env_vars, AZURE_CONFIG_DIR, run_in_background


DEFAULT_CLOUD_NAME = "AzureCloud"
CUSTOM_CLOUD_NAME = "LocalStack"

LOG = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'WARNING').upper(),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


def usage():
    print(__doc__.strip())


def run_in_current_process(cmd, env = None):
    """
    Replaces this process with the AZ CLI process, with the given command and environment
    """
    os.execvpe(cmd[0], cmd, env)


def run(cmd, hide_errors: bool = False):
    LOG.debug(f"Executing {cmd}...")
    process = subprocess.run(cmd, capture_output = True)
    if process.stdout:
        LOG.debug(f"Output of {cmd}:")
        LOG.debug(process.stdout)
    if process.stderr and not hide_errors:
        if process.stderr.startswith(b"WARNING"):
            LOG.warning(process.stderr)
        else:
            LOG.error(f"Error while running {cmd}:")
            LOG.error(process.stderr)
    return process.returncode


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        usage()

    if len(sys.argv) > 1 and sys.argv[1] == "start_interception":
        use_custom_cloud()
    elif len(sys.argv) > 1 and sys.argv[1] == "stop_interception":
        use_regular_cloud()
    else:
        # Backwards compatibility
        # The user could invoke the CLI as if it were an 'az' replacement:
        #    azlocal group list
        # If that's the case, we redirect the existing 'az' command via a proxy to our Emulator
        run_as_separate_process()


def use_custom_cloud():
    # Create the CustomCloud first
    create_custom_cloud()
    # Configure the CLI to use our CustomCloud
    run(["az", "cloud", "set", "--name", CUSTOM_CLOUD_NAME])
    LOG.info(f"AZ CLI now uses CustomCloud={CUSTOM_CLOUD_NAME}")
    # Our endpoint is not whitelisted, so we need to disable the endpoint validation
    run(["az", "config", "set", "core.instance_discovery=false"])
    # Login
    run(["az", "login", "--service-principal", "-u", "any-app", "-p", "any-pass", "--tenant", "anytenant"])
    LOG.info(f"AZ CLI is now logged in against CustomCloud={CUSTOM_CLOUD_NAME}")


def use_regular_cloud():
    # Configure the endpoint to use the default cloud
    run(["az", "cloud", "set", "--name", DEFAULT_CLOUD_NAME])
    # Re-enable instance discovery
    run(["az", "config", "set", "core.instance_discovery=true"])
    LOG.info(f"AZ CLI now uses Cloud={DEFAULT_CLOUD_NAME}")


def create_custom_cloud():
    custom_cloud_return_code = run(["az", "cloud", "show", "--name", CUSTOM_CLOUD_NAME], hide_errors=True)
    if custom_cloud_return_code == 0:
        # Exists
        return

    emulator_endpoint = os.environ.get("LOCALSTACK_HOST") or 'https://localhost.localstack.cloud:4566'
    # We currently only register the four necessary endpoints
    # We may want to expand this in the future and also register data plane endpoints
    # For example '--suffix-keyvault-dns' or '--suffix-storage-endpoint'
    run(["az", "cloud", "register", "--name", CUSTOM_CLOUD_NAME,
         "--endpoint-resource-manager", emulator_endpoint,
         "--endpoint-management", emulator_endpoint,
         "--endpoint-active-directory", emulator_endpoint,
         "--endpoint-active-directory-resource-id", emulator_endpoint])
    LOG.info(f"Created CustomCloud={CUSTOM_CLOUD_NAME}")


def run_as_separate_process():
    """
    Constructs a command line string and calls "az" as an external process.
    """

    cmd_args = list(sys.argv)
    cmd_args[0] = 'az'
    if ("--help" in cmd_args) or ("--version" in cmd_args):
        # Early exit - if we only want to know the version/help, we don't need LS to be running
        run_in_current_process(cmd_args, None)
        return

    proxy_endpoint = get_proxy_endpoint()

    env_dict = prepare_environment(proxy_endpoint)

    env_dict[AZURE_CONFIG_DIR_ENV] = AZURE_CONFIG_DIR
    if not os.path.exists(AZURE_CONFIG_DIR):
        # Create the config directory
        Path(AZURE_CONFIG_DIR).mkdir(parents=True, exist_ok=True)

        # Prepare necessary arguments to ensure `az ..` commands are run against this config directory
        az_args_list = [f"{key}={val}" for key, val in get_proxy_env_vars(proxy_endpoint).items()]
        az_args_list.append(f"{AZURE_CONFIG_DIR_ENV}={AZURE_CONFIG_DIR}")
        az_arg = " ".join(az_args_list)

        # Turn off telemetry
        survey_command = f"{az_arg} az config set output.show_survey_link=no"
        run_in_background(survey_command)
        telemetry_command = f"{az_arg} az config set core.collect_telemetry=false"
        run_in_background(telemetry_command)

        # Login to ensure the config directory has credentials
        login_command = f"{az_arg} az login --service-principal -u any-app -p any-pass --tenant any-tenant"
        run_in_background(login_command)

    # Hijack the login command
    # When creating our custom config dir, we automatically log in - so this is not necessary anymore
    if len(cmd_args) == 2 and cmd_args[1] == "login":
        print("Login Succeeded")
        return

    # Hijack the ACR login command
    if len(cmd_args) > 1 and cmd_args[1] == "acr" and "login" in cmd_args:
        print("Login Succeeded")
        return

    # run the command
    run_in_current_process(cmd_args, env_dict)


if __name__ == '__main__':
    main()

#!/usr/bin/env python

"""
Thin wrapper around the "terraform" command line interface (CLI) for use
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

import os
import sys
from pathlib import Path

from .constants import AZURE_CONFIG_DIR_ENV
from .shared import AZURE_CONFIG_DIR, check_proxy_is_running, get_proxy_endpoint, prepare_environment, run_in_background


def usage():
    print(__doc__.strip())


def run(cmd, env):
    """
    Replaces this process with the Terraform CLI process, with the given command and environment
    """
    os.execvpe(cmd[0], cmd, env)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        return usage()
    run_as_separate_process()


def run_as_separate_process():
    """
    Constructs a command line string and calls "terraform" as an external process.
    """

    cmd_args = list(sys.argv)
    cmd_args[0] = 'terraform'
    if ("--help" in cmd_args) or ("version" in cmd_args):
        # Early exit - if we only want to know the version/help, we don't need LS to be running
        run(cmd_args, None)
        return

    proxy_endpoint = get_proxy_endpoint()
    check_proxy_is_running(proxy_endpoint)

    if "init" not in cmd_args:
        # Init downloads all dependencies - no point in going through our proxy
        env_dict = prepare_environment(proxy_endpoint)
    else:
        env_dict = os.environ

    # Configure a custom configuration directory
    env_dict[AZURE_CONFIG_DIR_ENV] = AZURE_CONFIG_DIR
    if not os.path.exists(AZURE_CONFIG_DIR):
        # Create the config directory
        Path(AZURE_CONFIG_DIR).mkdir(parents=True, exist_ok=True)

        args_list = [f"{key}={val}" for key, val in env_dict.items()]
        args_list.append(f"{AZURE_CONFIG_DIR_ENV}={AZURE_CONFIG_DIR}")
        args = " ".join(args_list)

        # Initial login to ensure auth details are part of the configuration
        login_command = f"{args} az login --service-principal -u any-app -p any-pass --tenant any-tenant"
        run_in_background(login_command)

    # run the command
    run(cmd_args, env_dict)


if __name__ == '__main__':
    main()

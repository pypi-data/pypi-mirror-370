#!/usr/bin/env python

"""
Thin wrapper around the "func" command line interface (CLI) for use
with LocalStack.

The "funclocal" CLI allows you to easily spin up your IaC against LocalStack
without having to configure anything.

Example:
Instead of the following command ...
HTTPS_PROXY=... SSL_CERT_FILE=... func init
... you can simply use this:
funclocal init

Options:
  Run "funclocal help" for more details on the Azure CLI subcommands.
"""

import os
import sys

from .shared import check_proxy_is_running, get_proxy_endpoint, prepare_environment


def usage():
    print(__doc__.strip())


def run(cmd, env):
    """
    Replaces this process with the AZ CLI process, with the given command and environment
    """
    os.execvpe(cmd[0], cmd, env)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        return usage()
    run_as_separate_process()


def run_as_separate_process():
    """
    Constructs a command line string and calls "az" as an external process.
    """

    cmd_args = list(sys.argv)
    cmd_args[0] = 'func'
    if ("help" in cmd_args) or ("version" in cmd_args):
        # Early exit - if we only want to know the version/help, we don't need LS to be running
        run(cmd_args, None)
        return

    proxy_endpoint = get_proxy_endpoint()
    check_proxy_is_running(proxy_endpoint)

    env_dict = prepare_environment(proxy_endpoint)

    # run the command
    run(cmd_args, env_dict)


if __name__ == '__main__':
    main()

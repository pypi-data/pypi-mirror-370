import logging
import os
import sys
import inspect
import warnings
from pathlib import Path
from time import time

ENV_AZURE_AUTHORITY_HOST = "AZURE_AUTHORITY_HOST"

LOG = logging.getLogger(__name__)


def get_custom_host() -> str:
    return os.environ.get("LS_HOST") or "https://localhost.localstack.cloud:4566"


class PythonLocalSdk:

    def __init__(self):
        self._started = False

        self._clients_to_mock = self._find_azure_mgmt_clients()
        self._default_worldwide_endpoint: str | None = None
        self._existing_authority_host: str | None = None

    def start_interception(self):
        """
        Start intercepting all Azure requests.

         Invoking this method will:
          - inspect the current modules
          - load all `azure.mgmt` modules
          - find the latest client in every module
          - update the client to point to the LocalStack host

        Use the environment variable `LS_HOST` to configure the host.

        .. warning
              This only affects Clients that are created after this method is invoked

        :return:
        """
        if self._started:
            return

        # Set custom login endpoint
        # There are two ways that Azure SDK Clients determine which endpoint to call to login:
        #  - Using an environment variable
        #  - Using hardcoded values in the 'msal' module
        # Which method is used depends on the SDK, so we override both to be sure
        self._existing_authority_host = os.environ.get(ENV_AZURE_AUTHORITY_HOST)
        os.environ[ENV_AZURE_AUTHORITY_HOST] = get_custom_host()
        try:
            from msal import authority

            self._default_worldwide_endpoint = authority.WORLD_WIDE
            authority.WORLD_WIDE = get_custom_host().replace("https://", "")
        except ImportError:
            warnings.warn("Unable to import 'msal' - Authorization calls will not be intercepted")

        # Use Custom Client
        for client in self._clients_to_mock:
            self.prepare_client_for_interception(client)

    def stop_interception(self):
        if not self._started:
            return

        # Instrument client to stop interception
        for client in self._clients_to_mock:
            self.revert_client_interception(client)

        # Revert the login endpoints
        if self._existing_authority_host:
            os.environ[ENV_AZURE_AUTHORITY_HOST] = self._existing_authority_host
        if self._default_worldwide_endpoint:
            from msal import authority

            authority.WORLD_WIDE = self._default_worldwide_endpoint

        self._started = False

    def _find_azure_mgmt_clients(self) -> list:
        """
        Finds a list of all SDK clients that are defined in the `azure.mgmt` namespace.

        :return: A list of classes: [CosmosManagementClient, StorageManagementClient, ..]
        """

        from azure import mgmt  # noqa
        azure_mod = sys.modules["azure.mgmt"]
        azure_path = azure_mod.__path__

        clients = []

        total_start_time = time()

        for p in azure_path:
            mgmt_modules = sorted(os.listdir(p))

            for module_name in mgmt_modules:
                module_start_time = time()
                module = __import__(f"azure.mgmt.{module_name}", fromlist=["__init__"])
                LOG.debug(f"PythonSDK: importing %s took: \t%s s", module_name, (time() - module_start_time))

                if hasattr(module, '__all__'):
                    for attr_name in module.__all__:
                        if attr_name.endswith("Client"):
                            clients.append(getattr(module, attr_name))
                else:
                    # some modules (datalake, rdbms, maybe others) use have several clients in subdirectories
                    sub_modules = sorted(os.listdir(os.path.join(p, module_name)))

                    for submodule_name in sub_modules:
                        if not Path(os.path.join(p, module_name, submodule_name)).is_dir():
                            continue
                        submodule = __import__(f"azure.mgmt.{module_name}.{submodule_name}", fromlist=["__init__"])

                        if hasattr(submodule, '__all__'):
                            for attr_name in submodule.__all__:
                                if attr_name.endswith("Client"):
                                    clients.append(getattr(submodule, attr_name))

        LOG.debug(f"PythonSDK: finding all clients took \t%s s", (time() - total_start_time))

        return clients

    @staticmethod
    def prepare_client_for_interception(client) -> None:
        # There are three ways for a client to determine which endpoint to call
        # 1. Provided by the user: AzureServiceClient(base_url="..")
        # 2. Determined by the AzureCloud that is configured (env variable AZURE_CLOUD=AZURE_PUBLIC_CLOUD/AZURE_CHINA_CLOUD
        # 3. Use a hardcoded default
        #
        # Solutions:
        # 1. Asking the user to configure the base_url manually. Very laborious and prone to errors
        # 2. Override the AzureCloud. This is not feasible for a few reasons:
        #    - We can pass in an env variable, but there are only three Azure Clouds (Public/US GOV/China)
        #    - We cannot override the available AzureClouds, as that is an Enum (which is immutable by design)
        #    - We cannot override the method used to determine the endpoint
        #      1. Location of this method: from azure.mgmt.core.tools import get_arm_endpoints
        #      2. This is typically already imported at the top, so each client already has a direct reference to the `get_arm_endpoints` method.
        #         Overriding the method in the `azure.mgmt.core.tools`-module has therefore no effect.
        #
        # 3. We _can_ override the hardcoded default - which is what we do here

        # Determine (and store) the existing default values for the `__init__`-method
        # This is either None or a tuple
        # If a parameter does not have a default value, it is not part of the tuple - so the length of this list is not guaranteed the same as the number of parameters
        # __init__(a, b = None, c = "sth") --> _defaults__ == (None, "sth")
        client.__init__.__olddefaults = client.__init__.__defaults__

        if not client.__init__.__olddefaults:
            return

        # Get the default values as a dictionary
        # We skip the 'empty' Parameters, so parameters without a default value
        # __init__(a, b = None, c = "sth") --> [("b", None), ("c", "sth")]
        client_signature = inspect.signature(client.__init__)
        init_params = [(name, value.default) for name, value in client_signature.parameters.items() if value.default != inspect.Parameter.empty]

        # Construct our own tuple of default values, only overriding the `base_url`
        updated_default_values = tuple(get_custom_host() if name == "base_url" else value for name, value in init_params)

        client.__init__.__defaults__ = updated_default_values

    @staticmethod
    def revert_client_interception(client) -> None:
        client.__init__.__defaults__ = client.__init__.__olddefaults

import json
import os
import tempfile
import subprocess
import urllib.error
import urllib.request
from typing import Optional
from pathlib import Path

import certifi


HOME_DIR = Path.home()
AZURE_DIR = os.path.join(HOME_DIR, ".localstack/azure")
AZURE_CONFIG_DIR = os.path.join(AZURE_DIR, "az_config")

if not os.path.exists(AZURE_DIR):
    Path(AZURE_DIR).mkdir(parents=True, exist_ok=True)


def get_proxy_endpoint() -> str:
    ls_host = os.environ.get("LOCALSTACK_HOST") or 'http://localhost:4566'
    with urllib.request.urlopen(f"{ls_host}/_localstack/proxy") as req:
        proxy_details = json.loads(req.read().decode("utf-8"))
        proxy_port = proxy_details["proxy_port"]
    return f'http://localhost:{proxy_port}'


def get_default_proxy_certificate_location(proxy_endpoint):
    certificate_path = os.path.join(AZURE_DIR, "ca.crt")
    if not os.path.exists(certificate_path):
        certificate_bytes = _get_certificate_bytes(proxy_endpoint)
        Path(certificate_path).write_bytes(certificate_bytes)
    return certificate_path


def get_custom_proxy_certificate_location(proxy_endpoint) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(_get_certificate_bytes(proxy_endpoint))
    return tmp.name


def _get_certificate_bytes(proxy_endpoint: str) -> bytes:
    # Stock CA certificates
    certificate_bytes = Path(certifi.where()).read_bytes()

    # Custom CA certificate
    with urllib.request.urlopen(f"{proxy_endpoint}/_localstack/certs/ca/LocalStack_LOCAL_Root_CA.crt") as cert:
        certificate_bytes += cert.read()
    return certificate_bytes


def check_proxy_is_running(proxy_endpoint: str):
    try:
        assert urllib.request.urlopen(f"{proxy_endpoint}/_localstack/health").status == 200
    except (AssertionError, urllib.error.URLError) as e:
        raise Exception("Make sure LocalStack is running")


def prepare_environment(proxy_endpoint: str):
    # prepare env vars
    env_dict = os.environ.copy()
    env_dict.update(get_proxy_env_vars(proxy_endpoint))

    # update environment variables in the current process
    os.environ.update(env_dict)
    return env_dict



def get_proxy_env_vars(proxy_endpoint: str, certificate_path: Optional[str] = None):
    certificate_path = certificate_path or get_default_proxy_certificate_location(proxy_endpoint)

    return {
        "HTTP_PROXY": proxy_endpoint,
        "HTTPS_PROXY": proxy_endpoint,
        "REQUESTS_CA_BUNDLE": certificate_path,
        "SSL_CERT_FILE": certificate_path,
    }


def run_in_background(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()
    log_az_output(p)


def log_az_output(p):
    for line in p.stdout.readlines():
        # TODO: Log this cleanly
        #  Just not to stdout, as we should only print the output of the actual command that the user runs
        pass

from typing import List
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv, find_dotenv
import re

secrets_regexp = re.compile(r"^\${(.+)}")

load_dotenv(find_dotenv())


def get_secret(name: str, key_vault: str) -> str:
    """Get a secret from Azure Key Vault"""
    credential = DefaultAzureCredential()
    client = SecretClient(key_vault, credential)
    secret = client.get_secret(name)
    return secret.value


def get_secrets(secrets: List[dict]) -> dict:
    """Converts list of dicts with secret name and keyvault to dict with secrets"""
    return {
        secret["alias"]
        if secret.get("alias")
        else secret["name"]: get_secret(secret["name"], secret["keyVault"])
        for secret in secrets
    }


# Eval and lookup config secrets, e.g ${akv;<secret>;<keyvault>}
def set_config_secrets(config: dict):
    return eval_secrets(secrets_regexp, config)


def eval_secrets(compiled_regexp, config):
    if isinstance(config, dict):
        return {k: eval_secrets(compiled_regexp, v) for k, v in config.items()}
    elif isinstance(config, list):
        return [eval_secrets(compiled_regexp, i) for i in config]
    elif isinstance(config, str):
        return eval_single_secret(config)
    else:
        return config


# Secret format: ${akv;<secret>;<keyvault>}
def eval_single_secret(input: str) -> str:
    matches = secrets_regexp.findall(input)
    for match in matches:
        secrets_part = match.split(";")
        try:
            provider = secrets_part[0].strip()
            key = secrets_part[1].strip()
            vault = secrets_part[2].strip()
            if provider == "akv":
                return get_secret(key, vault)
            return f'Secret: "{input}" is incorrect configured. Format=<akv;secretName;keyvault>'
        except Exception as e:
            return f"Exception: {e} - Incorrect configured secret. Use <akv;secretName;keyvault>"
    return input


def test_get_secrets():
    json_secrets = [
        {
            "name": "tamDbUrl",
            "keyVault": "https://kv-bin-shared.vault.azure.net/",
            "alias": "dbUri",
        }
    ]
    secrets = get_secrets(json_secrets)
    assert (
        "@sqlsrv-tam-test.database.windows.net/sqldb-tam-test" in secrets["dbUri"]
    ), "Secret fetch failed"

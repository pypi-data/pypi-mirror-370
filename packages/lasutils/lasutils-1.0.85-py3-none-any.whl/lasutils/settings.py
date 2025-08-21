import json
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import yaml

load_dotenv(find_dotenv())


class ConnectorSettings:
    def __init__(self) -> None:
        print("Setting init")

    def load_settings(self, yaml_file: str):
        settings = yaml.safe_load(open(Path(yaml_file)).read())
        os.environ["CONNECTOR_CLASS"] = settings["spec"]["class"]
        if settings["spec"].get("config"):
            os.environ["CONFIG"] = json.dumps(settings["spec"]["config"])
        if settings["spec"].get("secrets"):
            os.environ["SECRETS"] = json.dumps(settings["spec"]["secrets"])

    @property
    def las_user(self):
        return os.getenv("LAS_USER")

    @property
    def las_pwd(self):
        return os.getenv("LAS_PWD")

    @property
    def connector_class(self):
        return os.getenv("CONNECTOR_CLASS")

    @property
    def config(self):
        return json.loads(os.getenv("CONFIG"))

    @property
    def secrets(self):
        return os.getenv("SECRETS")


# # LAS Auth
# LAS_USER = os.getenv("LAS_USER")
# LAS_PWD = os.getenv("LAS_PWD")

# # External Auth
# EXT_USER = os.getenv("EXT_USER")
# EXT_PWD = os.getenv("EXT_PWD")

# POLLER_CLASS = os.getenv("POLLER_CLASS")
# CONFIG = json.loads(os.getenv("CONFIG")) if os.getenv("CONFIG") else None
# SECRETS = json.loads(os.getenv("SECRETS")) if os.getenv("SECRETS") else None

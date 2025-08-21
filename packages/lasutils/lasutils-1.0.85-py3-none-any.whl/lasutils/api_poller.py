import logging
import signal
from typing import OrderedDict
import requests
from requests import HTTPError
import json
from collections import abc
from abc import ABC, abstractmethod
from importlib import import_module
from time import sleep

from lasutils import settings
from lasutils.deserializer import Deserializer, NoDeserializer, create_deserializer
from lasutils.helpers import MissingEnvironmentVariable, get_nested

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# API config names
CONF_API_TYPE = "api.type"
CONF_API_FORMAT = "api.format"
CONF_API_BASEURL = "api.url"
CONF_API_DATA_PATH = "api.dataPath"

# AUTH config names
CONF_API_AUTH_TOKEN_URL = "auth.token.url"
CONF_API_AUTH_TOKEN_NAME = "auth.token.name"
CONF_API_AUTH_CONTENT_TYPE = "auth.content.type"
CONF_API_AUTH_PAYLOAD = "auth.payload"


# SOAP config names
CONF_SOAP_ACTION = "api.soapAction"
CONF_SOAP_ACTION_PARAMS = "api.soapActionParams"
CONF_SOAP_ACTION_NS = "api.soapActionNamespace"


# API poller abstract class with some basic initialization.
class ApiPoller(ABC):
    def __init__(self, auth_config: dict, api_config: dict):
        self._api_config = api_config
        self._auth_config = auth_config

        self._deserializer = create_deserializer(api_config.get(CONF_API_FORMAT))

        self._header = {}
        self.set_header_field("charset", "utf-8")
        self.set_header_field("Cache-Control", "no-cache")
        self.set_header_field("site-id", "BACKOFFICE")
        self.set_header_field(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        )
        self._token = None
        self._session = requests.Session()

    @abstractmethod
    def poll(self, resource: str, fail_retry_time: int = 0, data_path: str = ""):
        pass

    def deserialize(self, data: str = "", data_path: str = ""):
        return self._deserializer.deserialize(data, data_path)

    def set_deserializer(self, deserializer: Deserializer):
        self._deserializer = deserializer

    def set_header_field(self, name, value):
        self._header[name] = value

    def get_header(self):
        return self._header

    def get_token(self):
        if self._token:
            return self._token

        payload = self._auth_config.get(CONF_API_AUTH_PAYLOAD)
        content_type = self._auth_config.get(CONF_API_AUTH_CONTENT_TYPE)
        self.set_header_field("Content-Type", f"application/{content_type}")

        r = self._session.post(
            f"{self._auth_config.get(CONF_API_AUTH_TOKEN_URL)}",
            headers=self.get_header(),
            data=payload if content_type != "json" else json.dumps(payload),
        )
        r.raise_for_status()
        self._token = r.json().get(self._auth_config.get(CONF_API_AUTH_TOKEN_NAME))
        return self._token


class RestPoller(ApiPoller):
    def __init__(
        self,
        auth_config: dict,
        api_config: dict,
    ):
        super().__init__(auth_config, api_config)

    # Post
    def post(
        self,
        resource: str,
        fail_retry_time: int = 0,
        params: dict = None,
        payload: dict = None,
    ):
        url = f"{self._api_config.get(CONF_API_BASEURL)}/{resource}"
        if not params:
            params = {}
        if not payload:
            payload = {}
        try:
            # POST request
            logger.debug(f"POST {url}.")
            if self._auth_config:
                self.set_header_field("Authorization", f"Bearer {self.get_token()}")
            self.set_header_field(
                "Content-Type", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )
            self.set_header_field(
                "Accept", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )

            resp = self._session.post(
                url,
                headers=self.get_header(),
                params=params,
                data=json.dumps(payload),
                timeout=180,
            )

            resp.raise_for_status()
            if resp.status_code == 204:
                logger.info("Got 204 (NoContent) back from API call.")
                return
            logger.debug(f"POST response was: {resp.status_code}.")
            # return resp.status_code
            # Deserialize response
            deserialized = self.deserialize(resp.text)
            return deserialized

        except Exception as err:
            if fail_retry_time == 0:
                logger.error(f"POST request failed: {err}.")
                raise RuntimeError("API called failed") from err
            logger.warning(
                f"POST request failed: {err}. Will retry in {fail_retry_time} seconds."
            )
            sleep(fail_retry_time)
            return self.post(resource, 0, params=params, payload=payload)

    # Patch
    def patch(
        self,
        resource: str,
        fail_retry_time: int = 0,
        params: dict = None,
        payload: dict = None,
    ):
        url = f"{self._api_config.get(CONF_API_BASEURL)}/{resource}"
        if not params:
            params = {}
        if not payload:
            payload = {}
        try:
            # PATCH request
            logger.debug(f"PATCH {url}.")
            if self._auth_config:
                self.set_header_field("Authorization", f"Bearer {self.get_token()}")
            self.set_header_field(
                "Content-Type", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )
            self.set_header_field(
                "Accept", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )

            resp = self._session.patch(
                url,
                headers=self.get_header(),
                params=params,
                data=json.dumps(payload),
                timeout=180,
            )

            resp.raise_for_status()
            if resp.status_code == 204:
                logger.info("Got 204 (NoContent) back from API call.")
                return
            logger.debug(f"PATCH response was: {resp.status_code}.")
            return resp.status_code

        except Exception as err:
            if fail_retry_time <= 0:
                logger.error(f"PATCH request failed: {err}.")
                raise RuntimeError("API called failed") from err
            logger.warn(
                f"PATCH request failed: {err}. Will retry in {fail_retry_time} seconds."
            )
            sleep(fail_retry_time)
            return self.patch(resource, 0, params=params, payload=payload)

    # PUT
    def put(
        self,
        resource: str,
        fail_retry_time: int = 0,
        params: dict = None,
        payload: dict = None,
    ):
        url = f"{self._api_config.get(CONF_API_BASEURL)}/{resource}"
        if not params:
            params = {}
        if not payload:
            payload = {}
        try:
            # PUT request
            logger.debug(f"PUT {url}.")
            if self._auth_config:
                self.set_header_field("Authorization", f"Bearer {self.get_token()}")
            self.set_header_field(
                "Content-Type", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )
            self.set_header_field(
                "Accept", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )

            resp = self._session.put(
                url,
                headers=self.get_header(),
                params=params,
                data=json.dumps(payload),
                timeout=180,
            )

            resp.raise_for_status()
            if resp.status_code == 204:
                logger.info("Got 204 (NoContent) back from API call.")
                return
            logger.debug(f"PUT response was: {resp.status_code}.")
            return resp.status_code

        except Exception as err:
            if fail_retry_time <= 0:
                logger.error(f"PUT request failed: {err}.")
                raise RuntimeError("API called failed") from err
            logger.warn(
                f"PUT request failed: {err}. Will retry in {fail_retry_time} seconds."
            )
            sleep(fail_retry_time)
            return self.put(resource, 0, params=params, payload=payload)

    # OPTIONS
    def options(
        self,
        resource: str,
        fail_retry_time: int = 0,
        params: dict = None,
    ):
        url = f"{self._api_config.get(CONF_API_BASEURL)}/{resource}"
        if not params:
            params = {}
        try:
            # OPTION request
            logger.debug(f"OPTION {url}.")
            if self._auth_config:
                self.set_header_field("Authorization", f"Bearer {self.get_token()}")
            self.set_header_field(
                "Content-Type", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )
            self.set_header_field(
                "Accept", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )

            resp = self._session.options(
                url,
                headers=self.get_header(),
                params=params,
                timeout=180,
            )

            resp.raise_for_status()
            if resp.status_code == 204:
                logger.info("Got 204 (NoContent) back from API call.")
                return
            logger.debug(f"OPTIONS response was: {resp.status_code}.")
            return resp.status_code

        except Exception as err:
            if fail_retry_time == 0:
                logger.error(f"OPTION request failed: {err}.")
                raise RuntimeError("API called failed") from err
            logger.warning(
                f"OPTION request failed: {err}. Will retry in {fail_retry_time} seconds."
            )
            sleep(fail_retry_time)
            return self.options(resource, 0, params=params)

    # Poll REST
    def poll(
        self,
        resource: str,
        fail_retry_time: int = 0,
        data_path: str = None,
        params: dict = None,
    ):
        if not data_path:
            data_path = self._api_config.get(CONF_API_DATA_PATH)

        url = f"{self._api_config.get(CONF_API_BASEURL)}/{resource}"

        try:
            # GET request
            logger.debug(f"GET {url}.")
            if self._auth_config:
                self.set_header_field("Authorization", f"Bearer {self.get_token()}")

            self.set_header_field(
                "Content-Type", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )
            self.set_header_field(
                "Accept", f"application/{self._api_config.get(CONF_API_FORMAT)}"
            )

            resp = self._session.get(
                url, headers=self.get_header(), params=params, timeout=180
            )

            resp.raise_for_status()
            if resp.status_code == 204:
                # logger.info("Got 204 (NoContent) back from API call.")
                return
            # Deserialize response
            deserialized = self.deserialize(resp.text, data_path)
            logger.debug(f"GET response deserialized data: {deserialized}.")
            return deserialized

        except Exception as err:
            if fail_retry_time == 0:
                logger.error(f"GET request failed: {err}.")
                raise RuntimeError("API called failed") from err
            else:
                logger.warning(
                    f"GET request failed: {err}. Will retry in {fail_retry_time} seconds."
                )
                sleep(fail_retry_time)
                return self.poll(resource, 0, data_path, params)


# SOAP implementation of API poller class.
# TODO: Add warnings if SOAP settings not set
class SoapPoller(ApiPoller):
    def __init__(self, auth_config: dict, api_config: dict):
        super().__init__(auth_config, api_config)
        self._body_prefix = []
        self._body_params = []
        self._body_suffix = []

        self.set_header_field("Content-Type", "text/xml")

        # Build SOAP requests from settings initially. Can be overridden.
        self.build_soap_request(
            soap_action=self._api_config.get(CONF_SOAP_ACTION),
            soap_action_namespace=self._api_config.get(CONF_SOAP_ACTION_NS),
            soap_action_parameters=self._api_config.get(CONF_SOAP_ACTION_PARAMS),
        )

    def _get_soap_body(self):
        return (
            "".join(self._body_prefix)
            + "".join(self._body_params)
            + "".join(self._body_suffix)
        )

    # Build the body of the SOAP request. (SOAP v1.1 requires "SOAPAction" header, https://www.w3.org/TR/2000/NOTE-SOAP-20000508/#_Toc478383528)
    def build_soap_request(
        self,
        soap_action: str = None,
        soap_action_namespace: str = "",
        soap_action_parameters: dict = None,
    ):
        nsn = "urn"
        # Build soap "action" part
        if soap_action:
            self._body_prefix = []
            self._body_suffix = []

            self.set_header_field("SOAPAction", soap_action)
            # Build first part of soap body
            self._body_prefix.append(f'<?xml version="1.0" encoding="UTF-8"?>')
            self._body_prefix.append(
                f'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">'
            )
            self._body_prefix.append(f"<soapenv:Header/>")
            self._body_prefix.append(f"<soapenv:Body>")
            self._body_prefix.append(
                f'<{nsn}:{soap_action} xmlns:{nsn}="{soap_action_namespace}">'
            )
            # Build last part of soap body
            self._body_suffix.append(f"</{nsn}:{soap_action}>")
            self._body_suffix.append(f"</soapenv:Body>")
            self._body_suffix.append(f"</soapenv:Envelope>")

        # Build soap "parameters" part. Will be placed between body prefix & suffix
        if soap_action_parameters:
            self._body_params = []
            for key, value in soap_action_parameters.items():
                self._body_params.append(f"<{key}>{value}</{key}>")

    # Polling SOAP request
    def poll(self, url: str, fail_retry_time: int = 0, data_path: str = None):
        if not data_path:
            data_path = self._api_config.get(CONF_API_DATA_PATH)
        if not url:
            url = self._api_config.get(CONF_API_BASEURL)

        try:
            # POST request
            logger.debug(f"Posting request to {url}.")
            self.set_header_field("Authorization", f"Bearer {self.get_token()}")
            resp = self._session.post(
                url, headers=self.get_header(), data=self._get_soap_body(), timeout=180
            )
            logger.debug(f"Post response code: {resp.status_code}.")
            logger.debug(f"Post response full data: {resp.text}.")
            resp.raise_for_status()
            if resp.status_code == 204:
                logger.info("Got 204 (NoContent) back from API call.")
                return
            # Deserialize response
            deserialized = self.deserialize(resp.text, data_path)
            logger.debug(f"Post response deserialized data: {deserialized}.")
            return deserialized
        except HTTPError as err:
            logger.error(
                f"SOAP request failed: {err}. Will retry in {fail_retry_time} seconds."
            )
            if fail_retry_time == 0:
                return
            sleep(fail_retry_time)
            self.poll(url, fail_retry_time, data_path)


# Factory method for API pollers
def create_poller(
    api_config: dict,
    auth_config: dict = None,
) -> ApiPoller:
    pollers = {
        "rest": RestPoller,
        "soap": SoapPoller,
    }
    if api_config:
        poller_class = pollers.get(api_config.get(CONF_API_TYPE).lower())
        if not poller_class:
            logger.error(
                f'API poller of type:"{api_config.get(CONF_API_TYPE)}" not found'
            )
        return poller_class(auth_config, api_config)
    else:
        logger.error(f"Missing API config for API poller. No poller created.")

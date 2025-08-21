import logging
import os
from abc import abstractmethod
from typing import Any, Mapping

from pmsintegration.platform.utils import ContextualDict

_log = logging.getLogger(__name__)


class Credentials(ContextualDict):
    def check_username_and_password(self, auth_type: str):
        if missing := self.find_missing_keys(["username", "password"]):
            raise ValueError(
                f"{auth_type} requires 'username' and 'password' to"
                f" be provided by the configured CredentialProvider. Missing: {missing}")

    def check_oauth2_config(self, auth_type: str):
        if missing := self.find_missing_keys(["domain", "consumer_key", "consumer_secret"]):
            raise ValueError(
                f"{auth_type} requires 'domain', 'consumer_key' and 'consumer_secret' to"
                f" be provided by the configured CredentialProvider. Missing: {missing}")

    def check_missing_keys(self, auth_type: str, *args):
        if missing := self.find_missing_keys(args):
            raise ValueError(
                f"{auth_type} requires {args} to"
                f" be provided by the configured CredentialProvider. Missing: {missing}")

    def __repr__(self):
        return repr({k: '*******' for k, _ in self.items()})

    def __str__(self):
        return repr(self)


class CredentialProvider:
    PREFIX = "None"
    _backends = {}

    def __init_subclass__(cls, /, **kwargs):
        cls._backends[cls.prefix()] = cls

    @classmethod
    def read_credentials(cls, credential_name: str, **kwargs) -> Credentials:
        credential, name = credential_name.split(":", maxsplit=1)
        backend = cls._backends.get(credential)
        if not (credential and name) or backend is None:
            backends = list(cls._backends.keys())
            raise ValueError(
                f"'{credential_name}' must be in format <backend>:<name>."
                f" <backend> can be one of :{backends}"
            )
        raw = backend().get_credential(name, **kwargs)
        creds = Credentials.adopt(raw)
        _log.debug(f"Credentials : {creds} for {credential}")
        return creds

    @classmethod
    def prefix(cls):
        return cls.PREFIX

    @abstractmethod
    def get_credential(self, name: str, **kwargs) -> Mapping[str, Any]:
        """Returns the credentials by the given name.
        It read the credentials managed by the data platform externally in a secure way. The name is a logical
        name created to refer.
        :param name: name of the credential
        :return: credentials in form of a dict.
        """
        ...


class OSEnvBackend(CredentialProvider):
    """Credentials can be configured using a set of environment variables together. The assumption is that all such
     environment variables will share the same prefix defined by a name. For example, 'snowflake' credentials could
     be defined as:
        SNOWFLAKE_ACCOUNT=snowflake-account
        SNOWFLAKE_USER=snowflake-user
        SNOWFLAKE_PASSWORD=snowflake-password
    """
    PREFIX = "osenv"

    def get_credential(self, name: str, **kwargs) -> Mapping[str, Any]:
        prefix = name.replace("-", "_").rstrip("_").upper() + "_"
        # NAME_
        return {
            k.removeprefix(prefix).lower(): v
            for k, v in os.environ.items()
            if k.startswith(prefix)
        }

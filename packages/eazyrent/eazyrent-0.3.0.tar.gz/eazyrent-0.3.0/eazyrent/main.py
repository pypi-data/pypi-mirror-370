import importlib
import inspect
import logging
import os
import pkgutil
import re

import eazyrent
from eazyrent.utils.auth import Auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EazyrentSDK:
    def __init__(self):
        self.server = os.environ.get("EAZ_SERVER", "https://api.eazyrent.fr")
        self._auth = Auth.authenticate()
        self.apis = self._load_all_apis()

    def _get_client(self, module):
        configuration = getattr(module, "Configuration").get_default()
        configuration.host = f"{self.server}{configuration.host}"
        if self._auth:
            method, credential = self._auth
            if method == "bearer":
                configuration.access_token = credential
            elif method == "token":
                configuration.api_key["Authorization"] = self._api_key
                configuration.api_key_prefix["Authorization"] = "Token"
            else:
                raise ValueError("Invalid auth method.")
        return getattr(module, "ApiClient")(configuration=configuration)

    def _load_all_apis(self):
        apis_root = type("Apis", (), {})()
        for finder, namespace, ispkg in pkgutil.iter_modules(
            eazyrent.__path__, prefix="eazyrent."
        ):
            if not ispkg:
                continue
            ns_module = importlib.import_module(namespace)
            ns_obj = type(namespace.title(), (), {})()

            for _, version, is_ver_pkg in pkgutil.iter_modules(
                ns_module.__path__, prefix=f"{namespace}."
            ):
                if not is_ver_pkg:
                    continue

                mod = importlib.import_module(version)
                ver_obj = type(version.title(), (), {})()

                if hasattr(mod, "ApiClient"):
                    client = self._get_client(mod)

                    for name, cls in inspect.getmembers(mod, inspect.isclass):
                        if name.endswith("Api") and cls.__module__.startswith(
                            mod.__name__
                        ):
                            attr_name = self._to_snake_case(name.removesuffix("Api"))
                            setattr(ver_obj, attr_name, cls(client))

                    setattr(ns_obj, version.split(".")[-1], ver_obj)

            setattr(apis_root, namespace.split(".")[-1], ns_obj)

        return apis_root

    def _to_snake_case(self, name):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

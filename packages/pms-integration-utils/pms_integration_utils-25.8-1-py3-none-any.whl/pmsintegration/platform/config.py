import copy
import functools
import logging
import os
import re
import typing
from abc import abstractmethod, ABC
from pathlib import Path
from typing import List, Dict, Any

from pmsintegration.platform.errors import (
    IllegalArgumentException,
    IllegalStateException,
    ConfigurationMissingException,
)
from pmsintegration.platform.utils import (
    DictStrAny,
    load_yaml_as_flatten_dict,
    file_exists,
    check,
    deep_merge_dicts,
    ensure_endswith,
    coerce_as_bool,
)

_log = logging.getLogger(__name__)


class BadInterpolationException(Exception):
    ...


class PropertySource(ABC):
    def __init__(self, name: str, order: int = 0):
        if name is None:
            raise IllegalArgumentException("Unnamed property source. Did you define __name__=<name> ?")
        if order is None:
            raise IllegalArgumentException("Unnamed property source. Did you define __order__=<order> ?")

        self.name = name
        self.order = order

    @abstractmethod
    def names(self) -> typing.Set[str]:
        pass

    @abstractmethod
    def get(self, name: str) -> typing.Any:
        pass

    def __contains__(self, item) -> bool:
        return item in self.names()

    def __repr__(self):
        return f"{self.__class__.__name__}#{self.name}"


class OSEnvPropertySource(PropertySource):
    def __init__(self, prefix: str = ""):
        super().__init__("OSEnv", 100)
        self.prefix = prefix
        self.offset = len(self.prefix)

    def get(self, name: str):
        if not self._may_contain(name):
            return None
        name = name[self.offset:]
        return os.environ.get(name, None)

    def names(self):
        return [f"{self.prefix}{n}" for n in os.environ.keys()]

    def _may_contain(self, name: str):
        return name.startswith(self.prefix)


class DictPropertySource(PropertySource):
    def __init__(self, properties: DictStrAny, name: str = None, order: int = None):
        self.properties = properties
        super().__init__(
            name or properties.get('__name__'),
            order or properties.get('__order__') or 0,
        )

    def names(self):
        return self.properties.keys()

    def get(self, name: str):
        return self.properties.get(name)


class YamlPropertySource(DictPropertySource):
    def __init__(self, file: str | Path, name: str = None, order: int = None):
        self.source_file = file
        super().__init__(
            load_yaml_as_flatten_dict(file),
            name,
            order,
        )

    def __repr__(self):
        return f"YamlPropertySource[{self.source_file}]"


class ConfigEnvironment:
    MAX_INTERPOLATION_DEPTH: int = 10
    _INTERPOLATION_EXP = re.compile(r"\${(.+?)}")

    def __init__(self):
        self._sources: List[PropertySource] = []
        self._conf_root: str = ""

    @property
    def conf_root(self):
        return self._conf_root

    @property
    def env_name(self):
        return self.get_required("app.env_name")

    def set_conf_root(self, conf_root):
        self._conf_root = conf_root
        # Set it to os.environ
        os.environ["CONF_ROOT"] = conf_root

    def get_app_env(self):
        return self.cached_get("app.env", "local")

    def add_source(self, source: PropertySource, precedence: int | str | None = None):
        """Add a new property source.

        You may specify the precedence for given property source.

        :param source: property source
        :param precedence: an integer value or "highest" or "lowest". Default is taken from source
        :return: typed prop value


        """
        sources: list = self._sources.copy()

        if source.order == 0:
            # If source do not have order specified; assume it is highest
            precedence = "highest"

        if precedence is not None:
            if isinstance(precedence, str):
                check(
                    precedence in ("lowest", "highest"),
                    "precedence must be either 'lowest' or 'highest'"
                )
            factor = 1 if precedence == "lowest" else -1
            source.order = factor * len(sources) if isinstance(precedence, str) else precedence

        for s in sources:
            if s.name == source.name:
                raise IllegalStateException(f"Source '{source.name}' already added")
            if s.order == source.order:
                raise IllegalStateException(f"'{source.name}'s order {source.order}' is already defined by"
                                            f" another source: '{s.name}'")
        sources.append(source)

        sources = sorted(sources, key=lambda ps: ps.order, reverse=True)
        self._sources = sources
        _log.info(f"Source '{source}'is registered in the environment. Effective order is: {sources}")
        return self

    def register_optional_config_file(self, urlpath: str | Path, log_warn: bool = False):
        if file_exists(urlpath):
            f_name = str(urlpath)
            if f_name.endswith('.yml') or f_name.endswith('.yaml'):
                self.add_source(YamlPropertySource(urlpath))
            else:
                if log_warn:
                    _log.warning(f"Unsupported configuration path: {urlpath}")
        else:
            if log_warn:
                _log.warning(f"Skipping configuration: {urlpath} as it does not exists")

    def known_property_names(self):
        sources = self._sources
        return set([n for s in sources for n in s.names()])

    @functools.lru_cache()
    def cached_get(
            self,
            key: str,
            fallback: typing.Optional[typing.Any] = ...,
            coerce: typing.Callable = None,
    ) -> typing.Any:
        return self.get(key, fallback, coerce)

    def _interpolate(self, key_: str, value_: typing.Any) -> typing.Any:
        if isinstance(value_, typing.Dict):
            interpolated_value = copy.copy(value_)
            for k, v in value_.items():
                interpolated_value[k] = self._interpolate(f"{key_}[{k}]", v)
        elif isinstance(value_, typing.List):
            interpolated_value = type(value_)()
            interpolated_value.clear()  # remove all
            for idx, e in enumerate(value_):
                interpolated_value.append(self._interpolate(f"{key_}[{idx}]", e))
        else:
            interpolated_value = self._interpolation(key_, value_)
        return interpolated_value

    def get(self, name: str, fallback=None, coerce: typing.Callable = None, ):
        """
        Ask the Property to the underlying sources and return it
        :param name: name of property. It may contain . to separate the names
        :param fallback: default fallback value if none of property source is able to resolve the property
        :param coerce: if you want to coerce the value into a typed (i.e. parsed/converted value)
        :return: configured value for given name
        """
        return self._get(name, fallback, coerce)

    def _get(self, name: str, fallback=None, coerce: typing.Callable = None, ):
        coerce = coerce or (lambda x: x)
        value = None

        sources = self._sources
        merged_dict = {}
        merged_list = []
        for s in sources:
            if name in s:
                value = self._interpolate(name, s.get(name))
                _log.debug(f"Property '{name}' resolved by source: {s}")
                if isinstance(value, dict):
                    merged_dict = deep_merge_dicts(value, merged_dict)
                elif merged_dict:
                    break
                elif isinstance(value, list):
                    strategy = self.get(f"__merge_strategy.{name}", "merge")
                    if strategy == "extend":
                        merged_list = merged_list + value
                    elif strategy == "keep_unique":
                        merged_list.extend(value)
                        merged_list = list(set(merged_list))
                    else:
                        merged_list = value
                        break
                elif merged_list:
                    break
                else:
                    break
        value = merged_dict or merged_list or value
        if not value:
            value = None if fallback is ... else fallback

        return coerce(value)

    def is_known_conf(self, name: str):
        return any(name in s.names() for s in self._sources)

    def find_matched(self, prefix: str, suffix: str = None, flatten: bool = False) -> Dict[str, Any]:
        """
        Return all the matching properties by given prefix (and optionally suffix).  You may request nested value
        to be returned.
        :param prefix: Prefix
        :param suffix: Suffix
        :param flatten: keep nested structure as flatten
        :return: dict<K,V> containing the matching property name and their value
        """
        options = {}
        prefix = ensure_endswith(prefix, ".")
        index = len(prefix)
        suffix = suffix or ''
        for n in self.known_property_names():
            if n.startswith(prefix) and n.endswith(suffix):
                p_name: str = n[index:]
                p_value = self.get(n)
                if flatten:
                    if not isinstance(p_value, dict):
                        options[p_name] = p_value
                else:
                    if "." not in p_name:
                        options[p_name] = p_value

        return options

    def get_required(self, name: str, coerce: typing.Callable = None):
        value = self.get(name, coerce)
        if value is None or (isinstance(value, str) and (value == 'Unspecified' or value.strip() == '')):
            raise ConfigurationMissingException(name)
        return value

    def get_int(self, key: str, fallback: typing.Any = None) -> int:
        return self.get(key, fallback, int)

    def get_bool(self, key: str, fallback: typing.Any = None) -> bool:
        return self.get(key, fallback, coerce_as_bool)

    def _interpolation(self, key: str, raw_value, depth: int = 0):  # noqa
        if not (raw_value and isinstance(raw_value, str) and "$" in raw_value):
            return raw_value
        if depth > self.MAX_INTERPOLATION_DEPTH:
            raise BadInterpolationException(f"max recursive interpolation reached. last key: {key}")
        acc = []
        rest = raw_value
        while rest:
            p = rest.find("$")
            if p < 0:
                acc.append(rest)
                break

            if p > 0:
                acc.append(rest[:p])
                rest = rest[p:]

            c = rest[1:2]
            if c == "$":
                acc.append("$")
                rest = rest[2:]  # noqa
            elif c == "{":
                m = self._INTERPOLATION_EXP.match(rest)
                if not m:
                    raise BadInterpolationException(f"bad interpolation expr: {rest}")
                ref_var = m.group(1)
                rest = rest[m.end():]
                ref_var_fallback = None
                if ":" in ref_var:
                    ref_var, ref_var_fallback = ref_var.split(":", maxsplit=1)
                    if "${" in ref_var_fallback:
                        ref_var_fallback = self._interpolation(key, ref_var_fallback, depth + 1)
                ref_var_value = self.get(ref_var, ref_var_fallback)
                if not ref_var_value:
                    if not self.is_known_conf(ref_var):
                        raise BadInterpolationException(
                            f"undefined reference: '{ref_var}' for conf: '{key}'. Sources: {self._sources}"
                        )
                else:
                    if acc or rest:
                        acc.append(str(ref_var_value))
                    else:
                        return ref_var_value
        return "".join(acc)

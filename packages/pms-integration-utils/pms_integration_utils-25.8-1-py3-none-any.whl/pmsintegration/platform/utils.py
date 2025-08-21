import csv
import dataclasses
import enum
import getpass
import importlib.util
import inspect
import io
import logging
import os
import re
import subprocess
import sys
import time
from contextlib import closing
from datetime import (
    datetime,
    timedelta,
)
from itertools import islice
from logging import Logger
from os import PathLike
from pathlib import Path
from string import Template
from typing import (
    TextIO,
    MutableMapping,
    Mapping,
    List,
    Any, Dict, Tuple, Type, Iterable, Callable, TypeVar, Iterator,
)

import fsspec
import pendulum
import yaml
from fsspec import AbstractFileSystem
from fsspec.utils import infer_compression
from yaml import (
    CLoader as Loader,
    CDumper as Dumper,
)

from pmsintegration.platform import errors

DictStrAny = Dict[str, Any]
T = TypeVar('T')

_log = logging.getLogger(__name__)


class ContextualDict(dict):
    """Contextual Dict to support the dot (.) notation to access the key/value pairs"""

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    @classmethod
    def adopt(cls, data):
        """Adopt the given data(potentially a dict) as ContextualDict object"""
        if data is None:
            adopted = cls()
        elif isinstance(data, ContextualDict):
            adopted = data
        elif isinstance(data, dict):
            adopted = cls({k: cls.adopt(v) for k, v in data.items()})
        elif isinstance(data, list):
            adopted = [cls.adopt(v) for v in data]
        else:
            adopted = data
        return adopted

    def find_missing_keys(self, __keys: str | Iterable[str], /) -> list[str]:
        return [k for k in ((__keys,) if isinstance(__keys, str) else __keys) if k not in self]

    @classmethod
    def unwrap(cls, data) -> dict[str, Any]:
        if data is None:
            adopted = dict()
        elif isinstance(data, dict | ContextualDict):
            adopted = dict({k: cls.unwrap(v) for k, v in data.items()})
        elif isinstance(data, list):
            adopted = [cls.unwrap(v) for v in data]
        else:
            adopted = data
        return adopted


def dict_ignoring_nulls(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}


class CTemplate(Template):
    """Custom Template. It extends the standard template class to allow dot character (.) in the identifier name
    """
    idpattern = r'(?a:[_a-z][._a-z0-9]*)'


def flatten_dict(d, parent_key='', sep='.'):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            for i, val in enumerate(v):
                list_key = f"{new_key}{sep}{i}"
                if isinstance(val, dict):
                    items.update(flatten_dict(val, list_key, sep=sep))
                else:
                    items[list_key] = val
        else:
            items[new_key] = v
    return items


class YamlTags:
    EVAL = "!eval"
    CONF = "!conf"


class DefaultLoader(Loader):
    def __init__(self, stream, env: dict[str, Any] | None = None):
        super().__init__(stream)
        self.env = env or {}


class DefaultDumper(Dumper):
    def represent_data(self, data):
        if isinstance(data, enum.Enum):
            return super().represent_data(data.value)
        return super().represent_data(data)


def __add_tags_to_default_loader():
    def _constructor_app_conf(loader: 'DefaultLoader', node) -> Any:
        value = loader.construct_scalar(node)
        if isinstance(value, str):
            value = CTemplate(value).substitute(loader.env)
        return value

    DefaultLoader.add_constructor(YamlTags.CONF, _constructor_app_conf)


__add_tags_to_default_loader()


def load_yaml_as_flatten(uri: str | PathLike, **kwargs) -> ContextualDict:
    """
    Load the YAML conf file as flatten. It may use the given arguments to resolve
    !conf before return the loaded data
    :param uri: uri of file
    :param kwargs: variables which should be used to resolve the placeholders
    :return: loaded conf as ContextualDict
    """
    data = {}
    with fsspec.open(uri, mode="rt", encoding=kwargs.get("encoding", "utf-8")) as f:
        data = flatten_dict(yaml.load(f, DefaultLoader))
    for _ in range(0, 3):  # We support 3 level deep nesting references
        data = {k: (CTemplate(v).substitute(data) if isinstance(v, str) and "${" in v else v) for k, v in data.items()}
    # formatted = deep_format_values(data, template_vars=lambda v: CTemplate(v).substitute(data) if "${" in v else v)
    return ContextualDict.adopt(data)


def load_conf_aware_yml(uri: str | PathLike, env: ContextualDict, **kwargs) -> ContextualDict[str, Any]:  # noqa
    with fsspec.open(uri, mode="rt", encoding=kwargs.get("encoding", "utf-8")) as f:
        loader = DefaultLoader(f, env)
        try:
            data = loader.get_single_data()
        finally:
            loader.dispose()
    return ContextualDict.adopt(data)


def deep_format_values(target: Any, template_vars: Dict | Callable[[str], str],
                       seen: Dict[int, Any] = None) -> Dict:
    # Prevent Recession
    if seen is None:
        seen = dict()
    _oid = id(target)
    if _oid in seen:
        return seen[_oid]

    updated = target
    if isinstance(target, dict):
        updated = {k: deep_format_values(v, template_vars, seen) for k, v in target.items()}
    elif isinstance(target, list):
        updated = [deep_format_values(v, template_vars, seen) for v in target]
    elif isinstance(target, str):
        updated = target.format_map(template_vars) if isinstance(template_vars, Mapping) else template_vars(target)
    seen[_oid] = updated

    return updated


def current_millis():
    return round(time.time() * 1000)


def duration(expr, t: pendulum.Date):
    # Define the regex pattern to match the offset string
    pattern = r'(?P<sign>[+-])\s*(?P<value>\d+)\s*(?P<unit>\w+)'
    match = re.search(pattern, expr)

    if match:
        # Extract components from the match
        sign = match.group('sign')
        value = int(match.group('value'))
        unit = match.group('unit').lower()
        unit = unit if unit[-1] == 's' else unit + 's'
        # Calculate the new date based on the offset
        offset_kwargs = {unit: value}
        if sign == '+':
            new_date = t.add(**offset_kwargs)
        else:
            new_date = t.subtract(**offset_kwargs)
        return new_date
    else:
        raise ValueError("Invalid offset format")


def try_cast_as_int(data: str) -> int | None:
    return int(data) if data and data.isdigit() else None


def infer_data_format_from_output_uri(uri: str) -> str:
    parts = uri.rsplit(".", maxsplit=2)

    if len(parts) == 3 and infer_compression(uri) is not None:
        ext1 = parts[-2]
    else:
        ext1 = parts[-1]
    return ext1


def cleanup_file(fs: AbstractFileSystem, path):
    try:
        fs.rm_file(path)
    except Exception as e:
        _log.warning(f"Could not cleanup target file: {path}", e)
        ...


def now():
    return str(datetime.now())


def load_yaml_as_flatten_dict(urlpath: str | Path) -> DictStrAny:
    with fsspec.open(urlpath, encoding='utf-8') as stream:
        data = dict()
        for doc in yaml.load_all(stream, Loader=DefaultLoader):
            data = {**data, **doc}

    return flatten(data)


def flatten(d, parent_key='', sep='.', keep_nested: bool = True) -> dict[str, Any]:
    items = []
    if not isinstance(d, Mapping):
        d = {"": d}
    for k, v in d.items():
        new_key = (parent_key + sep + k if parent_key else k).rstrip(sep)
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
            if keep_nested:
                items.append((new_key, v))
        elif isinstance(v, List):
            for _i, _v in enumerate(v):
                items.extend(flatten(_v, f"{new_key}.{_i}", sep=sep).items())  # noqa
            if keep_nested:
                items.append((new_key, v))
        else:
            items.append((new_key, v))
    return dict(items)


def log_complex_data(log: Logger, summary: str, data: Any, level: int = logging.INFO):
    log.log(level=level, msg=summary)
    if isinstance(data, Mapping):
        extra = "\n".join([f"===>{i:3d}: {k} = {v}" for i, (k, v) in enumerate(data.items())])
    elif isinstance(data, List):
        extra = "\n".join([f"--->{i:3d}: {v}" for i, v in enumerate(data)])
    else:
        extra = "\n" + str(data)
    log.log(level=level, msg=extra)


def check_mutual_exclusive(a: Any | None, b: Any | None, msg: str, /):
    i = 0 if a is None else 1
    j = 0 if b is None else 1
    if i == j == 1:
        raise errors.IllegalArgumentException(msg)


DefaultDumper.add_multi_representer(ContextualDict, yaml.representer.Representer.represent_dict)  # noqa


def parse_yaml(s: str | TextIO, /) -> ContextualDict:
    return ContextualDict.adopt(yaml.load(s, Loader=DefaultLoader))


def parse_yaml_as_raw(urlpath: str, encoding: str = "utf-8", /) -> dict:
    with fsspec.open(urlpath, mode="rt", encoding=encoding) as s:
        return yaml.load(s, Loader=DefaultLoader)


def to_yaml_str(obj: Any) -> str:
    """
    Serialize a given object into YAML document
    """
    return yaml.dump(obj, Dumper=DefaultDumper)


def module_exists(module: str, package: str | None = None) -> bool:
    try:
        return importlib.util.find_spec(module, package) is not None
    except ModuleNotFoundError:
        return False


def ensure_endswith(value: str, suffix: str):
    return value if value and value.endswith(suffix) else value + suffix


def check(test: bool | Any, message: str):
    if not test:
        raise errors.IllegalArgumentException(message)


def coerce_as_bool(value: bool | str | Any) -> bool:
    if isinstance(value, str):
        lit = value.lower()
        value = True if lit in (
            "yes",
            "1",
            "true",
            "on"
        ) else False if lit in (
            "no",
            "0",
            "false",
            "off",
            "none",
            "null",
            "na"
        ) else value
    return bool(value)


def coerce_as_datetime(date_string: str, formats: str | list[str] | Tuple[str, ...] = None):
    formats = coerce_as_list(formats) or ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f")

    if len(formats) == 1 and formats[0] == "epoch":
        return datetime.fromtimestamp(int(date_string) / 1000.0)

    for date_f in formats:
        try:
            return datetime.strptime(date_string, date_f)
        except ValueError:
            pass
    return errors.IllegalArgumentException(f"'{date_string}' is not valid. Format were: {formats}")


def coerce_as_date(date_string: str, formats: str | List[str] | Tuple[str, ...] = None):
    return coerce_as_datetime(date_string, formats).date()


def coerce_as_timedelta(delta: str | None) -> timedelta | None:
    if not delta:
        return None
    expr = f"timedelta({delta})"
    return eval(expr)


def coerce_as_list(data: Any | list[Any] | None):
    if data is None:
        return None
    if isinstance(data, list):
        return data
    if isinstance(data, set) or isinstance(data, tuple):
        return list(data)
    return [data]


def replace_file_extn(filename: str, extn: str):
    """
    Replace File extn
    :param filename: file name
    :param extn: New extension (must have a . as prefix)
    :return: filename with new extension
    """
    root, _ = os.path.splitext(filename)
    return root + extn


def ensure_dir_exists(path: str | Path):
    (Path(path) if isinstance(path, str) else path).mkdir(parents=True, exist_ok=True)


def file_extn(filename: str) -> str:
    _, extn = os.path.splitext(filename)
    return extn


def file_exists(urlpath: str) -> bool:
    with closing(fsspec.open(urlpath)) as f:
        fs: fsspec.AbstractFileSystem = f.fs
    return fs.exists(urlpath)


def find_class(_type: str) -> Type | None:
    try:
        module_name, class_name = _type.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as _e:
        _log.warning(f"Could not find type: '{_type}': {str(_e)}")


def instantiate(_type: str | Type, /, **kwargs):
    if isinstance(_type, str):
        cls = find_class(_type)
        if cls is None:
            raise errors.IllegalArgumentException(f"Could not find type: {_type}")
        _type = cls
    return _type(**kwargs)


def write_text_to(urlpath: str | Path, /, data: str, **kwargs):
    mode = kwargs.pop("mode", "wt")
    encoding = kwargs.pop("encoding", "utf-8")
    with fsspec.open(urlpath, mode=mode, encoding=encoding, **kwargs) as f:
        return f.write(data)


def read_text_from(
        urlpath: str | Path, /,
        strip: bool = True,
        ignore_non_existing: bool = False,
        **kwargs
) -> str | None:
    mode = kwargs.pop("mode", "rt")
    encoding = kwargs.pop("encoding", "utf-8")
    content = None
    if file_exists(urlpath):
        with fsspec.open(urlpath, mode=mode, encoding=encoding, **kwargs) as fp:
            content = fp.read()
            if strip:
                content = content.strip()
    elif not ignore_non_existing:
        raise errors.IllegalArgumentException(f"'{urlpath}' does not exists")
    return content


def deep_merge_dicts(defaults: Dict[Any, Any] | None, overrides: Dict[Any, Any] | None) -> Dict[Any, Any] | None:
    """Merge two dictionaries deeply.

    If a key exists in both dictionaries and the values associated with that
    key are either of dictionary or list type in both, then they will be merged. Otherwise, the value from the overrides
    dictionary will overwrite the value from the defaults dictionary in the resulting merged dictionary.

    :param defaults: Default dictionary.
    :param overrides: Dictionary with values to be merged with the defaults.
    :return: Merged dictionary.
    """
    if overrides is None:
        return defaults.copy()
    if defaults is None:
        return overrides.copy()

    result = defaults.copy()
    for key, new_value in overrides.items():
        old_value = defaults.get(key)
        if isinstance(old_value, dict) and isinstance(new_value, dict):
            result[key] = deep_merge_dicts(old_value, new_value)
        elif isinstance(old_value, list) and isinstance(new_value, list):
            result[key] = old_value + new_value
        else:
            result[key] = new_value

    return result


def parse_datetime(dt: str | None) -> pendulum.DateTime | None:
    from pendulum.parsing import exceptions
    try:
        dt = dt.strip() if dt else dt  # trim whitespace
        return pendulum.parse(dt) if dt else None
    except exceptions.ParserError as e:
        raise errors.IllegalArgumentException(*e.args) from e


@dataclasses.dataclass
class DateTimeRange:
    lower: pendulum.DateTime | None
    upper: pendulum.DateTime | None
    is_lower_inclusive: bool
    is_upper_inclusive: bool
    __PATTERN = re.compile(
        "^"
        r"  (?P<li>[(\[])?"  # Optional Lower Inclusive character
        r"      (?P<l>[ /0-9:-]+?)?"  # Lower Range Value; may contain spaces
        r"  ("
        r"      (?P<sep>,)"
        r"      (?P<u>[ /0-9:,-]+)?"
        r"  )?"  # Optional Upper Range Value; must have , as prefix
        r"  (?P<ui>[])])?"  # Optional Upper Inclusive character
        r"$",
        re.VERBOSE
    )

    @classmethod
    def parse(cls, expr: str) -> 'DateTimeRange':
        m = cls.__PATTERN.fullmatch(expr)
        if not m:
            raise errors.IllegalArgumentException(f"'{expr}' is not a valid datetime range expression")
        d = m.groupdict()
        if d.get("sep") is None:
            # If no sep, we must use lower range as the upper
            d["u"] = d.get("l")
        return cls(
            parse_datetime(d.get("l")),
            parse_datetime(d.get("u")),
            (d.get("li") or "[") == "[",
            (d.get("ui") or "]") == "]",
        )

    def inrange(self, _v: pendulum.DateTime | str) -> bool:
        v = _v if isinstance(_v, pendulum.DateTime) else pendulum.parse(_v)
        in_range = True
        if self.lower:
            in_range = self.lower <= v if self.is_lower_inclusive else self.lower < v
        if in_range:
            if self.upper:
                in_range = self.upper >= v if self.is_lower_inclusive else self.upper > v
        return in_range


def to_csv_line(row: Iterable[str], nl: str = "\n") -> str:
    sink = io.StringIO()
    writer = csv.writer(sink, dialect="excel", lineterminator=nl)
    writer.writerow(row)
    return sink.getvalue()


def read_csv_line(_line: str, sep: str = ",") -> list[str]:
    import csv
    with io.StringIO(_line) as s:
        row = next(csv.reader(s, delimiter=sep))
    return [c.strip() for c in row]


def infer_filename_extension(filename: str) -> str:
    f, ext = os.path.splitext(filename)
    file_ext = ""
    if ext in (".gz", ".tar"):
        _, file_ext = os.path.splitext(f)
    ext = file_ext + ext
    return ext


def find_module_member(__fqn: str, required: bool = True):
    try:
        module_, type_ = __fqn.rsplit(".", maxsplit=1)
        module = importlib.import_module(module_)
        return getattr(module, type_)
    except (ImportError, AttributeError) as e:
        logging.getLogger("core.utils").debug(f"Could not find module member: {__fqn}", exc_info=e)
        if required:
            raise


def coerce_as_callable(__fqn: str, args_types: list[Any] = None) -> Callable:
    fn = find_module_member(__fqn)
    if not callable(fn):
        raise errors.IllegalArgumentException(f'{__fqn} is not a callable/function')
    if args_types:
        sig = inspect.signature(fn)
        if len(sig.parameters) != len(args_types):
            raise errors.IllegalArgumentException(
                f"'{__fqn}' actual parameters and given formal arguments are not matching"
            )
        # TODO add type check here
    return fn


def run_process(
        command: str | list[str],
        stdout_line_handler: Callable[[str], str | None]
) -> int:
    """
    Run the command and stream the stdout to the given callback line by line
    Once child process completed, return the exit code.
    """
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        shell=True,
    )

    while (exit_code := process.poll()) is None:
        line = process.stdout.readline()
        if line:
            stdout_line_handler(line)

    return exit_code


def current_username():
    return getpass.getuser()


def trim_dict_keys(input_dict: dict[str, Any], chars_to_trim: str = " ") -> dict[str, Any]:
    """Creates a new dictionary with keys trimmed of leading/trailing characters.

    Args:
        input_dict: The input dictionary.
        chars_to_trim: The characters to trim from the keys (default: whitespace).

    Returns:
        A new dictionary with trimmed keys.  The original dictionary is not modified.
        Returns an empty dict if the input is not a dictionary.
    """
    return {
        key.strip(chars_to_trim): value for key, value in input_dict.items()
    }


def coerce_as_float(value__: str | float | int | None, null_values: str | list[str] = None):
    if null_values is None:
        null_values = ("NA", "N.A.", "None", None, "null", "")
    return None if value__ in null_values else float(value__)


def coerce_as_float_pct(value__: str | int | float | None, null_values: str | list[str] = None):
    """
    Given value is not in % format. it should be in '1.4%', 11.5, -1.4, +4  etc.
    """
    if null_values is None:
        null_values = ("NA", "N.A.", "None", None, "null", "")

    if value__ in null_values:
        return None

    value = str(value__).strip("% ").replace(" ", "")
    return float(value) / 100


if sys.version_info >= (3, 12):
    from itertools import batched as _batched  # noqa
else:
    def _batched(iterable: Iterable[T], n: int) -> Iterator[list[T]]:
        if n <= 0:
            raise ValueError("n must be > 0")
        it = iter(iterable)
        while batch := list(islice(it, n)):
            yield batch

batched = _batched

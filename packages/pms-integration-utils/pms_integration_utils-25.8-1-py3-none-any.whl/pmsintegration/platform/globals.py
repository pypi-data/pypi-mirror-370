import importlib
import logging
from pathlib import Path

from pmsintegration.platform import dynamic_expr, utils, errors
from pmsintegration.platform.config import ConfigEnvironment
from pmsintegration.platform.utils import read_text_from, read_csv_line, module_exists


class GlobalOpts:
    verbose: bool = False


def _discover_conf_root(_env: ConfigEnvironment) -> str:
    _root = _env.get("CONF_ROOT")
    if _root:
        return _root

    candidate = Path("./conf")
    fs_root = Path("/conf").resolve()
    while True:
        root = candidate.resolve()
        if (root / "defaults.yml").exists():
            return str(root)
        if root == fs_root:
            break
        candidate = Path("..") / candidate

    raise errors.IllegalStateException("Could not discover the conf root")


def _autoconfigure(urlpath: str, _env):
    raw_text = read_text_from(urlpath, ignore_non_existing=True) or ""
    for line in raw_text.splitlines():
        if line.startswith("__auto_configure__:"):
            _, module_name = line.split(":", maxsplit=1)
            for module_name in read_csv_line(module_name):
                if module_exists(module_name):
                    importlib.import_module(module_name).configure(_env)


def _make_default_env():
    from pmsintegration.platform.config import OSEnvPropertySource
    import os

    def _override_osenv_if_not_already_set(target, source):
        if target not in os.environ:
            if source in os.environ:
                os.environ[target] = os.environ[source]

    # Fix OS incompatibility
    _override_osenv_if_not_already_set('USER', 'USERNAME')
    _override_osenv_if_not_already_set('USERNAME', 'USER')
    _env = ConfigEnvironment()

    _env.add_source(OSEnvPropertySource())

    app_env = _env.get("APP_ENV", "local")
    conf_root = _discover_conf_root(_env)
    _env.set_conf_root(conf_root)

    if utils.find_module_member('dotenv.load_dotenv', False):
        from dotenv import load_dotenv
        load_dotenv(f"{conf_root}/.env")

    default_conf_file = f"{conf_root}/defaults.yml"

    _autoconfigure(default_conf_file, _env)
    _env.register_optional_config_file(default_conf_file)
    _env.register_optional_config_file(f"{conf_root}/env-{app_env}.yml")

    def _register_dynamic_sources():
        # Lazy Loading of modules
        config_modules = _env.get("app.config_modules", [])
        for config_module in config_modules:
            try:
                module = importlib.import_module(config_module)
                register = getattr(module, "register")
                register(_env)
            except (ImportError, AttributeError) as e:
                logging.getLogger(__name__).warning(f"Property module could not loaded: {config_module}. Causes: {e}")

    _register_dynamic_sources()

    dynamic_expr.add_global_context("env", _env)

    logging.basicConfig(
        level="INFO",
        format='%(asctime)s.%(msecs)03d - %(thread)d - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # logging.getLogger("").setLevel("WARN")
    logging.getLogger("azure").setLevel("WARN")
    logging.getLogger("pmsintegration").setLevel("INFO")

    return _env


env = _make_default_env()

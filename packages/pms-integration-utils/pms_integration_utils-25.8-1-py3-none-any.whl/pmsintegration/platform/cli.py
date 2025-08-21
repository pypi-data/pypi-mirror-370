import logging

import typer

from pmsintegration.platform import utils
from pmsintegration.platform.globals import GlobalOpts

app = typer.Typer(
    pretty_exceptions_show_locals=False,
)


def _register_children_apps():
    from pmsintegration.platform.globals import env
    modules = env.get("app.cli_modules")
    for module in modules:
        register_fn = utils.find_module_member(f"{module}.register", required=False)
        if register_fn is None:
            warning_message = (
                typer.style(f"WARNING: Configure cli module not available - {module}",
                            fg=typer.colors.YELLOW,
                            bold=True)
            )
            typer.echo(warning_message)
        else:
            register_fn(app)
            logging.getLogger(__name__).debug(f"CLI module registered - {module}")


_register_children_apps()


@app.callback()
def main():
    """PMS Integration CLI App.

    This CLI application provides a collection of commands to efficiently
    perform various tasks related to PMS integration. It is designed to
    simplify workflows and streamline operations through an easy-to-use
    interface.
    """


@app.command()
def version():
    """Show package version.

    """
    from importlib import metadata
    __version__ = metadata.version("pms-integration-utils")
    if GlobalOpts.verbose:
        typer.echo("Version is: ", nl=False)
    typer.echo(__version__, nl=False)


@app.command()
def check_forbidden_package_usage(
        source_dir: str,
        packages: list[str] = typer.Option(
            [], "--package", "-p",
            min=1,
            help="Specify the forbidden package (space-separated)",
        )
):
    """Scan source code for forbidden packages (typically a devtool)

    """
    from pmsintegration.platform.internal import python_code_checker
    typer.secho("Checking forbidden package usage")
    typer.secho(f"In directory: {source_dir}")
    for _p in packages:
        typer.secho(f"  forbidden - {_p}")
    exit_code = 0
    for py_file in python_code_checker.find_python_files(source_dir):
        imports = python_code_checker.find_imports(py_file)

        if any(imp.startswith(p) for imp in imports for p in packages):
            exit_code = 1
            typer.secho(
                message=f"ERROR: Disallowed import found in {py_file}",
                fg=typer.colors.RED,
                err=True
            )
    if exit_code:
        raise typer.Exit(code=exit_code)


if __name__ == '__main__':
    app()

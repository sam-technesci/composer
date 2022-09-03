#!/usr/bin/python3
import logging
import sys

import click

from composition import api, template_cmd, VERSION
from composition.install import install_application
from composition.list_apps import list_applications, setup_default_logging_format
from composition.models import Context
from composition.storage import create_storage_if_not_exist
from composition.uninstall import uninstall_application


@click.command("install", context_settings={'show_default': True})
@click.option("--template", "-t", default="template.yaml", help="The name of the template file to install")
@click.option("--value", "-v", default=["values.yaml"], help="A list of values YAML files to generate templates from",
              multiple=True)
@click.option("--id", "-i", default=None,
              help="Set the application id (must be unique for each installation of an app.")
def install(template="template.yaml", value=None, id=None):
    """
    Install a docker-compose application using a given template.
    """
    install_application(template, value, application_id=id)


@click.command("delete", context_settings={
    'show_default': True,
    "ignore_unknown_options": True,
    "allow_extra_args": True
})
@click.pass_context
@click.option("--force", "force", default=False, flag_value=True)
@click.option("--all", "all", default=False, flag_value=True)
def delete(ctx, force=False, all=False):
    """
        Uninstalls a given applications, removing it completely.
    """
    # Alias for uninstall

    uninstall_application(ctx.args, force, all)


@click.command("uninstall", context_settings={
    'show_default': True,
    "ignore_unknown_options": True,
    "allow_extra_args": True
}, hidden=True)
@click.pass_context
@click.option("--force", "force", default=False, flag_value=True)
@click.option("--all", "all", default=False, flag_value=True)
def uninstall(ctx, force=False, all=False):
    """
    Uninstalls a given applications, removing it completely.
    """
    uninstall_application(ctx.args, force, all)


@click.command("template", context_settings={'show_default': True})
@click.option("--template", "-t", default="template.yaml", help="The name of the template file to install")
@click.option("--value", "-v", default=["values.yaml"], help="A list of values YAML files to generate templates from",
              multiple=True)
def template_func(template="template.yaml", value=None):
    """
    Prints the output docker_compose.yaml once the values have been applied. Can be used to produce a compose for use
    outside of the composer install environment
    """
    template_cmd.template(template, value)


@click.command("list")
@click.option("--quiet", "quiet", default=False, flag_value=True)
def list_all(quiet=False):
    """
    list installed applications
    """
    list_applications(quiet)


@click.command("version")
def version():
    """
    Print the current version number
    """
    logging.info(f"composer version {VERSION} (pip package docker-composition)")


@click.group()
@click.option("--verbose", "verbose", default=False, flag_value=True)
@click.option("--level", default="INFO", type=click.Choice(['DEBUG', 'INFO', 'ERROR']))
def cli(verbose, level):
    Context.verbose = verbose
    if verbose:
        level = logging.DEBUG
    # Set the default logging
    logging.basicConfig(level=level)
    logging.root.setLevel(level)
    # Remove the default formatting with log level
    setup_default_logging_format()
    # Create the temporary storage if it does not exist
    create_storage_if_not_exist()
    # Check docker-compose is installed
    if not api.is_compose_installed():
        logging.error("[ERROR] docker-compose is not installed")
        logging.error("Exiting.")
        sys.exit(1)


def entrypoint():
    # Register the cli commands
    cli.add_command(install)
    cli.add_command(delete)
    cli.add_command(uninstall)
    cli.add_command(list_all)
    cli.add_command(template_func)
    cli.add_command(version)
    # Call the cli
    cli()


if __name__ == "__main__":
    entrypoint()

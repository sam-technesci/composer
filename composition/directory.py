import json
import logging
import os
import sys
from os.path import exists
from pathlib import Path

from composition import install, api
from composition.models import Application, generate_name
from composition.storage import get_yaml


def get_app_details(template):
    if not os.path.exists(os.path.join(os.getcwd(), template)):
        logging.error(f"Template file '{template}' not found in this directory.")
        sys.exit(1)
    app_yaml_path = os.path.join(os.getcwd(), "app.yaml")
    if not os.path.exists(app_yaml_path):
        logging.error(f"app.yaml not found in this directory.")
        sys.exit(1)
    app_details = get_yaml(app_yaml_path)
    if app_details is None:
        logging.error(f"Invalid app.yaml file at location {app_yaml_path}.")
        sys.exit(1)
    if "name" not in app_details or "version" not in app_details:
        logging.error(f"Invalid app.yaml at {app_yaml_path}.")
        logging.error("Must have a name and version.")
        return
    return app_details


def handle_install(template="template.yaml", values=None, application_id=None, manual_values=None):
    if values is None:
        values = ["values.yaml"]
    if manual_values is None:
        manual_values = []
    if application_id is None:
        application_id = generate_name()
    logging.debug(f"Values: {values}")
    found_paths = find_file_paths('app.yaml')

    app_details = get_app_details(template)
    app_name = app_details["name"]
    version = app_details["version"]
    for p in found_paths:
        recursive_install(template, p, application_id, values, manual_values)
    # Create the application (it automatically registers itself)
    app = Application(os.getcwd(), app_name, version=version, application_id=application_id)
    logging.info(f"Successfully created installed {app.id}")
    logging.info("To view installed applications use `composer list`")


def handle_delete(application_id, force=False):
    location = get_compose_path(application_id)
    guids = get_application_guids(location)
    for guid in guids:
        compose_location = os.path.join(location, guid)
        api.compose_down(compose_location, application_id, force)


def get_application_guids(location):
    with open(os.path.join(location, "config.json"), 'r') as f:
        config = json.loads(f.read())
    guids = [c["guid"] for c in config["apps"]]
    # Reverse the list of guids so the parent is destroyed last
    guids.reverse()
    return guids


def get_compose_path(application_id):
    location = os.path.join(Path.home(), ".composer", application_id)
    if not os.path.exists(location):
        logging.error(f"Could not find application {application_id}")
        sys.exit(1)
    return location


def get_name_from_guid(location, guid):
    with open(os.path.join(location, "config.json"), 'r') as f:
        config = json.loads(f.read())
    app_id = [c["name"] for c in config["apps"] if c["guid"] == guid][0]
    return app_id


def handle_logs(application_id, follow=False, service=None, application=None):
    location = get_compose_path(application_id)
    guids = get_application_guids(location)
    for guid in guids:
        compose_location = os.path.join(location, guid)
        application_name = get_name_from_guid(location, guid)
        if application is not None and application != application_name:
            logging.debug(f"Skipping logs for {application_name}")
            # If the user has specified to look for a specific app.yaml name, then skip if its doesn't match
            continue
        logging.info(f"Logs for: {application_name}")
        api.compose_logs(compose_location, follow, service)


def handle_cmd(application_id, arg_list, application=None):
    logging.debug(f"Application {application_id}, Arguments {arg_list}")
    location = get_compose_path(application_id)
    guids = get_application_guids(location)
    for guid in guids:
        compose_location = os.path.join(location, guid)
        application_name = get_name_from_guid(location, guid)
        if application is not None and application != application_name:
            logging.debug(f"Skipping logs for {application_name}")
            # If the user has specified to look for a specific app.yaml name, then skip if its doesn't match
            continue
        logging.info(f"Running 'docker-compose {' '.join(arg_list)}'")
        api.cmd(compose_location, arg_list)


def handle_list_subapps(application_id):
    location = get_compose_path(application_id)
    guids = get_application_guids(location)
    for guid in guids:
        application_name = get_name_from_guid(location, guid)
        logging.info(application_name)


def find_file_paths(target_regex, base=None):
    if base is None:
        base = os.getcwd()
    if not os.path.exists(base):
        logging.error(f"Path {base} does not existing.")
        sys.exit(1)
    found_paths = []
    for path in Path(base).rglob(target_regex):
        found_paths.append(path)
    return found_paths


def recursive_install(template, p: Path, application_id, values, manual_values):
    if values is None:
        values = ["values.yaml"]
    app_details = get_yaml(p)
    if app_details is None:
        logging.error(f"Invalid app.yaml file at location {p}, skipping.")
        return
    logging.debug(f"App details: {app_details}")
    directory = os.path.dirname(p)
    logging.debug(f"Handling Path: {directory}")
    # Check if the template.yaml is in the current directory
    template_location = os.path.join(directory, template)
    if not exists(template_location):
        logging.error(f"Could not find file {template_location}, skipping.")
        return
    logging.debug(f"Found {template_location} performing action INSTALL.")
    install.generate_template(directory, template, app_details, application_id, values, manual_values)

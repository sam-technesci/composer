import json
import logging
import os.path
import re
import sys
import traceback

import jinja2 as jinja2

from composition import directory, storage, api
from composition.models import Context
from composition.storage import get_yaml


def install_application(template="template.yaml", values=None, application_id=None, manual_values=None):
    directory.handle_install(template, values, application_id, manual_values)


def consolidate_values(values, manual_values):
    all_values = {}
    # First check that we can find all the values files
    for p in values:
        val_path = p
        if not os.path.isabs(p):
            val_path = os.path.join(os.getcwd(), p)
        if not str(val_path).endswith(".yaml"):
            logging.error(f"{val_path} is not a valid yaml file.")
            sys.exit(1)
        if not os.path.exists(val_path):
            logging.error(f"Values file {val_path} does not exist.")
            sys.exit(1)
        # Load the values file
        loaded_values = get_yaml(val_path)
        if loaded_values is None:
            logging.error("Could not load {val_path}, is it empty or invalid?")
            sys.exit(1)
        all_values = merge(all_values, loaded_values)
    # The add the values to consolidated dictionary
    # Now merge the manual values
    for string in manual_values:
        if re.match(r"(.*)=(.*)", string):
            variable = get_value(string)
            val_dict = {string.split("=")[0]: variable}
            all_values = merge(all_values, val_dict)
        else:
            logging.error(f"Value {string} must be in format key=value")
            sys.exit(1)
    return all_values


def get_value(string):
    string = string.split("=")[1]
    if string.startswith("{"):  # this is likely a dictionary
        try:
            return json.loads(string)
        except json.JSONDecodeError:
            # If the json decoding fails return it as a string
            pass
    if string.lower() == "true":
        return True
    if string.lower() == "false":
        return False
    if string.isnumeric():
        return float(string)
    return string


def merge(dict_1, dict_2):
    result = dict_1 | dict_2
    return result


def generate_config_maps(template_env, all_values):
    config_strs = []
    config_files = directory.find_file_paths("*.configmap")
    logging.debug(f"Config maps found: {config_files}")
    for conf in config_files:
        # The path is local so get the filename
        string = generate_template_str(template_env, os.path.basename(conf), all_values)
        config_strs.append({"filename": conf, "content": string})
    return config_strs


def generate_template_str(template_env, template_file, values):
    template = template_env.get_template(template_file)
    try:
       return template.render(values)
    except jinja2.exceptions.TemplateError as e:
        logging.error("Error when rendering template.")
        logging.error(f"Message: {e.message}")
        if Context.verbose:
            logging.error(traceback.format_exc())
        else:
            logging.error("Enable --verbose flag for more details.")
        sys.exit(1)

def generate_template(template_dir, template_file, app_details, application_id, values, manual_values):
    if "name" not in app_details or "version" not in app_details:
        logging.error(f"Invalid app.yaml at {template_dir}.")
        logging.error("Must have a name and version.")
        return
    app_name = app_details["name"]
    logging.info(f"Generating template for {app_name}.")
    all_values = consolidate_values(values, manual_values)
    logging.debug(f"Values to apply: {all_values}")
    # Use the values to generate the template
    templateLoader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=templateLoader)
    # first generate configmap files
    config_strs = generate_config_maps(template_env, all_values)
    # generate the docker-compose file
    output_str = generate_template_str(template_env, template_file, all_values)
    # Save the template in the temp folders, returns the path of the output compose
    compose_path = os.path.join(template_dir, template_file)

    path = storage.write_compose(application_id, output_str, app_details, compose_path, template_dir, config_strs)

    if "alwaysPull" in app_details and app_details["alwaysPull"]:
        api.compose_pull(path)
    logging.info(f"Starting services for {app_name}, this could take some time.")
    # docker-compose up on the template
    api.compose_up(app_name, path, application_id)

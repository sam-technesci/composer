import logging
import os.path
import sys
import traceback

import jinja2 as jinja2

from composition import directory, storage, api
from composition.models import Context
from composition.storage import get_yaml


def install_application(template="template.yaml", values=None, application_id=None):
    directory.handle_install(template, values, application_id)


def consolidate_values(values):
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
    return all_values


def merge(dict_1, dict_2):
    result = dict_1 | dict_2
    return result


def generate_template(template_dir, template_file, app_details, application_id, values):
    if "name" not in app_details or "version" not in app_details:
        logging.error(f"Invalid app.yaml at {template_dir}.")
        logging.error("Must have a name and version.")
        return
    app_name = app_details["name"]
    logging.info(f"Generating template for {app_name}.")
    all_values = consolidate_values(values)
    logging.debug(f"Values to apply: {all_values}")
    # Use the values to generate the template
    templateLoader = jinja2.FileSystemLoader(searchpath=template_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)
    try:
        output_str = template.render(all_values)
    except jinja2.exceptions.TemplateError as e:
        logging.error("Error when rendering template.")
        logging.error(f"Message: {e.message}")
        if Context.verbose:
            logging.error(traceback.format_exc())
        else:
            logging.error("Enable --verbose flag for more details.")
        sys.exit(1)
    # Save the template in the temp folders, returns the path of the output compose
    compose_path = os.path.join(template_dir, template_file)
    path = storage.write_compose(application_id, output_str, app_details, compose_path, template_dir)

    if "alwaysPull" in app_details and app_details["alwaysPull"]:
        logging.info("Always pull is enabled. Pulling latest images.")
        # If always pull is set
        # Enumerate all docker images in the compose
        # Docker pull for each image
        pass

    # docker-compose up on the template
    api.compose_up(app_name, path, application_id)


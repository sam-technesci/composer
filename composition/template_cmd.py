import logging
import os
import sys
import traceback

import jinja2

from composition.install import consolidate_values
from composition.models import Context


def template(template_file="template.yaml", values=None):
    all_values = consolidate_values(values)
    # Use the values to generate the template
    templateLoader = jinja2.FileSystemLoader(searchpath=os.getcwd())
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
    # Using print ensure its works with stdout properly
    print(f"{output_str}")

import logging
import os
import sys
import traceback

import jinja2
from jinja2 import Template

from composition.install import consolidate_values
from composition.models import Context


def template(template_file="template.yaml", values=None, manual_values=None):
    if manual_values is None:
        manual_values = []
    all_values = consolidate_values(values, manual_values)
    # Use the values to generate the template
    with open(template_file) as f:
        template = Template(f.read())
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

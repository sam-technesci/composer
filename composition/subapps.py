import logging
import sys

from composition.directory import handle_list_subapps


def subapps(application_id_list):
    if not application_id_list:
        logging.error("Please include an id of application to list sub-applications.")
        logging.error("e.g. composer applications moon-baboon")
        sys.exit(1)
    for application_id in application_id_list:
        logging.info(f"Sub-applications for {application_id}")
        handle_list_subapps(application_id)
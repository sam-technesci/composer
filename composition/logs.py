import logging
import sys

from composition.directory import handle_logs


def logs(application_id_list, follow, service, application):
    if not application_id_list:
        logging.error("Please include an id of application to view logs.")
        logging.error("e.g. composer logs moon_baboon")
        sys.exit(1)
    for application_id in application_id_list:
        handle_logs(application_id, follow=follow, service=service, application=application)

import logging
import sys

from composition import directory, storage
from composition.models import Context


def uninstall_application(application_id_list, force, all):
    if all:
        for app in Context.get_applications():
            application_id = app.id
            logging.info(f"Uninstalling {application_id}")
            directory.handle_delete(application_id, force=force)
            storage.remove(application_id)
        return

    if not application_id_list:
        logging.error("Please include an id to delete.")
        logging.error("e.g. composer uninstall -i moon_baboon")
        sys.exit(1)
    for application_id in application_id_list:
        logging.info(f"Uninstalling {application_id}")
        directory.handle_delete(application_id, force=force)
        storage.remove(application_id)


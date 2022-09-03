import logging

from composition.directory import handle_cmd


def cmd(arg_list, application):
    if not arg_list or len(arg_list) <= 1:
        logging.error("Please include an argument for docker-compose.")
        logging.error("e.g. composer application_id cmd images <service>")
    logging.debug(f"Arguments to cmd {arg_list}")
    handle_cmd(arg_list[0], arg_list[1:], application)

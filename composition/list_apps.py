import logging
import time
import humanize

from composition.models import Context, Application


def setup_column_logging():
    root = logging.getLogger()
    hdlr = root.handlers[0]
    fmt = logging.Formatter(
        '%(app_id)-15s %(version)-10s %(time)-10s %(status)-10s %(app_name)-23s %(compose_name)-20s')
    hdlr.setFormatter(fmt)


def setup_default_logging_format():
    root = logging.getLogger()
    hdlr = root.handlers[0]
    fmt = logging.Formatter('%(message)s')
    hdlr.setFormatter(fmt)


def list_applications(quiet):
    if not quiet:
        setup_column_logging()
        # Print the headings
        logging.info("", extra={
            "app_id": "APP ID",
            "version": "VERSION",
            "time": "UPTIME",
            "app_name": "APP NAME",
            "status": "STATUS",
            "compose_name": "COMPOSE"
        })

    # Print the installed applications
    if quiet:
        # Use print to ensure output to stdout
        [print(app.id, end=" ") for app in Context.get_applications()]
    else:
        for app in Context.get_applications():  # type: Application
            time_delta = time.time() - app.start_timestamp
            # Utilise logging to set reasonable columns
            logging.info("", extra={"app_id": app.id, "version": app.version, "app_name": app.app_name,
                                    "time": humanize.naturaldelta(time_delta), "status": app.status.name,
                                    "compose_name": app.compose_name}
                         )
    setup_default_logging_format()

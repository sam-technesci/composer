import json
import logging
import os
import time
from enum import Enum
from pathlib import Path

import petname


class Context:
    _applications = []
    verbose = False

    @staticmethod
    def add_application(app):
        Context._applications.append(app)

    @staticmethod
    def get_applications():
        Context.refresh_applications()
        return Context._applications

    @staticmethod
    def refresh_applications():
        Context._applications = []
        application_path = os.path.join(Path.home(), ".composer")
        subfolders = [f.path for f in os.scandir(application_path) if f.is_dir()]
        configs = []
        for folder in subfolders:
            config_path = os.path.join(folder, "config.json")
            if not os.path.exists(config_path):
                logging.error("Path: {}, does not have a config.json.")
                continue
            with open(config_path, "r") as f:
                configs.append(json.loads(f.read()))
        for config in configs:
            main_compose = config["apps"][0]
            Context._applications.append(
                Application(
                    main_compose["compose_name"],
                    main_compose["name"],
                    main_compose["timestamp"],
                    main_compose["version"],
                    config["application_id"],
                    Status(config["status"]))
            )


class Action(str, Enum):
    INSTALL = "INSTALL"
    DELETE = "DELETE"


class Status(str, Enum):
    RUNNING = "RUNNING"
    ERROR = "ERROR"


def generate_name():
    return petname.Generate()


class Application:
    def __init__(self, compose_name, app_name,
                 timestamp=None, version="0.0.1", application_id=None, status=Status.RUNNING):
        if application_id is None:
            application_id = generate_name()
        if timestamp is None:
            timestamp = time.time()
        self.id = application_id
        self.app_name = app_name
        self.compose_name = compose_name
        self.version = version
        self.status = status
        self.start_timestamp = timestamp
        logging.debug(f"Adding application {self.id} to context.")

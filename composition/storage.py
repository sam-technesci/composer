import errno
import json
import logging
import os.path
import shutil
import sys
import tempfile
import time
import uuid
from os.path import join
from pathlib import Path
import yaml

from composition.models import Status


def get_yaml(loc):
    val = None
    with open(loc, "r") as stream:
        try:
            val = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return val


def create_storage_if_not_exist():
    storage_path = os.path.join(Path.home(), ".composer")
    if not os.path.exists(storage_path):
        os.mkdir(storage_path)
    if not os.path.isdir(storage_path):
        logging.error(f"Path: {storage_path} used for local storage is already in use.")
        logging.error("Please remove the file there and try again. Exiting.")
        sys.exit(1)
    if not is_writeable(storage_path):
        logging.error(f"Path {storage_path} for local storage is not writeable, exiting.")
        sys.exit(1)


def is_writeable(path):
    # Temp file is automatically deleted
    try:
        testfile = tempfile.TemporaryFile(dir=path)
        testfile.close()
    except OSError as e:
        if e.errno == errno.EACCES:
            return False
        e.filename = path
        raise
    return True


def update_status(application_id, status: Status):
    application_path = os.path.join(Path.home(), ".composer", application_id)
    config_path = os.path.join(application_path, "config.json")
    if not os.path.exists(config_path):
        logging.error(f"Config path does not exist {config_path}")
        sys.exit(1)
    with open(config_path, "r") as f:
        json_out = json.loads(f.read())
    json_out["status"] = status
    with open(config_path, "w") as f:
        f.write(json.dumps(json_out))


def append_to_app_config(app_details, application_id):
    application_path = os.path.join(Path.home(), ".composer", application_id)
    config_path = os.path.join(application_path, "config.json")
    # If the config file does not already exist
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(json.dumps({
                "application_id": application_id,
                "status": Status.RUNNING,
                "apps": [
                    app_details
                ]
            }))
    # If the config file already exists
    else:
        # Read the file and update it
        with open(config_path, "r") as f:
            json_out = json.loads(f.read())
        json_out["apps"].append(app_details)
        # Overwrite the existing config
        with open(config_path, "w") as f:
            f.write(json.dumps(json_out))


def write_compose(application_id, output_str, app_details, compose_path, template_dir):
    application_path = os.path.join(Path.home(), ".composer", application_id)
    if not os.path.exists(application_path):
        os.mkdir(application_path)
    # Use a UUID as we can have multiple composes per app and we don't want them to overlap
    guid = str(uuid.uuid4())
    # Add to the config
    app_details["guid"] = guid
    app_details["timestamp"] = time.time()
    app_details["compose_name"] = compose_path
    append_to_app_config(app_details, application_id)
    compose_path = os.path.join(application_path, guid)
    # Copy all files from current directory
    # Unless they are in .composer_ignore
    ignore_contents = get_ignore_contents()
    shutil.copytree(template_dir, compose_path,
                    ignore=ignore_patterns_override(*ignore_contents))
    path = os.path.join(compose_path, "docker-compose.yaml")
    with open(path, "w") as f:
        f.write(output_str)
    return path


def remove(application_id):
    location = os.path.join(Path.home(), ".composer", application_id)
    shutil.rmtree(location)
    logging.info(f"Application: '{application_id}' uninstalled.")


def get_ignore_contents():
    ignore_file = join(os.getcwd(), ".composerignore")
    if not os.path.exists(ignore_file):
        return []
    with open(ignore_file, 'r') as f:
        return f.readlines()


def ignore_patterns_override(*patterns):
    """Function that can be used as copytree() ignore parameter.
    Patterns is a sequence of glob-style patterns
    that are used to exclude files/directories"""

    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            for path in Path(os.getcwd()).rglob(pattern):
                ignored_names.append(str(path))
        for f in names:
            for pattern in patterns:
                if os.path.abspath(join(path, f)) == pattern:
                    ignored_names.append(f)
        return set(ignored_names)

    return _ignore_patterns

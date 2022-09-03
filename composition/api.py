import logging
import os.path
import subprocess
import sys

from composition import storage
from composition.models import Status


def is_compose_installed():
    return compose_cmd("docker-compose", "version").returncode == 0


def compose_cmd(*args, shell=True):
    logging.debug(f"Running command: {args}")
    return subprocess.run(args, capture_output=True, text=True, shell=shell)


def compose_up(app_name, path, application_id):
    out = compose_cmd(f"docker-compose", "-f", path, "up", "-d", shell=False)
    if out.returncode != 0 or "error" in out.stderr.lower():
        storage.update_status(application_id, Status.ERROR)
        logging.error(f"Error: {out.stderr}")
        logging.error(f"docker-compose up has failed for app {app_name}")
        sys.exit(1)
    logging.debug(out)


def compose_down(path, application_id, force=False):
    path = os.path.join(path, "docker-compose.yaml")
    if force:
        out = compose_cmd("docker-compose", "-f", path, "down", "--timeout=0", shell=False)
    else:
        out = compose_cmd("docker-compose", "-f", path, "down", shell=False)
    if out.returncode != 0 or "error" in out.stderr.lower():
        storage.update_status(application_id, Status.ERROR)
        logging.warning(f"Error: {out.stderr}")
        logging.warning(f"docker-compose down has failed for app {application_id}")
        logging.warning("Still removing application, but some containers might still persist")
    logging.debug(out)


def unbuffered_command(*command_line_args):
    process = subprocess.Popen(command_line_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with process.stdout:
        log_subprocess_output(process.stdout)
    return process.wait()  # 0 means success


def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''):  # b'\n'- separated lines
        logging.info(line.decode().rstrip('\n'))


def compose_logs(path, follow, service):
    path = os.path.join(path, "docker-compose.yaml")
    cmd = ["docker-compose", "-f", path, "logs"]
    if service is not None:
        cmd.append(service)
    if follow:
        cmd.append("-f")
    out = unbuffered_command(*cmd)
    if out != 0:
        logging.error("An error has occurred retrieving logs from application.")
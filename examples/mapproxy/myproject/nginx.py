from importlib import resources
import jinja2
import os
import socket
import tempfile

from servicectl import service, command
from servicectl.process import process, pid, wait_write_close

from .config import config


class nginx(service):

    dependencies = (
        "myproject.mapproxy:mapproxy",
    )

    def get_config(self):
        return jinja2.Template(resources.read_text("myproject.config",
                                                   "nginx.conf")) \
                     .render(config)

    @command()
    def start(self):
        os.makedirs(config["nginx_temp_path"], exist_ok=True)
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".conf") as nginx_cfg_file, \
                 wait_write_close(config["nginx_pid"], 3):
                nginx_cfg_file.write(self.get_config())
                nginx_cfg_file.flush()
                process(("nginx",
                         "-c", nginx_cfg_file.name,
                         "-e", config["nginx_error_log"]),
                        stdout=self.log.info, stderr=self.log.error).run()
        except wait_write_close.file_not_found:
            self.log.error("No nginx.pid file")
            return False
        return pid(config["nginx_pid"]).alive()

    @command()
    def stop(self):
        try:
            return pid(config["nginx_pid"]).kill()
        except FileNotFoundError:
            return False

    @command()
    def status(self):
        try:
            with socket.create_connection(("localhost", config["nginx_port"])):
                return True
        except Exception as e:
            self.log.info(e)
            return False

    @command()
    def print_config(self):
        print(self.get_config())
        return True

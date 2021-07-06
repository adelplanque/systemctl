from importlib import resources
import jinja2
import tempfile

from servicectl import service, command
from servicectl.process import process, pid, wait_write_close

from .config import config


class nginx(service):

    dependencies = (
        "otherproject.gunicorn:gunicorn",
    )

    def get_config(self):
        return jinja2.Template(resources.read_text("otherproject.config",
                                                   "nginx.conf")) \
                     .render(config)

    @command()
    def start(self):
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".conf") as nginx_cfg_file, \
                 wait_write_close(config["nginx_pid"], 3):
                nginx_cfg_file.write(self.get_config())
                nginx_cfg_file.flush()
                cmd = ("nginx", "-c", nginx_cfg_file.name)
                process(cmd, stdout=self.log.info, stderr=self.log.error) \
                    .run()
        except wait_write_close.file_not_found:
            self.log.error("No nginx.pid file")
            return False
        return pid(config["nginx_pid"]).alive()

    @command()
    def stop(self):
        return pid(config["nginx_pid"]).kill()

    @command()
    def print_config(self):
        """
        Print nginx configuration file.
        """
        print(self.get_config())

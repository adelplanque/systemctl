from importlib import resources
import jinja2
import tempfile

from servicectl import service, command
from servicectl.process import process, pid, wait_write_close

from .config import config


class mapproxy(service):

    dependencies = (
        "myproject.redis:redis",
    )

    @command()
    def start(self):
        config_uwsgi = \
            jinja2.Template(resources.read_text("myproject.config", "uwsgi.ini")) \
                  .render(config)
        config_mapproxy = \
            jinja2.Template(resources.read_text("myproject.config", "uwsgi.ini")) \
                  .render(config)
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".ini") as uwsgi_cfg_file, \
                 tempfile.NamedTemporaryFile("w") as mapproxy_cfg_file, \
                 wait_write_close(config["uwsgi_pid"], 3):
                uwsgi_cfg_file.write(config_uwsgi)
                uwsgi_cfg_file.flush()
                mapproxy_cfg_file.write(config_mapproxy)
                mapproxy_cfg_file.flush()
                process(("uwsgi", uwsgi_cfg_file.name),
                        stdout=self.log.info, stderr=self.log.error) \
                    .daemonize() \
                    .run()
        except wait_write_close.file_not_found:
            self.log.error("No uwsgi.pid file")
            return False
        return pid(config["uwsgi_pid"]).alive()

    @command()
    def stop(self):
        try:
            return pid(config["uwsgi_pid"]).kill()
        except FileNotFoundError:
            return False

    @command()
    def status(self):
        try:
            return pid(config["uwsgi_pid"]).alive()
        except FileNotFoundError:
            return False

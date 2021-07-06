from importlib import resources
import jinja2
import tempfile

from servicectl import service, command
from servicectl.process import process, pid, wait_write_close

from .config import config


class redis(service):

    @command()
    def start(self):
        config_redis = \
            jinja2.Template(resources.read_text("myproject.config", "redis.conf")) \
                  .render(config)
        try:
            with tempfile.NamedTemporaryFile("w") as cfg_file, \
                 wait_write_close(config["redis_pid"], 30):
                cfg_file.write(config_redis)
                cfg_file.flush()
                process(("redis-server", cfg_file.name),
                        stdout=self.log.info, stderr=self.log.error).run()
        except wait_write_close.file_not_found:
            self.log.error("No redis.pid file")
            return False
        return pid(config["redis_pid"]).alive()

    @command()
    def stop(self):
        try:
            return pid(config["redis_pid"]).kill()
        except FileNotFoundError:
            return False

    @command()
    def status(self):
        try:
            return pid(config["redis_pid"]).alive()
        except FileNotFoundError:
            return False

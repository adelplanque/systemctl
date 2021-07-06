from servicectl import service, command
from servicectl.process import process, pid, wait_write_close

from .config import config


class gunicorn(service):

    dependencies = (
        "otherproject.postgresql:postgresql",
    )

    @command()
    def start(self):
        options = {
            "bind": "unix:%s" % config["gunicorn_socket"],
            "pid": config["gunicorn_pid"],
            "max-requests": 500,
            "max-requests-jitter": 100,
            "limit-request-line": 8192,
            "log-level": "info",
            "preload": None,
            "daemon": None,
            "workers": config["gunicorn_workers"],
            "threads": 1,
            "timeout": 305,
            "log-file": config["gunicorn_log"],
            "capture-output": None,
            "access-logfile": config["gunicorn_access_log"],
        }
        cmd = ["gunicorn"]
        cmd.extend(f"--{option}" if value is None else f"--{option}={value}"
                   for option, value in options.items())
        cmd.append("otherproject.djangoapp.wsgi")
        try:
            with wait_write_close(config["gunicorn_pid"], 30):
                process(cmd, stdout=self.log.info, stderr=self.log.error).run()
        except process.run_process_error as e:
            self.log.critical(e)
            return False
        except wait_write_close.file_not_found:
            self.log.error("No gunicorn.pid file")
            return False
        return True

    @command()
    def status(self):
        try:
            return pid(config["gunicorn_pid"]).alive()
        except FileNotFoundError:
            self.log.warning("No gunicorn.pid file")
            return False

    @command()
    def stop(self):
        try:
            return pid(config["gunicorn_pid"]).kill()
        except FileNotFoundError as e:
            self.log.critical(e)
            return False

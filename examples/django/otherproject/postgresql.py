from importlib import resources
import functools
import jinja2
import os
import shutil
import subprocess
import tempfile

from servicectl import service, command
from servicectl.process import process

from .config import config


@functools.lru_cache
def which(binary):
    """
    Search for binary file.
    """
    prog = shutil.which(binary)
    if prog:
        return prog
    if shutil.which("dpkg"):
        # On ubuntu pg_ctl/initdb are not in PATH
        p = subprocess.Popen(("dpkg", "-S", binary), stdout=subprocess.PIPE)
        candidates = [
            filepath
            for filepath in (line.decode("utf-8").split(":")[1].strip()
                             for line in p.stdout)
            if os.path.basename(filepath) == binary
            and os.access(filepath, os.X_OK)
        ]
        if candidates:
            return max(candidates)
    raise RuntimeError(f"{binary} not found")


class postgresql(service):

    @command()
    def start(self):
        process((which("pg_ctl"), "start", "-w",
                 "-D", config["postgres_datadir"],
                 "-o", "-p %s" % config['postgres_port'],
                 "-l", config["postgres_postmaster_log"]),
                stdout=self.log.info, stderr=self.log.error).run()
        return self.status()

    @command()
    def init(self):
        # initdb
        shutil.rmtree(config["postgres_datadir"], ignore_errors=True)
        with tempfile.NamedTemporaryFile("w") as pwfile:
            pwfile.write(f"{config['postgres_password']}\n")
            pwfile.flush()
            process((which("initdb"),
                     "--pgdata=%s" % config["postgres_datadir"],
                     "--encoding=UTF8",
                     "--username=%s" % config["postgres_username"],
                     "--pwfile=%s" % pwfile.name),
                    stdout=self.log.info, stderr=self.log.warning).run()
        env = jinja2.Environment(keep_trailing_newline=True)
        env.filters["basename"] = os.path.basename
        env.filters["dirname"] = os.path.dirname
        config_pg = \
            env.from_string(resources.read_text("otherproject.config",
                                                "postgres.conf")) \
               .render(config)
        with open(os.path.join(config["postgres_datadir"],
                               "postgresql.conf"), "w") as cfg_file:
            cfg_file.write(config_pg)

        with self:
            # createdb
            process(("createdb", "--host=localhost",
                     "--port=%s" % config["postgres_port"],
                     "--username=%s" % config["postgres_username"],
                     config["postgres_dbname"]),
                    stdout=self.log.info, stderr=self.log.error).run()
            # Run init script
            with tempfile.NamedTemporaryFile("w") as sql_file:
                sql_file.write(resources.read_text("otherproject.config",
                                                   "setup-db.sql"))
                sql_file.flush()
                process(("psql", "-h", "localhost",
                         "-p", str(config["postgres_port"]),
                         "-U", config["postgres_username"],
                         "-f", sql_file.name),
                        stdout=self.log.info, stderr=self.log.error).run()

        pg_hba = \
            env.from_string(resources.read_text("otherproject.config",
                                                "pg_hba.conf")) \
               .render(config)
        with open(os.path.join(config["postgres_datadir"],
                               "pg_hba.conf"), "w") as cfg_file:
            cfg_file.write(pg_hba)

        return True

    @command()
    def stop(self):
        try:
            process((which("pg_ctl"),
                     "--pgdata=%s" % config["postgres_datadir"],
                     "-w", "stop", "-m", "fast"),
                    stdout=self.log.info, stderr=self.log.error).run()
            return True
        except process.run_process_error:
            return False

    @command()
    def status(self):
        try:
            process(("pg_isready",
                     "--dbname=%s" % config["postgres_dbname"],
                     "--host=localhost",
                     "--port=%s" % config["postgres_port"],
                     "--username=%s" % config["postgres_username"]),
                    stdout=self.log.info, stderr=self.log.error).run()
            return True
        except process.run_process_error:
            return False

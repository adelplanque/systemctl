import inotify.adapters
import inotify.constants
import itertools
import logging
import os
import shlex
import shutil
import signal
import socket
import subprocess
import threading
import time


class thread_logger(object):

    def __init__(self, stream, writer):
        self._stream = stream
        self._writer = writer
        self._t = threading.Thread(target=self._process)
        self._t.start()

    def _process(self):
        for line in self._stream:
            line = line.rstrip().decode("utf-8", errors="replace")
            self._writer(line)


class process(object):

    class run_process_error(Exception):
        pass

    def __init__(self, cmd, stdout, stderr, env=None, **kwargs):
        self._cmd = cmd
        self._stdout = stdout
        self._stderr = stderr
        self._env = env
        self._kwargs = kwargs

    def daemonize(self):
        self._cmd = tuple(itertools.chain(
            ("daemonize", shutil.which(self._cmd[0])), self._cmd[1:])
        )
        return self

    def run(self):
        kwargs = {
            "stdout": subprocess.PIPE if callable(self._stdout) else self._stdout,
            "stderr": subprocess.PIPE if callable(self._stderr) else self._stderr
        }
        if self._env:
            env = dict(os.environ)
            env.update(self._env)
            kwargs["env"] = env
        kwargs.update(self._kwargs)
        cmd_str = " ".join(shlex.quote(x) for x in self._cmd)
        logging.getLogger("servicectl").debug(f"RUN: {cmd_str}")
        p = subprocess.Popen(self._cmd, **kwargs)
        if callable(self._stdout):
            thread_logger(p.stdout, self._stdout)
        if callable(self._stderr):
            thread_logger(p.stderr, self._stderr)
        p.wait()
        if p.returncode:
            raise self.run_process_error(
                f"COMMAND `{cmd_str}` fail with return code {p.returncode}")


class wait_write_close(object):
    """
    Context manager to wait for the write closing event on a file to move on.
    """

    class file_not_found(Exception):
        """
        Exception raised when the expected file is not found.
        """

    def __init__(self, filename, timeout):
        self._filename = filename
        self._timeout = timeout

    def __enter__(self):
        self.i = inotify.adapters.Inotify()
        self.i.add_watch(os.path.dirname(self._filename),
                         mask=inotify.constants.IN_CLOSE_WRITE)

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            return
        basename = os.path.basename(self._filename)
        for event in self.i.event_gen(yield_nones=False,
                                      timeout_s=self._timeout):
            _, _, _, filename = event
            if filename == basename:
                return
        raise self.file_not_found()


class pid(object):
    """
    Manage an existing process given by its pid.
    """

    def __init__(self, pid):
        if isinstance(pid, str):
            with open(pid, "r") as pidfile:
                self.pid = int(pidfile.read())
        else:
            self.pid = pid

    def kill(self, timeout=30):
        """
        Send TERM signal to `pid` process.
        If process is still alive after `timeout`, send KILL signal
        """
        try:
            os.kill(self.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        limit = time.time() + timeout
        while time.time() < limit:
            time.sleep(.1)
            try:
                os.kill(self.pid, 0)
                continue
            except ProcessLookupError:
                return True
        try:
            os.kill(self.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            os.kill(self.pid, 0)
            return False
        except ProcessLookupError:
            return True

    def alive(self):
        """
        Check if the process is still alive.

        Return:
            Boolean, True if process is alive.
        """
        try:
            os.kill(self.pid, 0)
            return True
        except ProcessLookupError:
            return False


def wait_tcp_connection(hostname, port, timeout=30):
    """
    Wait until a port starts accepting TCP connections.
    Args:
        hostname (str): Host on which the port should exist.
        port (int): Port number.
        timeout (float): In seconds. How long to wait before raising errors.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified
            in `timeout`.
    """
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((hostname, port), timeout=timeout):
                break
        except OSError:
            time.sleep(0.01)
            if time.time() - start_time >= timeout:
                raise TimeoutError(
                    f"Unable to establish a connection to {hostname}:{port} "
                    f"after {timeout} s")

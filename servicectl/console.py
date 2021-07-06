import io
import os
import sys
import threading


class console(dict):

    def __init__(self):
        self._ttys = {}

    def _get_tty(self, stream):
        name = os.ttyname(stream.fileno())
        if name not in self._ttys:
            self._ttys[name] = tty(stream)
        return self._ttys[name]

    def __enter__(self):
        self._stdout = sys.stdout
        if sys.stdout.isatty():
            sys.stdout = self._get_tty(sys.stdout)
        else:
            sys.stdout = notty(sys.stdout)
        self._stderr = sys.stderr
        if sys.stderr.isatty():
            sys.stderr = self._get_tty(sys.stderr)
        else:
            sys.stderr = notty(sys.stderr)

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self._stdout
        sys.stderr = self._stderr


class tty(io.TextIOWrapper):

    status = {
        "ok": "\u001b[32mOK      \u001b[0m",
        "fail": "\u001b[31mFAIL    \u001b[0m",
        "canceled": "\u001b[33CANCELED\u001b[0m",
    }

    def __init__(self, wrapped):
        super().__init__(wrapped.buffer, encoding=wrapped.encoding,
                         errors="replace", newline=wrapped.newlines,
                         line_buffering=True, write_through=True)
        self._lineno = 0
        self._tags = {}
        self._lock = threading.Lock()

    def write(self, data, tag=None):
        with self._lock:
            if tag is not None:
                self._tags[tag] = self._lineno
            super().write(data)
            super().flush()
            self._lineno += data.count("\n")

    def write_status(self, status, tag):
        with self._lock:
            dlines = self._lineno - self._tags.get(tag, self._lineno)
            super().write("\u001b[s\u001b[%dA\u001b[50C[ %s ]\u001b[u"
                          % (dlines, self.status[status]))
            super().flush()


class notty(object):

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._tags = {}

    def __getattr__(self, name):
        return self._wrapped.__getattr__(name)

    def write(self, data, tag=None):
        if tag is not None:
            self._tags[tag] = data
        self._wrapped.write(data)
        self._wrapped.flush()

    def write_status(self, status, tag):
        self._wrapped.write(
            "%s [ %s ]\n" % (self._tags.get(tag, "").rstrip(), status.upper()))
        self._wrapped.flush()

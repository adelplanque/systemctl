import concurrent.futures
import errno
import fcntl
import itertools
import os
import sys
import threading
import time
import logging


class scheduler(object):

    def __init__(self, dependencies, args):
        self._dependencies = dependencies
        self._args = args

    def _setup_tasks(self):
        tasks = {}
        for cmd in set(itertools.chain.from_iterable(self._dependencies)):
            if cmd is None:
                continue
            tasks[cmd] = task(cmd.get_callable(self._args))
        for a, b in self._dependencies:
            if b is None:
                continue
            tasks[a].depend(tasks[b])
        return set(tasks.values())

    def _tasks(self):
        tasks = self._setup_tasks()

        def deep_first_iterate(task):
            if task not in tasks:
                return
            tasks.remove(task)
            for dep in task.dependencies:
                for t in deep_first_iterate(dep):
                    yield t
            yield(task)

        while tasks:
            for t in deep_first_iterate(next(iter(tasks))):
                yield t

    def run(self):
        pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._args.workers)
        fs = [pool.submit(task.run) for task in self._tasks()]
        return all([x.result() for x in fs])


class flock(object):

    def __init__(self, lockname, timeout=30):
        self._lockname = lockname
        self._timeout = timeout

    def __enter__(self):
        log = logging.getLogger("scheduler")
        log.debug("Get file lock: %s", self._lockname)
        start_time = time.time()
        first = True
        self._fd = os.open(self._lockname, os.O_CREAT | os.O_WRONLY, 0o660)
        while True:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError as e:
                if e.errno == errno.EWOULDBLOCK:
                    if first:
                        log.warning(
                            f"{self._lockname} is hold by another "
                            f"process. Wait at most {self._timeout} s")
                        first = False
                    time.sleep(0.1)
                    if time.time() - start_time > self._timeout:
                        break
                else:
                    raise e
        raise TimeoutError()

    def __exit__(self, exc_type, exc_value, tb):
        fcntl.flock(self._fd, fcntl.LOCK_UN)
        os.close(self._fd)


class task(object):

    def __init__(self, fct):
        self._fct = fct
        self.dependencies = set()
        self._lock = threading.Lock()
        self._lock.acquire()

    def depend(self, t):
        self.dependencies.add(t)

    def wait(self):
        """
        Wait until task is done
        """
        with self._lock:
            pass

    def run(self):
        for task in self.dependencies:
            task.wait()
        try:
            if callable(self._fct):
                sys.stdout.write("- %s...\n" % self._fct.__doc__, tag=id(self))
                lockname = os.path.join(
                    "/tmp",
                    ".".join((self._fct.__module__,
                              self._fct.__qualname__, "lock"))
                )
                try:
                    with flock(lockname):
                        result = self._fct()
                except TimeoutError:
                    logging.getLogger("scheduler").critical(
                        f"Command {self._fct.__qualname__} is locked by "
                        f"another process")
                    result = False
                except Exception as e:
                    logging.getLogger("scheduler").critical(
                        f"Can't acquire file lock {lockname}: {e}")
                    result = False
                sys.stdout.write_status("ok" if result else "fail", tag=id(self))
            else:
                result = True
        finally:
            self._lock.release()
        return result

    def __repr__(self):
        return "task(%s)" % (self._fct if callable(self._fct)
                             else "empty task %s" % id(self))

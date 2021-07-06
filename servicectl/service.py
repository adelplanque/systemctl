import argparse
import functools
import importlib
import logging
import sys

from .commands import _command_descriptor, command, restart_command
from .console import console
from .logs import setup_logging
from .scheduler import scheduler


def _resolve(obj):
    if isinstance(obj, str):
        mod_name, obj_name = obj.split(":")
        obj = functools.reduce(lambda obj, name: getattr(obj, name),
                               obj_name.split("."),
                               importlib.import_module(mod_name))
    return obj


class _service(type):

    def __new__(meta, name, bases, attrs):
        attrs.setdefault("name", name)
        attrs.setdefault("_abstract", False)
        commands = {}
        dependencies = set(attrs.get("dependencies") or ())
        for cls in reversed(bases):
            commands.update(getattr(cls, "_commands", ()))
            dependencies.update(getattr(cls, "dependencies", ()))
        commands.update((x.name, x) for x in attrs.values()
                        if isinstance(x, _command_descriptor))
        attrs["_commands"] = commands
        attrs["dependencies"] = dependencies
        attrs.setdefault("cli_name", None)
        return super().__new__(meta, name, bases, attrs)


class baseservice(object, metaclass=_service):

    _abstract = True

    def __init__(self, args):
        self.args = args
        self.log = logging.getLogger(self.name)

    def service_instance(self, name):
        return _resolve(name)(self.args)

    @classmethod
    def resolve_command(cls, descr, cmd_name):
        obj = _resolve(descr)
        if issubclass(obj, baseservice):
            return getattr(obj, cmd_name)
        return obj

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser(
            description=cls.__doc__ or f"Service {cls.name}"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="count",
            help="More verbose output (max -vvv)"
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=8,
            help="Number of executors in parallel (default 8)"
        )
        subparsers = parser.add_subparsers(help="Commands", dest="cmd")
        subparsers.required = True
        for cmd in sorted(cls._commands.values(), key=lambda x: x.name):
            cmd.setup_subparser(subparsers)
        return parser.parse_args()

    @classmethod
    def main(cls):
        with console():
            args = cls.parse_args()
            setup_logging(args)
            res = scheduler(getattr(cls, args.cmd).dependencies(), args).run()
            sys.exit(0 if res else 1)


class service(baseservice):

    _abstract = True

    @command()
    def start(self):
        self.log.error("Start command not implemented")
        return False

    @command()
    def stop(self):
        self.log.error("Stop command not implemented")
        return False

    restart = _command_descriptor(
        main=None,
        name="restart",
        command_class=restart_command
    )

    @command()
    def init(self):
        self.log.error("Init command not implemented")
        return False

    @command()
    def status(self):
        self.log.error("Status command not implemented")
        return False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()

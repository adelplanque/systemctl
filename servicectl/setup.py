import importlib
import inspect
import itertools
import pkgutil
import setuptools

from .service import service


def collect_modules(packages):
    for pkg in packages:
        try:
            mod = importlib.import_module(pkg)
            yield mod
        except ImportError:
            print(f"Can't import `{pkg}`")
        if not hasattr(mod, "__path__"):
            continue
        for importer, name, ispkg in pkgutil.iter_modules(mod.__path__):
            if ispkg:
                continue
            try:
                yield importlib.import_module("%s.%s" % (pkg, name))
            except ImportError:
                print(f"Can't import `{pkg}.{name}`")


class command(object):

    def __init__(self, service):
        self._service = service

    def entry_point(self, project_name):
        cli = self._service.cli_name or f"{project_name}.{self._service.name}"
        return f"{cli} = {self._service.__module__}:{self._service.__qualname__}.main"


def collect_commands(packages):
    for mod in collect_modules(packages):
        for name, obj in mod.__dict__.items():
            if (
                    inspect.isclass(obj) and issubclass(obj, service)
                    and not obj._abstract
            ):
                yield command(obj)


def setup(*args, **kwargs):
    project_name = kwargs["name"]
    packages = kwargs.get("packages") or ()
    entry_points = kwargs.setdefault("entry_points", {})
    entry_points["console_scripts"] = tuple(itertools.chain(
        entry_points.get("console_scripts", ()),
        (x.entry_point(project_name) for x in collect_commands(packages))
    ))
    setuptools.setup(*args, **kwargs)

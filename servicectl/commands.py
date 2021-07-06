import functools
import itertools
import types


class _command_meta(object):

    def __init__(self, **kwargs):
        self.main = kwargs.get("main")
        self.name = kwargs.get("name")
        self.recursive = kwargs.get("recursive", "no")
        self.dependencies = kwargs.get("dependencies")


class default_command(object):

    def __init__(self, meta, service):
        self._service = service
        self._meta = meta

    def _resolve(self, name):
        return self._service.resolve_command(name, self._meta.name)

    def _expand_dependency(self, dep):
        if isinstance(dep, (tuple, list)):
            return tuple(self._resolve(x) for x in dep)
        return (self, self._resolve(dep))

    def _direct_dependencies(self):
        local_deps = self._meta.dependencies or self._service.dependencies
        if not local_deps:
            return set(((self, None), ))
        dependencies = set()
        for a, b in (self._expand_dependency(dep) for dep in local_deps):
            dependencies.add((a, b))
            if b != self:
                dependencies.update(b._direct_dependencies())
        return dependencies

    def _reverse_dependencies(self):
        local_deps = self._meta.dependencies or self._service.dependencies
        dependencies = set(((self, None), ))
        for a, b in (self._expand_dependency(dep) for dep in local_deps):
            dependencies.add((b, a))
            if b != self:
                dependencies.update(b._reverse_dependencies())
        return dependencies

    def dependencies(self, recursive=None):
        """
        Dependencies set of command to be executed.
        """
        recursive = recursive or self._meta.recursive
        if recursive == "no":
            return set(((self, None), ))
        elif recursive == "yes":
            return self._direct_dependencies()
        elif recursive == "reverse":
            return self._reverse_dependencies()
        raise RuntimeError(f"Illegal recursive value: {recursive}")

    def get_callable(self, args):
        """
        Return the function bound to the service instance according to the
        command line arguments.
        """
        service = self._service(args)

        @functools.wraps(self._meta.main)
        def wrapped(*args, **kwargs):
            try:
                return self._meta.main(service, *args, **kwargs)
            except Exception as e:
                service.log.critical("%s: %s", e.__class__.__name__, e)
                return False
        if not wrapped.__doc__:
            wrapped.__doc__ = \
                f"{self._meta.name.capitalize()} {self._service.name} service"
        return wrapped

    def __repr__(self):
        return f"<Command {self._service.name}.{self._meta.name}>"


class restart_command(default_command):

    def dependencies(self, recursive=None):
        """
        Dependencies set of command to be executed.
        """
        recursive = recursive or self._meta.recursive
        dependencies = set()
        start_dependencies = self._service.start.dependencies()
        dependencies.update(start_dependencies)
        stop_dependencies = self._service.stop.dependencies()
        dependencies.update(stop_dependencies)
        stop_commands = set(itertools.chain.from_iterable(stop_dependencies))
        for a, b in start_dependencies:
            if b is None:
                dependencies.update((a, x) for x in stop_commands)
        return dependencies


class _command_descriptor(object):
    """
    Command descriptor.
    """

    def __init__(self, **kwargs):
        self._meta = _command_meta(**kwargs)
        self.name = self._meta.name
        self._class = kwargs.get("command_class", default_command)
        self._commands = {}

    def __get__(self, instance, owner=None):
        """
        Return bounded command to service instance.
        """
        if instance is None and owner:
            if owner not in self._commands:
                self._commands[owner] = self._class(self._meta, owner)
            return self._commands[owner]
        elif instance and self._meta.main:
            return types.MethodType(self._meta.main, instance)
        else:
            return self._meta.main

    def __set__(self, service, fct):
        self._main = fct

    def setup_subparser(self, subparsers):
        cmd_help = self._meta.main.__doc__ \
            or f"{self._meta.name.capitalize()} service"
        parser = subparsers.add_parser(
            self._meta.name,
            help=cmd_help
        )
        parser.add_argument(
            "--recursive", "-r",
            choices=("yes", "no", "reverse", ),
            default=self._meta.recursive,
            help=f"Execute the command recursively for dependent services "
            f"(default {self._meta.recursive})."
        )

    def __repr__(self):
        return f"<Command descriptor {self._meta.name}>"


def command(**kwargs):
    """
    Create a service management command.
    """
    def _decorator(fct):
        kwargs["main"] = fct
        kwargs["name"] = fct.__name__
        return _command_descriptor(**kwargs)
    return _decorator

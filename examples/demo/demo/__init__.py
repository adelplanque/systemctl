import time

from servicectl import service, command


class postgres(service):

    @command()
    def start(self):
        time.sleep(2)


class redis2http(service):

    dependencies = (
        "demo:nginx",
    )

    @command()
    def start(self):
        time.sleep(2)


class django2(service):

    dependencies = (
        "demo:postgres",
    )

    @command()
    def start(self):
        time.sleep(1)


class djangomonitor2(service):

    dependencies = (
        "demo:django2",
    )

    @command()
    def start(self):
        time.sleep(.1)


class django3(service):

    dependencies = (
        "demo:postgres",
    )

    @command()
    def start(self):
        time.sleep(1)


class djangomonitor3(service):

    dependencies = (
        "demo:django3",
    )

    @command()
    def start(self):
        time.sleep(.1)


class nginx(service):

    dependencies = (
        "demo:django2",
        "demo:django3"
    )

    @command()
    def start(self):
        time.sleep(1)


class main(service):

    cli_name = "demo"

    dependencies = (
        "demo:postgres",
        "demo:django2",
        "demo:djangomonitor2",
        "demo:django3",
        "demo:djangomonitor3",
        "demo:nginx",
        "demo:redis2http",
    )

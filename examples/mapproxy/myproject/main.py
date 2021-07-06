from servicectl import service, command


class main(service):
    """
    Manage services for myproject.
    """

    cli_name = "myproject"

    dependencies = (
        "myproject.nginx:nginx",
        "myproject.mapproxy:mapproxy",
        "myproject.redis:redis",
    )

    @command(recursive="yes")
    def start(self):
        "Start all services"
        return True

    @command(recursive="reverse")
    def stop(self):
        "Stop all services"
        return True

    @command(recursive="yes")
    def status(self):
        return True

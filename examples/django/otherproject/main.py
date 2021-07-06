from servicectl import service, command


class main(service):
    """
    Manage services for myproject.
    """

    cli_name = "otherproject"

    dependencies = (
        "otherproject.nginx:nginx",
        "otherproject.gunicorn:gunicorn",
        "otherproject.postgresql:postgresql",
    )

    @command(recursive="yes")
    def start(self):
        "Start all services"
        return True

    @command(recursive="reverse")
    def stop(self):
        "Stop all services"
        return True

    @command(
        recursive="yes",
        dependencies=(
            "otherproject.postgresql:postgresql",
            "otherproject.django:django",
        )
    )
    def init(self):
        return True

    @command(recursive="yes")
    def status(self):
        return True

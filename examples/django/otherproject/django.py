import os

from servicectl import service, command
from servicectl.process import process


class django(service):

    def create_admin(self):
        from django import setup
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              "otherproject.djangoapp.settings")
        setup()
        from django.contrib.auth import get_user_model
        from django.contrib.auth.hashers import make_password
        User = get_user_model()
        User(username="admin", password=make_password("admin"),
             is_staff=True, is_superuser=True) \
            .save()

    @command(
        dependencies=(
            "otherproject.postgresql:postgresql",
        )
    )
    def init(self):
        with self.service_instance("otherproject.postgresql:postgresql"):
            process(("otherproject.manage", "collectstatic", "--noinput"),
                    stdout=self.log.info, stderr=self.log.error).run()
            process(("otherproject.manage", "migrate"),
                    stdout=self.log.info, stderr=self.log.error).run()
            self.create_admin()
        return True

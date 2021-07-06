import unittest
import time
import sys
from unittest import mock

from servicectl import service, command


class Test(unittest.TestCase):

    def test(self):
        start_times = {}

        class service1(service):

            @command()
            def start(self):
                start_times[self.__class__] = time.time()
                time.sleep(.2)
                return True

        class service2(service):

            @command()
            def start(self):
                start_times[self.__class__] = time.time()
                time.sleep(.2)
                return True

        class service3(service):

            dependencies = (
                service1,
                service2,
            )

            @command(recursive="yes")
            def start(self):
                start_times[self.__class__] = time.time()
                time.sleep(.2)
                return True

        with mock.patch.object(sys, "argv", ["service", "start"]):
            service3.main()

        self.assertTrue(start_times[service1] - start_times[service2] < .01)
        self.assertTrue(
            start_times[service3]
            - max(start_times[service1], start_times[service2]) >= .2)

import sys
import unittest
from unittest import mock

from servicectl import service, command


class testservice(service):

    @command()
    def start(self):
        print("real start")
        return True


class Test(unittest.TestCase):

    def test_command_called(self):
        print("toto")
        print(testservice.start)
        a = testservice.__dict__
        with mock.patch.object(sys, "argv", ["service", "start"]), \
             mock.patch.object(testservice, "start") as srv_mock:
            testservice.main()
            print(testservice.start)
            self.assertTrue(srv_mock.called)

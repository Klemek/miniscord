from unittest import TestCase
from unittest.mock import MagicMock, patch
import asyncio


class AsyncTestCase(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def _await(self, fn):
        return self.loop.run_until_complete(fn)


def pass_through(arg):
    return arg


def patch_discord(test):
    def wrapper(*args):
        m = MagicMock()
        m.event = pass_through
        with patch("discord.Client", return_value=m):
            test(*args)

    return wrapper

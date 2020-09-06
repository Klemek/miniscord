import functools
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


def __patch_discord_base(add_arg):
    def test_decorator(test):
        @functools.wraps(test)
        def wrapper(*args, **kwargs):
            client_mock = MagicMock()
            client_mock.event = pass_through
            with patch("discord.Client", return_value=client_mock):
                if add_arg:
                    test(*args, client_mock, **kwargs)
                else:
                    test(*args, **kwargs)

        return wrapper

    return test_decorator


def patch_discord_arg(test):
    return __patch_discord_base(True)(test)


def patch_discord(test):
    return __patch_discord_base(False)(test)

from unittest import TestCase, skip
from unittest.mock import Mock, MagicMock, AsyncMock
from tests.utils import AsyncTestCase

import discord
from datetime import datetime
from miniscord._bot import Bot


class TestInit(TestCase):
    def test_normal(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version")
        self.assertEqual("app_name", bot.app_name)
        self.assertEqual("version", bot.version)
        self.assertIsNone(bot.alias)
        discord.Client.assert_called_once()
        self.assertEqual(2, len(bot._Bot__commands))
        self.assertEqual(2, len(bot.games))

    def test_alias(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version", alias="alias")
        self.assertEqual("app_name", bot.app_name)
        self.assertEqual("version", bot.version)
        self.assertEqual("alias", bot.alias)
        discord.Client.assert_called_once()
        self.assertEqual(2, len(bot._Bot__commands))
        self.assertEqual(3, len(bot.games))


class TestInfo(AsyncTestCase):
    def test(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version")
        message = AsyncMock()
        t0 = datetime.now()
        bot._Bot__t0 = t0
        bot.client.guilds = [None, None, None]
        self._await(bot.info(None, message, "info"))
        message.channel.send.assert_awaited_once_with(
            f"```\n"
            f"app_name vversion\n"
            f"* Started at {t0:%Y-%m-%d %H:%M}\n"
            f"* Connected to 3 guilds\n"
            f"```"
        )


class TestHelp(AsyncTestCase):
    def test_list_minimal(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version")
        message = AsyncMock()
        self._await(bot.help(None, message, "help"))
        message.channel.send.assert_awaited_once_with(
            f"```\n"
            f"List of available commands:\n"
            f"* info: show description\n"
            f"* help: show this help\n"
            f"```"
        )

    def test_list_alias(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version", alias="¡")
        message = AsyncMock()
        self._await(bot.help(None, message, "help"))
        message.channel.send.assert_awaited_once_with(
            f"```\n"
            f"List of available commands:\n"
            f"* ¡info: show description\n"
            f"* ¡help: show this help\n"
            f"```"
        )

    def test_list_functions(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version")
        bot.register_command("", None, "test1: desc1", None)
        bot.register_command("", None, "test2: desc2", None)
        message = AsyncMock()
        self._await(bot.help(None, message, "help"))
        message.channel.send.assert_awaited_once_with(
            f"```\n"
            f"List of available commands:\n"
            f"* test2: desc2\n"
            f"* test1: desc1\n"
            f"* info: show description\n"
            f"* help: show this help\n"
            f"```"
        )

    def test_long(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version")
        bot.register_command("test1", None, None, "long desc")
        message = AsyncMock()
        self._await(bot.help(None, message, "help", "test1"))
        message.channel.send.assert_awaited_once_with("long desc")

    def test_long_regex(self):
        discord.Client = Mock()
        bot = Bot("app_name", "version")
        bot.register_command("test", None, None, "desc1")
        bot.register_command("t.*", None, None, "desc2")
        message = AsyncMock()
        self._await(bot.help(None, message, "help", "test"))
        message.channel.send.assert_awaited_once_with("desc2")


class TestRegisterCommand(TestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")


class TestOnMessage(AsyncTestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")


class TestOnReady(AsyncTestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")


class TestOnGuildJoin(AsyncTestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")


class TestOnGuildRemove(AsyncTestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")

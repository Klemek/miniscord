from unittest import TestCase, skip
from unittest.mock import AsyncMock
from tests.utils import AsyncTestCase, patch_discord

import discord
from datetime import datetime
from miniscord._bot import Bot


class TestInit(TestCase):
    @patch_discord
    def test_normal(self):
        bot = Bot("app_name", "version")
        self.assertEqual("app_name", bot.app_name)
        self.assertEqual("version", bot.version)
        self.assertIsNone(bot.alias)
        discord.Client.assert_called_once()
        self.assertEqual(2, len(bot._Bot__commands))
        self.assertEqual(2, len(bot.games))

    @patch_discord
    def test_alias(self):
        bot = Bot("app_name", "version", alias="alias")
        self.assertEqual("app_name", bot.app_name)
        self.assertEqual("version", bot.version)
        self.assertEqual("alias", bot.alias)
        discord.Client.assert_called_once()
        self.assertEqual(2, len(bot._Bot__commands))
        self.assertEqual(3, len(bot.games))


class TestInfo(AsyncTestCase):
    @patch_discord
    def test(self):
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
    @patch_discord
    def test_list_minimal(self):
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

    @patch_discord
    def test_list_alias(self):
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

    @patch_discord
    def test_list_functions(self):
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

    @patch_discord
    def test_long(self):
        bot = Bot("app_name", "version")
        bot.register_command("test1", None, None, "long desc")
        message = AsyncMock()
        self._await(bot.help(None, message, "help", "test1"))
        message.channel.send.assert_awaited_once_with("long desc")

    @patch_discord
    def test_long_regex(self):
        bot = Bot("app_name", "version")
        bot.register_command("test", None, None, "desc1")
        bot.register_command("t.*", None, None, "desc2")
        message = AsyncMock()
        self._await(bot.help(None, message, "help", "test"))
        message.channel.send.assert_awaited_once_with("desc2")


class TestRegisterCommand(TestCase):
    @patch_discord
    def test_normal(self):
        bot = Bot("app_name", "version")
        self.assertEqual(2, len(bot._Bot__commands))

        def fn():
            pass

        bot.register_command("^t[eo]a?st$", fn, "short", "long")
        self.assertEqual(3, len(bot._Bot__commands))
        cmd = bot._Bot__commands[0]
        self.assertEqual("^t[eo]a?st$", cmd.regex)
        self.assertEqual(fn, cmd.compute)
        self.assertEqual("short", cmd.help_short)
        self.assertEqual("long", cmd.help_long)

    @patch_discord
    def test_add_regex(self):
        bot = Bot("app_name", "version")
        bot.register_command("test", None, None, None)
        cmd = bot._Bot__commands[0]
        self.assertEqual("^test$", cmd.regex)


class TestOnMessage(AsyncTestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")


class TestOnReady(AsyncTestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")


class TestOnGuildJoin(AsyncTestCase):
    @patch_discord
    def test_no_log(self):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = None
        guild = AsyncMock()
        self._await(bot.on_guild_join(guild))
        # nothing
        # TODO test normal file path

    @skip
    def test_log(self):
        self.fail("not implemented")


class TestOnGuildRemove(AsyncTestCase):
    @patch_discord
    def test_no_log(self):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = None
        guild = AsyncMock()
        self._await(bot.on_guild_remove(guild))
        # nothing
        # TODO test normal file path

    @skip
    def test_log(self):
        self.fail("not implemented")

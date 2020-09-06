from unittest import TestCase, skip
from unittest.mock import AsyncMock, patch, MagicMock
from os import path
import os
from tests.utils import AsyncTestCase, patch_discord, patch_discord_arg

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
    LOG_PATH = "guilds.log"

    def setUp(self):
        super().setUp()
        if path.exists(self.LOG_PATH):
            os.remove(self.LOG_PATH)

    def tearDown(self):
        super().tearDown()
        if path.exists(self.LOG_PATH):
            os.remove(self.LOG_PATH)

    @patch_discord_arg
    def test_no_log(self, client_mock):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = None
        ex = Exception("test")
        client_mock.change_presence.side_effect = ex
        try:
            with patch("discord.Game") as game_mock:
                game_mock.return_value = "activity"
                self._await(bot.on_ready())
        except Exception as error:
            self.assertEqual(ex, error)
        client_mock.change_presence.assert_called_with(
            activity="activity",
            status=discord.Status.online
        )

    @patch_discord_arg
    def test_log_create(self, client_mock):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = self.LOG_PATH
        client_mock.change_presence.side_effect = Exception("test")
        client_mock.guilds = [MagicMock(), MagicMock()]
        client_mock.guilds[0].id = "id1"
        client_mock.guilds[0].name = "name1"
        client_mock.guilds[1].id = "id2"
        client_mock.guilds[1].name = "name2"
        d = datetime.now()
        try:
            with patch("discord.Game") as game_mock:
                game_mock.return_value = "activity"
                self._await(bot.on_ready())
        except:
            pass
        with open(self.LOG_PATH, encoding="utf-8", mode="r") as f:
            self.assertEqual(f"{d:%Y-%m-%d %H:%M} +id1: name1\n"
                             f"{d:%Y-%m-%d %H:%M} +id2: name2\n", f.read())

    @patch_discord_arg
    def test_log_exists(self, client_mock):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = self.LOG_PATH
        client_mock.change_presence.side_effect = Exception("test")
        client_mock.guilds = [MagicMock()]
        client_mock.guilds[0].id = "id1"
        client_mock.guilds[0].name = "name1"
        with open(self.LOG_PATH, encoding="utf-8", mode="w") as f:
            f.write("test")
        try:
            with patch("discord.Game") as game_mock:
                game_mock.return_value = "activity"
                self._await(bot.on_ready())
        except:
            pass
        with open(self.LOG_PATH, encoding="utf-8", mode="r") as f:
            self.assertEqual(f"test", f.read())


class TestOnGuildJoin(AsyncTestCase):
    LOG_PATH = "guilds.log"

    def setUp(self):
        super().setUp()
        if path.exists(self.LOG_PATH):
            os.remove(self.LOG_PATH)

    def tearDown(self):
        super().tearDown()
        if path.exists(self.LOG_PATH):
            os.remove(self.LOG_PATH)

    @patch_discord
    def test_no_log(self):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = None
        guild = AsyncMock()
        self._await(bot.on_guild_join(guild))
        self.assertFalse(path.exists(self.LOG_PATH))

    @patch_discord
    def test_log(self):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = self.LOG_PATH
        guild1 = AsyncMock()
        guild1.id = "id1"
        guild1.name = "name1"
        guild2 = AsyncMock()
        guild2.id = "id2"
        guild2.name = "name2"
        d = datetime.now()
        self._await(bot.on_guild_join(guild1))
        self._await(bot.on_guild_join(guild2))
        self.assertTrue(path.exists(self.LOG_PATH))
        with open(self.LOG_PATH, encoding="utf-8", mode="r") as f:
            self.assertEqual(f"{d:%Y-%m-%d %H:%M} +id1: name1\n"
                             f"{d:%Y-%m-%d %H:%M} +id2: name2\n", f.read())


class TestOnGuildRemove(AsyncTestCase):
    LOG_PATH = "guilds.log"

    def setUp(self):
        super().setUp()
        if path.exists(self.LOG_PATH):
            os.remove(self.LOG_PATH)

    def tearDown(self):
        super().tearDown()
        if path.exists(self.LOG_PATH):
            os.remove(self.LOG_PATH)

    @patch_discord
    def test_no_log(self):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = None
        guild = AsyncMock()
        self._await(bot.on_guild_join(guild))
        self.assertFalse(path.exists(self.LOG_PATH))

    @patch_discord
    def test_log(self):
        bot = Bot("app_name", "version")
        bot.guild_logs_file = self.LOG_PATH
        guild1 = AsyncMock()
        guild1.id = "id1"
        guild1.name = "name1"
        guild2 = AsyncMock()
        guild2.id = "id2"
        guild2.name = "name2"
        d = datetime.now()
        self._await(bot.on_guild_remove(guild1))
        self._await(bot.on_guild_remove(guild2))
        self.assertTrue(path.exists(self.LOG_PATH))
        with open(self.LOG_PATH, encoding="utf-8", mode="r") as f:
            self.assertEqual(f"{d:%Y-%m-%d %H:%M} -id1: name1\n"
                             f"{d:%Y-%m-%d %H:%M} -id2: name2\n", f.read())

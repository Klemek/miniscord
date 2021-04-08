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
            f"```",
            reference=message,
            mention_author=False,
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
            f"```",
            reference=message,
            mention_author=False,
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
            f"```",
            reference=message,
            mention_author=False,
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
            f"```",
            reference=message,
            mention_author=False,
        )

    @patch_discord
    def test_long(self):
        bot = Bot("app_name", "version")
        bot.register_command("test1", None, None, "long desc")
        message = AsyncMock()
        self._await(bot.help(None, message, "help", "test1"))
        message.channel.send.assert_awaited_once_with(
            "long desc", reference=message, mention_author=False
        )

    @patch_discord
    def test_long_regex(self):
        bot = Bot("app_name", "version")
        bot.register_command("test", None, None, "desc1")
        bot.register_command("t.*", None, None, "desc2")
        message = AsyncMock()
        self._await(bot.help(None, message, "help", "test"))
        message.channel.send.assert_awaited_once_with(
            "desc2", reference=message, mention_author=False
        )

    @patch_discord
    def test_not_found(self):
        bot = Bot("app_name", "version")
        message = AsyncMock()
        self._await(bot.help(None, message, "help", "notfound"))
        message.channel.send.assert_awaited_once_with(
            f"Command `notfound` not found",
            reference=message,
            mention_author=False,
        )


class TestRegisterEvent(TestCase):
    @skip
    def test_todo(self):
        self.fail("not implemented")


class TestRegisterCommand(TestCase):
    @patch_discord
    def test_add_regex(self):
        bot = Bot("app_name", "version")
        self.assertEqual(2, len(bot._Bot__commands))
        callback = AsyncMock()
        bot.register_command("^t[eo]a?st$", callback, "short", "long")
        self.assertEqual(3, len(bot._Bot__commands))
        cmd = bot._Bot__commands[0]
        self.assertEqual("^t[eo]a?st$", cmd.regex)
        self.assertEqual(callback, cmd.compute)
        self.assertEqual("short", cmd.help_short)
        self.assertEqual("long", cmd.help_long)

    @patch_discord
    def test_add_simple(self):
        bot = Bot("app_name", "version")
        bot.register_command("test", None, None, None)
        cmd = bot._Bot__commands[0]
        self.assertEqual("^test$", cmd.regex)


class TestOnMessage(AsyncTestCase):
    @patch_discord
    def test_no_mention_minial(self):
        bot = Bot("app_name", "version")
        message = AsyncMock()
        message.content = "hello there"
        self._await(bot.on_message(message))

    @patch_discord
    def test_no_mention(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "hello there"
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_mention_no_command(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> testt arg0 arg1"
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_awaited_once_with(
            bot.client, message, "testt", "arg0", "arg1"
        )

    @patch_discord
    def test_mention_no_command_empty(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345>"
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_awaited_once_with(bot.client, message)

    @patch_discord
    def test_mention_command_simple(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> test arg0 arg1"
        self._await(bot.on_message(message))
        simple_callback.assert_awaited_once_with(
            bot.client, message, "test", "arg0", "arg1"
        )
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_mention_command_regex(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.client.user.id = "12345"
        regex_callback = AsyncMock()
        bot.register_command("^t[eo]a?st$", regex_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> toast hey"
        self._await(bot.on_message(message))
        regex_callback.assert_awaited_once_with(bot.client, message, "toast", "hey")
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_mention_alias_no_command(self):
        bot = Bot("app_name", "version", alias="|")
        bot.enforce_write_permission = False
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "|toast hey"
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_awaited_once_with(bot.client, message, "toast", "hey")

    @patch_discord
    def test_mention_alias_command_simple(self):
        bot = Bot("app_name", "version", alias="|")
        bot.enforce_write_permission = False
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "|test hey"
        self._await(bot.on_message(message))
        simple_callback.assert_awaited_once_with(bot.client, message, "test", "hey")
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_mention_no_permission(self):
        bot = Bot("app_name", "version")
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> test hey"
        message.channel.__repr__ = lambda *a: "test_channel"
        message.guild.__repr__ = lambda *a: "test_guild"
        permissions = AsyncMock()
        permissions.send_messages = False
        message.channel.permissions_for = lambda u: permissions
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()
        message.author.create_dm.assert_awaited_once()
        message.author.dm_channel.send.assert_awaited_once_with(
            f"Hi, this bot doesn't have the permission to send a message to"
            f" #test_channel in server 'test_guild'"
        )

    @patch_discord
    def test_mention_self(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> test arg0 arg1"
        message.author = bot.client.user
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_not_awaited()
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_mention_direct(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> test arg0 arg1"
        message.channel.type == discord.ChannelType.private
        self._await(bot.on_message(message))
        simple_callback.assert_awaited_once_with(
            bot.client, message, "test", "arg0", "arg1"
        )
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_any_mention(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.any_mention = True
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "test <@12345> arg0 arg1"
        message.channel.type == discord.ChannelType.private
        message.mentions = [bot.client.user]
        self._await(bot.on_message(message))
        simple_callback.assert_awaited_once_with(
            bot.client, message, "test", "arg0", "arg1"
        )
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_any_mention_off(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.any_mention = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "test <@12345> arg0 arg1"
        message.channel.type == discord.ChannelType.private
        message.mentions = [bot.client.user]
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_remove_mentions(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.remove_mentions = True
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> test <@12345> arg1"
        self._await(bot.on_message(message))
        simple_callback.assert_awaited_once_with(bot.client, message, "test", "arg1")
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_remove_mentions_off(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.remove_mentions = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> test <@12345> arg1"
        self._await(bot.on_message(message))
        simple_callback.assert_awaited_once_with(
            bot.client, message, "test", "<@12345>", "arg1"
        )
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_lower_command_names(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.lower_command_names = True
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> Test arg0 arg1"
        self._await(bot.on_message(message))
        simple_callback.assert_awaited_once_with(
            bot.client, message, "test", "arg0", "arg1"
        )
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_not_awaited()

    @patch_discord
    def test_lower_command_names_off(self):
        bot = Bot("app_name", "version")
        bot.enforce_write_permission = False
        bot.lower_command_names = False
        bot.client.user.id = "12345"
        simple_callback = AsyncMock()
        bot.register_command("test", simple_callback, "short", "long")
        watcher_callback = AsyncMock()
        bot.register_watcher(watcher_callback)
        fallback_callback = AsyncMock()
        bot.register_fallback(fallback_callback)
        message = AsyncMock()
        message.content = "<@12345> Test arg0 arg1"
        self._await(bot.on_message(message))
        simple_callback.assert_not_awaited()
        watcher_callback.assert_awaited_once_with(bot.client, message)
        fallback_callback.assert_awaited_once_with(
            bot.client, message, "Test", "arg0", "arg1"
        )

    @skip
    def test_fire_registered_event(self):
        self.fail("not implemented")

    @skip
    def test_fire_registered_event_cancel(self):
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
            activity="activity", status=discord.Status.online
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
            self.assertEqual(
                f"{d:%Y-%m-%d %H:%M} +id1: name1\n" f"{d:%Y-%m-%d %H:%M} +id2: name2\n",
                f.read(),
            )

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

    @skip
    def test_fire_registered_event(self):
        self.fail("not implemented")

    @skip
    def test_fire_registered_event_cancel(self):
        self.fail("not implemented")


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
            self.assertEqual(
                f"{d:%Y-%m-%d %H:%M} +id1: name1\n" f"{d:%Y-%m-%d %H:%M} +id2: name2\n",
                f.read(),
            )

    @skip
    def test_fire_registered_event(self):
        self.fail("not implemented")

    @skip
    def test_fire_registered_event_cancel(self):
        self.fail("not implemented")


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
            self.assertEqual(
                f"{d:%Y-%m-%d %H:%M} -id1: name1\n" f"{d:%Y-%m-%d %H:%M} -id2: name2\n",
                f.read(),
            )

    @skip
    def test_fire_registered_event(self):
        self.fail("not implemented")

    @skip
    def test_fire_registered_event_cancel(self):
        self.fail("not implemented")

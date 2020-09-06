from typing import Callable, Coroutine, Tuple, Any
import time
import logging
import traceback
import discord
import re
import asyncio
import random
import os
from datetime import datetime
from dotenv import load_dotenv

from ._utils import sanitize_input, parse_arguments

CommandFunction = Callable[[discord.Client, discord.Message, Tuple[str]], Coroutine[Any, Any, None]]


def debug(message: discord.Message, txt: str):
    logging.info(f"{message.guild} > #{message.channel}: {txt}")


class Command(object):
    def __init__(self, regex: str, compute: CommandFunction, help_short: str, help_long: str):
        self.regex = regex
        self.compute = compute
        self.help_short = help_short
        self.help_long = help_long


class Bot(object):
    def __init__(self, app_name: str, version: str, *, alias: str = None):
        # constants
        self.token_env_var = "DISCORD_TOKEN"
        self.remove_mentions = True  # remove mentions from arguments
        self.alias = alias  # can call bot with {alias}{command_name}
        self.any_mention = False  # bot mention can be anywhere
        self.log_calls = False
        self.guild_logs_file = "guilds.log"
        self.enforce_write_permission = True
        self.lower_command_names = True
        self.game_change_delay = 10
        self.error_restart_delay = 2
        # config vars
        self.app_name = app_name
        self.version = version
        # future vars
        self.__token = None
        self.__t0 = None
        self.__last_error = None
        # init
        self.__commands = []
        self.games = [f"v{version}",
                      lambda:f"{len(self.client.guilds)} guilds"]
        if self.alias is not None:
            self.games += [f"{self.alias}help"]
        self.client = discord.Client()
        self.__register_events()
        self.__register_commands()

    def __register_events(self):
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)
        self.on_guild_join = self.client.event(self.on_guild_join)
        self.on_guild_remove = self.client.event(self.on_guild_remove)

    def __register_commands(self):
        # register default commands
        tmp_alias = '' if self.alias is None else self.alias
        self.register_command(
            "(help|h)", self.help, "help: show this help",
            f"```\n"
            f"* {tmp_alias}help\n"
            f"\tShows the list of commands.\n"
            f"* {tmp_alias}help [command]\n"
            f"\tShows help about a specific command.\n"
            f"```"
        )
        self.register_command(
            "(info|about)", self.info, "info: show description",
            f"```\n"
            f"* {tmp_alias}info:\n"
            f"\tShows this bot's status.\n"
            f"```"
        )

    def __generate_game(self) -> str:
        game = random.choice(self.games)
        if callable(game):
            return game()
        else:
            return game

    async def info(self, _client: discord.client, message: discord.Message, *args: str):
        await message.channel.send(
            f"```\n"
            f"{self.app_name} v{self.version}\n"
            f"* Started at {self.__t0:%Y-%m-%d %H:%M}\n"
            f"* Connected to {len(self.client.guilds)} guilds\n"
            f"```"
        )

    async def help(self, _client: discord.client, message: discord.Message, *args: str):
        if len(args) <= 1:
            tmp_alias = '' if self.alias is None else self.alias
            await message.channel.send(
                f"```\n"
                f"List of available commands:\n" +
                "".join([f"* {tmp_alias}{command.help_short}\n" for command in self.__commands]) +
                f"```"
            )
        else:
            for command in self.__commands:
                if re.match(command.regex, args[1].lower() if self.lower_command_names else args[1]):
                    await message.channel.send(command.help_long)
                    return
            await message.channel.send(f"Command `{sanitize_input(args[1])}` not found")

    async def on_ready(self):
        # Change status
        logging.info(f"{self.client.user} (v{self.version}) has connected to {len(self.client.guilds)} Discord guilds")
        if self.guild_logs_file is not None and not os.path.exists(self.guild_logs_file):
            for guild in self.client.guilds:
                await self.on_guild_join(guild)
        while True:
            await self.client.change_presence(
                activity=discord.Game(self.__generate_game()),
                status=discord.Status.online
            )
            await asyncio.sleep(self.game_change_delay)

    async def on_message(self, message: discord.Message):
        if message.author == self.client.user:
            return  # Ignore self messages

        is_direct = message.channel.type == discord.ChannelType.private

        is_mention = self.any_mention and self.client.user in message.mentions \
            or bool(re.match(f"^<@!?{self.client.user.id}>", message.content))

        if self.remove_mentions:
            message.content = re.sub(r"<@!?[^>]+>", "", message.content)
        elif is_mention:
            message.content = re.sub(f"^<@!?{self.client.user.id}>", "", message.content)

        command_args = parse_arguments(message.content)

        if len(command_args) == 0:
            return  # Empty message

        is_alias = self.alias is not None and command_args[0].startswith(self.alias)
        if is_alias:  # remove alias from first arg
            command_args[0] = command_args[0][len(self.alias):]

        if not is_direct and not is_mention and not is_alias:
            return  # Not for the bot

        for command in self.__commands:
            if re.match(command.regex, command_args[0].lower() if self.lower_command_names else command_args[0]):
                if self.log_calls:
                    debug(message, str(command_args))

                if not is_direct and self.enforce_write_permission:
                    # Check if bot can respond on current channel or DM user
                    permissions = message.channel.permissions_for(message.guild.me)
                    if not permissions.send_messages:
                        await message.author.create_dm()
                        await message.author.dm_channel.send(
                            f"Hi, this bot doesn\'t have the permission to send a message to"
                            f" #{message.channel} in server '{message.guild}'"
                        )
                        return
                await command.compute(self.client, message, *command_args)
                break

    async def on_guild_join(self, guild: discord.guild):
        if self.guild_logs_file is not None:
            with open(self.guild_logs_file, encoding="utf-8", mode="a") as f:
                f.write(f"{datetime.now():%Y-%m-%d %H:%M} +{guild.id}: {guild.name}\n")

    async def on_guild_remove(self, guild: discord.guild):
        if self.guild_logs_file is not None:
            with open(self.guild_logs_file, encoding="utf-8", mode="a") as f:
                f.write(f"{datetime.now():%Y-%m-%d %H:%M} -{guild.id}: {guild.name}\n")
        pass

    def register_command(self, regex: str, compute: CommandFunction, help_short: str, help_long: str):
        if not regex.startswith("^"):
            regex = "^" + regex
        if not regex.endswith("$"):
            regex = regex + "$"
        self.__commands.insert(0, Command(regex, compute, help_short, help_long))

    def start(self):
        logging.info(f"Current PID: {os.getpid()}")
        env_file_found = load_dotenv()
        self.__token = os.getenv(self.token_env_var)
        if self.__token is None:
            if env_file_found:
                raise EnvironmentError(f"No token was loaded, please verify your .env file has '{self.token_env_var}'")
            else:
                raise EnvironmentError(f"No environment variable '{self.token_env_var}' found")
        self.__t0 = datetime.now()
        # Launch client and rerun on errors
        while True:
            try:
                self.client.run(self.__token)
                break  # clean kill
            except Exception as e:
                t = datetime.now()
                logging.error(f"Exception raised : {repr(e)}")
                if repr(e) != self.__last_error:
                    self.__last_error = repr(e)
                    filename = f"error_{t:%Y-%m-%d_%H-%M-%S}.txt"
                    with open(filename, 'w') as f:
                        f.write(
                            f"{self.app_name} v{self.version} started at {self.__t0:%Y-%m-%d %H:%M}\r\n"
                            f"Exception raised at {t:%Y-%m-%d %H:%M}\r\n"
                            f"\r\n"
                            f"{traceback.format_exc()}"
                        )
                time.sleep(self.error_restart_delay)

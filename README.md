[![Scc Count Badge](https://sloc.xyz/github/klemek/miniscord?category=code)](https://github.com/boyter/scc/#badges-beta)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Klemek/miniscord.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Klemek/miniscord/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Klemek/miniscord.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Klemek/miniscord/context:python)
[![Coverage Status](https://coveralls.io/repos/github/Klemek/miniscord/badge.svg?branch=master)](https://coveralls.io/github/Klemek/miniscord?branch=master)

# Miniscord
*A minimalist discord bot API*

```python
from miniscord import Bot
import discord


async def hello(client: discord.client, message: discord.Message, *args: str):
    await message.channel.send("Hello!")


bot = Bot(  
    "test-app",     # name
    "0.1-alpha",    # version
    alias="|"       # respond to '|command' messages
)  
bot.register_command(
    "hello",                    # command text (regex) 
    hello,                      # command function
    "hello: says 'Hello!'",     # short help
    f"```\n"                    # long help
    f"* |help\n"
    f"\tSays 'Hello!'.\n"
    f"```"
)
bot.start()
# this bot respond to "|help", "|info" and "|hello"
```

![](./sample.jpg)

> **⚠ Disclaimer:** I intend to use this project personally, I'm open to ideas but I don't care if it doesn't work for you. Same for the name, feel free to use it, I'm not registering it on PyPI

## Features

*TODO*

## Installation

**1. Install package**

```
pip install git+git://github.com/Klemek/miniscord.git
```

**2. Make a .env file as following**

```
#.env
DISCORD_TOKEN=<bot token from discordapp.com/developers>
```

## Documentation

### Bot init

```python
bot = Bot(  
    "test-app",     # name
    "0.1-alpha",    # version
    alias="|"       # respond to '|command' messages
)  
```

### Bot configuration properties

* `token_env_var` (default: `"DISCORD_TOKEN"`)
  * Which var to read in the `.env` file.
* `remove_mentions` (default: `True`)
  * Remove any mention in the message / arguments.
* `any_mention` (default: `False`)
  * If the bot respond to a mention in the middle of messages.
* `log_calls` (default: `False`)
  * Log any calls to the Python logging.
* `guild_logs_file` (default: `"guilds.log"`)
  * Log guilds join/leave on a file.
* `enforce_write_permission` (default: `True`)
  * If the bot can't respond on a channel it was called, it sends a DM to the caller.
* `lower_command_names` (default: `True`)
  * Use lowercase on command names (if false, commands are case-sensitive).
* `game_change_delay` (default: `10`)
  * Change the game status every n seconds.
* `error_restart_delay` (default: `2`)
  * On crash, restart after n seconds.

### Registering commands

TODO

### Game status

TODO

### Exposed utility functions

TODO

## Versions

* v0.0.1 (WIP) : initial version

## TODO

* Finish README.md
* Write more tests
* Add comments to code
* Separate branches
* Working CI
* Fix bugs

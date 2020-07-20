import logging
from bot import Bot

logging.basicConfig(format="[%(asctime)s][%(levelname)s][%(module)s] %(message)s", level=logging.INFO)

bot = Bot("test-app", "0.1-alpha", alias="|")
bot.log_calls = True
bot.start()

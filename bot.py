import asyncio
import motor.motor_asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from handlers import payments
from handlers import user_messages, user_commands, questionaire
from config_reader import config


client = motor.motor_asyncio.AsyncIOMotorClient(config.mongodb_token.get_secret_value())
db = client.laborant
default_properties = DefaultBotProperties(parse_mode="HTML")

async def main():
    bot = Bot(config.bot_token.get_secret_value(), default=default_properties)
    dp = Dispatcher()

    dp.include_routers(
        user_commands.router,
        questionaire.router,
        user_messages.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

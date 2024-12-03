'''import os
from aiogram import Bot, Router, types
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from dotenv import load_dotenv

router = Router()

# Загружаем токен платежного провайдера из .env
load_dotenv()
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")

# Цены на услуги
PRICE = LabeledPrice(label="Расшифровка анализов", amount=50000)  # Цена указана в копейках (50000 = 500 руб)

# Обработчик команды для начала оплаты
@router.message(Command("start_payment"))
async def start_payment(message: types.Message, bot: Bot):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Расшифровка анализов",
        description="Услуга расшифровки медицинских анализов",
        payload="decode_analysis_payload",  # Уникальный идентификатор транзакции
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=[PRICE],
        start_parameter="decode_analysis",
        need_name=True,
        need_phone_number=False,
        need_email=True,
        need_shipping_address=False,
        is_flexible=False
    )

# Обработчик для подтверждения платежа
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обработчик успешной оплаты
@router.message(types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    successful_payment = message.successful_payment
    await message.answer(f"Спасибо за оплату {successful_payment.total_amount / 100} {successful_payment.currency}! Начинаем расшифровку анализов.")
    # Здесь можно вызвать функцию расшифровки анализов и продолжить взаимодействие с пользователем
'''

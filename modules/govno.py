from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda message: message.chat.type == "private" and message.business_connection_id is not None and message.text.lower().startswith("привет"))
async def greet_user(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Чем могу помочь в личном чате бизнес-аккаунта?")

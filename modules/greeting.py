from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Text

router = Router()

@router.message(Text(startswith="привет", ignore_case=True))
async def greet_user(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Как дела?")

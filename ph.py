import asyncio
import os
import importlib
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

# Инициализация роутера и диспетчера
router = Router()
dp = Dispatcher()
load_dotenv()

# Словарь для хранения активных модулей
active_modules = {}

# Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я модульный бот для Telegram Business. Используй команды:\n"
        "/load <имя_модуля> — загрузить модуль\n"
        "/unload <имя_модуля> — выгрузить модуль\n"
        "/list — список загруженных модулей"
    )

# Команда /list
@router.message(Command("list"))
async def cmd_list(message: Message):
    if active_modules:
        modules = ", ".join(active_modules.keys())
        await message.answer(f"Активные модули: {modules}")
    else:
        await message.answer("Нет активных модулей.")

# Функция для динамической загрузки модуля
def load_module_dynamic(module_name):
    try:
        module = importlib.import_module(f"modules.{module_name}")
        module_router = module.router
        dp.include_router(module_router)
        active_modules[module_name] = module_router
        return True
    except ImportError as e:
        print(f"Ошибка загрузки модуля {module_name}: {e}")
        return False

# Функция для выгрузки модуля
def unload_module_dynamic(module_name):
    if module_name in active_modules:
        dp.routers.remove(active_modules[module_name])
        del active_modules[module_name]
        if f"modules.{module_name}" in importlib.import_module.__dict__:
            del importlib.import_module.__dict__[f"modules.{module_name}"]
        return True
    return False

# Команда /load
@router.message(Command("load"))
async def load_module(message: Message):
    module_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not module_name:
        await message.answer("Укажи имя модуля: /load <имя_модуля>")
        return
    if module_name in active_modules:
        await message.answer(f"Модуль {module_name} уже загружен!")
        return
    if load_module_dynamic(module_name):
        await message.answer(f"Модуль {module_name} успешно загружен!")
    else:
        await message.answer(f"Ошибка: модуль {module_name} не найден или содержит ошибки.")

# Команда /unload
@router.message(Command("unload"))
async def unload_module(message: Message):
    module_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not module_name:
        await message.answer("Укажи имя модуля: /unload <имя_модуля>")
        return
    if unload_module_dynamic(module_name):
        await message.answer(f"Модуль {module_name} выгружен!")
    else:
        await message.answer(f"Модуль {module_name} не найден или не загружен.")

# Обработка сообщений из бизнес-чата
@router.message(lambda message: message.chat.type == "private" and message.business_connection_id is not None)
async def handle_business_message(message: Message):
    await message.answer("Сообщение получено в бизнес-чате! Модули обрабатывают запрос.")

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

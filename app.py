import os.path
import json
import asyncio
from dotenv import load_dotenv
from user_kb import kb_user
from cryptography.fernet import Fernet
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

# Load environment variables from .env
load_dotenv()

# Message visibility time
VISIB_TIME = 40

# Create bot and dispatcher
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


# Creating state classes
class AddService(StatesGroup):
    waiting_for_service = State()
    waiting_for_login_password = State()

class GetService(StatesGroup):
    waiting_for_service = State()

class DelService(StatesGroup):
    waiting_for_service = State()


# Class for working with user data
class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.data = {}
        self.folder_path = "users"
        self.file_path = f"{self.folder_path}/{self.user_id}.json"

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as f:
                encrypted_data = f.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                self.data = json.loads(decrypted_data)

    def save_data(self):
        with open(self.file_path, "wb") as f:
            encrypted_data = fernet.encrypt(json.dumps(self.data).encode())
            f.write(encrypted_data)

    def set_value(self, service_name, login, password):
        login_encrypted = fernet.encrypt(login.encode()).decode()
        password_encrypted = fernet.encrypt(password.encode()).decode()
        self.data[service_name] = {"login": login_encrypted, "password": password_encrypted}
        self.save_data()

    def get_value(self, service_name):
        data = self.data.get(service_name, None)
        if data:
            login = fernet.decrypt(data['login'].encode()).decode()
            password = fernet.decrypt(data['password'].encode()).decode()
            return {"login": login, "password": password}
        else:
            return None

    def del_value(self, service_name):
        if service_name in self.data:
            del self.data[service_name]
            self.save_data()


# Generate an encryption key and save it to a file
if not os.path.exists("key.key"):
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
else:
    with open("key.key", "rb") as key_file:
        key = key_file.read()

# Create fernet object to encrypt and decrypt data
fernet = Fernet(key)


# Command /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    await message.reply("👋 Привет! Я бот-менеджер паролей. Я помогу тебе хранить свои пароли в безопасности.\n\n🔐Чтобы добавить новый сервис, отправь мне команду /set, затем введи название сервиса, логин и пароль через символ ':'.\n\n🔍Чтобы получить логин и пароль для сервиса, отправь мне команду /get с указанием названия сервиса.\n\n🗑️Чтобы удалить данные для сервиса, отправь мне команду /del с указанием названия сервиса.", reply_markup=kb_user)


# Command /set
@dp.message_handler(commands=['set'])
async def set_command(message: types.Message):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    sent_message = await message.reply("Введите название сервиса:")
    await AddService.waiting_for_service.set()

      # wait
    await asyncio.sleep(VISIB_TIME)

    # delte
    if sent_message.from_user.id == bot.id:
        await sent_message.delete()

@dp.message_handler(state=AddService.waiting_for_service)
async def process_service_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    service_name = message.text
    sent_message = await message.reply(f"Введите логин и пароль для сервиса {service_name} в формате 'логин:пароль':")
    await state.update_data(service_name=service_name)
    await AddService.waiting_for_login_password.set()
     # wait
    await asyncio.sleep(VISIB_TIME)

    # Delete the message
    if sent_message.from_user.id == bot.id:
        await sent_message.delete()

@dp.message_handler(state=AddService.waiting_for_login_password)
async def process_login_password(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    login_password = message.text
    service_name = (await state.get_data())['service_name']

    if login_password.count(':') != 1:
        await message.reply("❌ Ошибка: введите логин и пароль через один символ ':'.")
        return

    login, password = login_password.split(':')
    user_data.set_value(service_name, login, password)
    sent_message = await message.reply(f"✅ Логин и пароль для сервиса {service_name} успешно сохранены!")

    await state.finish()

    # wait
    await asyncio.sleep(VISIB_TIME)

    # Delete the message
    if sent_message.from_user.id == bot.id:
        await sent_message.delete()


# Command /get
@dp.message_handler(commands=['get'])
async def get_command(message: types.Message):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    sent_message = await message.reply("Введите название сервиса:")
    await GetService.waiting_for_service.set()

      # wait
    await asyncio.sleep(VISIB_TIME)

    # delete the message
    if sent_message.from_user.id == bot.id:
        await sent_message.delete()

@dp.message_handler(state=GetService.waiting_for_service)
async def process_service_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    service_name = message.text
    login_password = user_data.get_value(service_name)
    if login_password:
        login = login_password["login"]
        password = login_password["password"]
        sent_message = await  message.reply(f"🔑 Логин для сервиса {service_name}: {login}\n🔒 Пароль для сервиса {service_name}: {password}")
    else:
        sent_message = await message.reply(f"❌ Данные для сервиса {service_name} не найдены.")

    await state.finish()

    # wait
    await asyncio.sleep(VISIB_TIME)

    # Delete the message
    if sent_message.from_user.id == bot.id:
        await sent_message.delete()


# Command /del
@dp.message_handler(commands=['del'])
async def del_command(message: types.Message):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    sent_message = await message.reply("Введите название сервиса:")
    await DelService.waiting_for_service.set()

    # wait
    await asyncio.sleep(VISIB_TIME)

    # Delete the message
    if sent_message.from_user.id == bot.id:
        await sent_message.delete()

@dp.message_handler(state=DelService.waiting_for_service)
async def process_service_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = UserData(user_id)
    service_name = message.text
    if not user_data.get_value(service_name):
        sent_message = await message.reply(f"❌ Сервис {service_name} не найден.")
    else:
        user_data.del_value(service_name)
        sent_message = await message.reply(f"✅ Данные для сервиса {service_name} удалены.")

    await state.finish()

    # wait
    await asyncio.sleep(VISIB_TIME)

    # Delete the message
    if message.from_user.id == bot.id:
        await sent_message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

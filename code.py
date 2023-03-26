import os

import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

bot_token = "6172822773:AAGbFKhMEQMPo5GyU3cH8xAVrYdHU_MYiqk"

strorage = MemoryStorage()
bot = Bot(bot_token)
dp = Dispatcher(bot,
                storage=strorage)

class ClientStatesGroup(StatesGroup):
    go_cd = State()
    dir_new = State()
    delete = State()
    dir = State()
    dir_rename_get = State()
    dir_rename_set = State()

dir_name = None
dir_new_name = None

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await bot.send_message(message.from_user.id, "Привет! Я могу управлять твоим компьютером ")


@dp.message_handler(commands=['get_cd'])
async def get_cd(message: types.Message, ):
    await bot.send_message(message.from_user.id, text=os.getcwd())

@dp.message_handler(commands=['dir_new'])
async def new_direct(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Введите название директории")
    await ClientStatesGroup.dir_new.set()

@dp.message_handler(state=ClientStatesGroup.dir_new)
async def create_direct(message: types.Message, state: FSMContext):
    name_direct = message.text
    if not os.path.isdir(name_direct):
        os.mkdir(name_direct)
        os.chdir(name_direct)
        new_direct_path = os.getcwd()
        await bot.send_message(message.from_user.id, f'Создана новая директория: {name_direct}\nПуть: {new_direct_path} ')
        os.chdir('..')
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, f'Директория с название: {name_direct} уже  существует')
        await state.finish()

@dp.message_handler(commands=['dir_go'])
async def go_cd(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Введите название директории куда вы хотите переместиться')
    await ClientStatesGroup.go_cd.set()

@dp.message_handler(state=ClientStatesGroup.go_cd)
async def go_direct(message: types.Message, state: FSMContext):
    name_direct = message.text
    os.chdir(name_direct)
    direct_path = os.getcwd()
    await bot.send_message(message.from_user.id, f'Вы переместились в {direct_path}')
    await state.finish()

@dp.message_handler(commands=['dir_delete'])
async def cmd_delete_direct(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Введите название директории, которую хотите удалить')
    await ClientStatesGroup.delete.set()

@dp.message_handler(state=ClientStatesGroup.delete)
async def delete_direct(message: types.Message, state: FSMContext):
    name_directory = message.text
    if os.path.isdir(name_directory):
        os.chdir(name_directory)
        delete_path = os.getcwd()
        os.chdir('..')
        os.rmdir(name_directory)
        await bot.send_message(message.from_user.id, f'Путь {delete_path} был удален')
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, f'Директории с названием: {name_directory} не сущетвует!')
        await state.finish()


@dp.message_handler(commands=['dir'])
async def cmd_isdir(message: types.Message, state: FSMContext):
    path_direct = os.getcwd()
    for dirpath, dirnames, filenames in os.walk("."):
        for dirname in dirnames:
            dir = f'Директория: {os.path.join(dirpath,dirname)}'
            for filename in filenames:
                dir_file = f'Файл: {os.path.join(dirpath, filename)}'
                await bot.send_message(message.from_user.id, f'Директория {path_direct}\n{dir}\n{dir_file}')

@dp.message_handler(commands=['dir_set'])
async def cmd_dir_set(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Введите название директории, для дальнейших действий')
    await ClientStatesGroup.dir_rename_get.set()

@dp.message_handler(state=ClientStatesGroup.dir_rename_get)
async def dir_rename_get(message: types.Message, state: FSMContext):
    global dir_name
    dir_name = message.text
    if os.path.isdir(dir_name):
        await state.finish()
        await bot.send_message(message.from_user.id, f'Выбрана директория: {dir_name}')
    else:
        await bot.send_message(message.from_user.id, f'Директории с названием: {dir_name} не существует!')
        await state.finish()
        dir_name = None

@dp.message_handler(commands=['dir_rename'])
async def cmd_dir_rename(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, f'Выберите новое название для директории {dir_name}')
    await ClientStatesGroup.dir_rename_set.set()

@dp.message_handler(state=ClientStatesGroup.dir_rename_set)
async def dir_rename_set(message: types.Message, state: FSMContext):
    global dir_name
    global dir_new_name
    dir_new_name = message.text
    if not os.path.isdir(dir_new_name):
        os.rename(dir_name, dir_new_name)
        await state.finish()
        await bot.send_message(message.from_user.id, f'Старое название: {dir_name}\nНовое название: {dir_new_name}')
        dir_name = None
        dir_new_name = None
    else:
        await bot.send_message(message.from_user.id, f'Директория с названием: {dir_new_name} уже существует!')
        await state.finish()
        dir_name = None
        dir_new_name = None

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
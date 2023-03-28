import os
import pathlib
import webbrowser
import  shutil

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import config

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
    dir_move = State()
    file_new = State()
    file_delete = State()
    file_rename_set = State()
    file_rename_get = State()
    file_write = State()
    file_move = State()
    file_open = State()
    link_open_get = State()
    link_open_set = State()
    photo_new_set_name = State()
    photo_new_set_photo = State()

dir_name = None
dir_new_name = None
file_name = None
file_new_name = None
link = None
photo_name = None

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await bot.send_message(message.from_user.id, "Привет! Я могу управлять твоим компьютером ",
                           reply_markup=config.kb)


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
    if os.path.isdir(name_direct):
        os.chdir(name_direct)
        direct_path = os.getcwd()
        await bot.send_message(message.from_user.id, f'Вы переместились в {direct_path}')
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, f'Директория {name_direct} не существует! ')

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
    global dir_name
    if dir_name != None:
        await bot.send_message(message.from_user.id, f'Выберите новое название для директории {dir_name}')
        await ClientStatesGroup.dir_rename_set.set()
    else:
        await bot.send_message(message.from_user.id, 'Сначала выберите нужную директорию командой /dir_set')

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

@dp.message_handler(commands=['dir_move'])
async def cmd_dir_move(message: types.Message, state: FSMContext):
    global dir_name
    if dir_name != None:
        await bot.send_message(message.from_user.id, f'Выберите куда вы хотите переместить директорию {dir_name}')
        await ClientStatesGroup.dir_move.set()
    else:
        await bot.send_message(message.from_user.id, 'Сначала выберите нужную директорию командой /dir_set')
        
@dp.message_handler(state=ClientStatesGroup.dir_move)
async def dir_move(message: types.Message, state: FSMContext):
    global dir_name
    path_move = message.text
    shutil.move(dir_name, path_move)
    await bot.send_message(message.from_user.id, f'Директория {dir_name} была перемещена в:\n{path_move}')
    dir_name = None
    await state.finish()


@dp.message_handler(commands=['file_new'])
async def cmd_file_new(message: types.Message, state: FSMContext):
    dir_path = os.getcwd()
    await bot.send_message(message.from_user.id, f'Напишите название файла\nФайл будет создан в: {dir_path}')
    await ClientStatesGroup.file_new.set()

@dp.message_handler(state=ClientStatesGroup.file_new)
async def file_new(message: types.Message, state: FSMContext):
    file_name = message.text
    path = pathlib.Path(file_name)
    path_file = os.getcwd()
    if path.is_file() == False:
        file = open(file_name, 'w')
        file.close()
        await state.finish()
        await bot.send_message(message.from_user.id, f'Файл {file_name} был создан\nПуть: {path_file}')
    else:
        await state.finish()
        await bot.send_message(message.from_user.id, f'Файл с названием {file_name} уже существует!')


@dp.message_handler(commands=['file_delete'])
async def cmd_file_delete(message: types.Message, state: FSMContext):
    path_file = os.getcwd()
    await bot.send_message(message.from_user.id, f'Выберите название файла, который находится в {path_file}')
    await ClientStatesGroup.file_delete.set()

@dp.message_handler(state=ClientStatesGroup.file_delete)
async def file_delete(message: types.Message, state: FSMContext):
    file_name = message.text
    path = pathlib.Path(file_name)
    if path.is_file() == True:
        os.remove(file_name)
        await state.finish()
        await bot.send_message(message.from_user.id, f'Файл {file_name} был удален')
    else:
        await state.finish()
        await bot.send_message(message.from_user.id, f'Файл {file_name} не существует!')


@dp.message_handler(commands=['file_set'])
async def cmd_file_rename(message: types.Message, state: FSMContext):
    path_file = os.getcwd()
    await bot.send_message(message.from_user.id, f'Выберите название файла, который находится в {path_file}')
    await ClientStatesGroup.file_rename_set.set()

@dp.message_handler(state=ClientStatesGroup.file_rename_set)
async def file_rename_set(message: types.Message, state: FSMContext):
    global file_name
    file_name = message.text
    path = pathlib.Path(file_name)
    if path.is_file() == True:
        await state.finish()
        await bot.send_message(message.from_user.id, f'Выбран файл {file_name}')
    else:
        await state.finish()
        await bot.send_message(message.from_user.id, f'Файл с названием {file_name} не существует!')

@dp.message_handler(commands=['file_rename'])
async def cmd_file_rename(message: types.Message, state: FSMContext):
    global file_name
    if file_name != None:
        await bot.send_message(message.from_user.id, f'Выберите новое название для файла {file_name}')
        await ClientStatesGroup.file_rename_get.set()
    else:
        await bot.send_message(message.from_user.id, 'Сначала выберите нужный файл командой /file_set')
        
@dp.message_handler(state=ClientStatesGroup.file_rename_get)
async def file_rename_get(message: types.Message, state: FSMContext):
    global file_name, file_new_name
    if file_name != None:
        file_new_name = message.text
        os.rename(file_name, file_new_name)
        await state.finish()
        await bot.send_message(message.from_user.id, f'Старое название файла: {file_name}\nНовое название файла: {file_new_name}')
        file_name = None
        file_new_name = None

@dp.message_handler(commands=['file_read'])
async def cmd_file_read(message: types.Message):
    global file_name
    if file_name != None:
        file = open(file_name, 'r', encoding='UTF-8')
        file_read = file.read()
        await bot.send_message(message.from_user.id, f'Содержимое файла:\n{file_read}')
        file.close()
        file_name = None
    else:
        await bot.send_message(message.from_user.id, 'Сначала выберите нужный файл командой /file_set')

@dp.message_handler(commands=['file_write'])
async def cmd_file_write(message: types.Message, state: FSMContext):
    global file_name
    if file_name != None:
        await bot.send_message(message.from_user.id, 'Введите текст')
        await ClientStatesGroup.file_write.set()
    else:
        await bot.send_message(message.from_user.id, 'Сначала выберите нужный файл командой /file_set')
        
@dp.message_handler(state=ClientStatesGroup.file_write)
async def file_write(message: types.Message, state: FSMContext):
    global file_name
    write_text = message.text
    write_file = open(file_name, 'r+', encoding='UTF-8')
    write_file.write(write_text)
    write_file.close()
    file = open(file_name, 'r+', encoding='UTF-8')
    file_read = file.read()
    await state.finish()
    await bot.send_message(message.from_user.id, f'Содержание файла {file_name} было изменено:\n{file_read}')
    file_name = None

@dp.message_handler(commands=['file_move'])
async def cmd_file_move(message: types.Message, state: FSMContext):
    global file_name
    if file_name != None:
        await bot.send_message(message.from_user.id, f'Выберите путь куда переместить файл {file_name}')
        await ClientStatesGroup.file_move.set()
    else:
        await bot.send_message(message.from_user.id, 'Сначала выберите нужный файл командой /file_set')

@dp.message_handler(state=ClientStatesGroup.file_move)
async def file_move(message: types.Message, state: FSMContext):
    global file_name
    new_path_file = message.text
    os.replace(file_name, new_path_file)
    await state.finish()
    await bot.send_message(message.from_user.id, f'Файл {file_name} был перемещен в:\n{new_path_file} ')
    file_name = None

@dp.message_handler(commands=['file_open'])
async def cmd_file_opem(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Выберите какой файл открыть')
    await ClientStatesGroup.file_open.set()


@dp.message_handler(state=ClientStatesGroup.file_open)
async def file_open(message: types.Message, state: FSMContext):
    file_path = message.text
    os.startfile(file_path)
    await state.finish()
    await bot.send_message(message.from_user.id, f'Файл {file_path} открыт')

@dp.message_handler(commands=['link_open'])
async def cmd_link_open(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Отправьте ссылку, которую хотите открыть')
    await ClientStatesGroup.link_open_get.set()

@dp.message_handler(state=ClientStatesGroup.link_open_get)
async def link_open_get(message: types.Message, state: FSMContext):
    link = message.text
    await bot.send_message(message.from_user.id, 'Напишите число как открыть ссылку:\n0.Ссылка откроется в том же окне браузера\n1.Откроется новое окно браузера\n2.Откроется новая вкладка браузера')
    await state.finish()
    await ClientStatesGroup.link_open_set.set()

@dp.message_handler(state=ClientStatesGroup.link_open_set)
async def link_open_set(message: types.Message, state: FSMContext):
    global link
    method = message.text
    if method == '0':
        webbrowser.open(link, new=0)
        await state.finish()
        await bot.send_message(message.from_user.id, f'Ссылка {link} открыто 0 методом')
        link = None
    elif method == '1':
        webbrowser.open(link, new=1)
        await state.finish()
        await bot.send_message(message.from_user.id, f'Ссылка {link} открыто 1 методом')
        link = None
    elif method == '2':
        webbrowser.open(link, new=2)
        await state.finish()
        await bot.send_message(message.from_user.id, f'Ссылка {link} открыто 2 методом')
        link = None
    else:
        await bot.send_message(message.from_user.id, 'Вы выбрали неверный метод открытия ссылки')
        await state.finish()
        link = None

@dp.message_handler(Text(equals='Команды'))
async def cmd_help(message: types.Message):
    await bot.send_message(message.from_user.id, config.cmd_help)


@dp.message_handler(commands=['photo_new'])
async def cmd_photo_new(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Выберите название для фотографии')
    await ClientStatesGroup.photo_new_set_name.set()

@dp.message_handler(state=ClientStatesGroup.photo_new_set_name)
async def photo_new_set_name(message: types.Message, state: FSMContext):
    global photo_name
    photo_name = message.text
    await bot.send_message(message.from_user.id, 'Название фотографии записано.\nТеперь отправьте фотографию')
    await state.finish()
    await ClientStatesGroup.photo_new_set_photo.set()

@dp.message_handler(state=ClientStatesGroup.photo_new_set_photo)
async def photo_new_set_photo(message: types.Message):
    global photo_name
    await message.photo[-1].download(photo_name)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
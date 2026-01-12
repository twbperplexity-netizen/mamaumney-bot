import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp
from states import CreateChildForm
from database import get_user, save_user

# --------- СОЗДАНИЕ ПРОФИЛЯ РЕБЕНКА ---------

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(
        "Настройте профиль ребенка",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton("+ Добавить ребенка", callback_data="add_child")]])
    )

@dp.callback_query_handler(lambda c: c.data == "add_child")
async def add_child_step_1(callback_query: types.CallbackQuery):
    await CreateChildForm.name.set()
    await callback_query.message.answer(
        "Название в формате: Имя: короткое описание (возраст, пол).\nПример: Мира: девочка, 3 года 2 месяца."
    )

@dp.message_handler(state=CreateChildForm.name)
async def process_child_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await CreateChildForm.next()
    await message.answer(
        "Имя сохранено!"
    )
    return

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

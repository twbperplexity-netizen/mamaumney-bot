import asyncio
import json
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TELEGRAM_TOKEN = "853663680:AAF9r1g-s-ykbFE36h3H9-RaxAv%lyLXIPM"
AUTH_KEY = "MD55v++5ZGtYzEyMy03Mjh1LThNWGEtODA3MGQ2ZDJhNzAxOjFwNJR1MzEyLlY2MjEtNGZjNS1lNDFiLWF1MT0tMDJhGE4zg=="
SCOPE = "GIGACHAT_API_PERS"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

user_profiles = {}
access_token = None

SCENARIOS = {
    "food_menu": {
        "category": "food",
        "title": "Меню и список продуктов",
        "questions": [
            {"key": "for_who", "text": "Для кого делаем меню – только для этого ребенка или для всей семьи?"},
            {"key": "food_profile", "text": "Навчи: аллергии, непереносимости, продукты которых нет дома, что ребенок любит."},
            {"key": "budget", "text": "Бюджет на еду? Пример: '700P в день' или '5000P в неделе'."},
        ],
        "prompt_template": "Ты нутриционист. Профиль ребенка: {child_profile}.\nДля кого меню: {for_who}.\nОбстановность: {food_profile}.\nАпробет",
        "system": "You are a helpful nutritionist assistant."
    },
    "medicine_advice": {
        "category": "medicine",
        "title": "Советы по здоровью и лекарства",
        "questions": [
            {"key": "symptom", "text": "Какой симптом или заболевание?"},
            {"key": "med_profile", "text": "Информация: хронические болезни, принимаемые лекарства, аллергии на лекарства."},
            {"key": "duration", "text": "Как долго длится? Когда началось?"},
        ],
        "prompt_template": "Ты врач. Профиль ребенка: {child_profile}.\nСимптомы: {symptom}.\nИстория: {med_profile}.\nДлительность: {duration}.",
        "system": "You are a medical advisor for children."
    },
    "budget_plan": {
        "category": "budget",
        "title": "Бюджет и финансовое планирование",
        "questions": [
            {"key": "needs", "text": "Какие расходы на ребенка? (еда, учеба, спорт, развлечения)"},
            {"key": "budget_profile", "text": "Семейный доход, уже имеющиеся расходы, приоритеты."},
            {"key": "goals", "text": "Какие цели? Например, откладывать на образование?"},
        ],
        "prompt_template": "Ты финансовый консультант. Профиль ребенка: {child_profile}.\nРасходы: {needs}.\nСемейный бюджет: {budget_profile}.\nЦели: {goals}.",
        "system": "You are a family finance advisor."
    },
    "development_plan": {
        "category": "development",
        "title": "Развитие и образование",
        "questions": [
            {"key": "interests", "text": "Интересы и таланты ребенка?"},
            {"key": "dev_profile", "text": "Возраст, уровень развития, уже пройденные курсы или занятия."},
            {"key": "goals", "text": "Какие навыки развить? Например: чтение, математика, музыка?"},
        ],
        "prompt_template": "Ты педагог-консультант. Профиль ребенка: {child_profile}.\nИнтересы: {interests}.\nТекущий уровень: {dev_profile}.\nЦели: {goals}.",
        "system": "You are a child development advisor."
    }
}

def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🍽️ Меню и продукты")],
            [types.KeyboardButton(text="💊 Здоровье и лекарства")],
            [types.KeyboardButton(text="💰 Бюджет и финансы")],
            [types.KeyboardButton(text="📚 Развитие и образование")],
        ],
        resize_keyboard=True
    )
    return keyboard

@dp.message(CommandStart())
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"children": [], "step": 0, "scenario": None, "data": {}}
    await message.answer(
        "Привет! Это бот помогает мамам. Выбери категорию:",
        reply_markup=main_menu_keyboard()
    )

@dp.message(lambda message: "Меню" in message.text)
async def process_food_menu(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"children": [], "step": 0, "scenario": None, "data": {}}
    user = user_profiles[user_id]
    user["scenario"] = "food_menu"
    user["step"] = 0
    user["data"] = {}
    q = SCENARIOS["food_menu"]["questions"][0]
    await message.answer(q["text"])

@dp.message(lambda message: "Здоровье" in message.text)
async def process_medicine(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"children": [], "step": 0, "scenario": None, "data": {}}
    user = user_profiles[user_id]
    user["scenario"] = "medicine_advice"
    user["step"] = 0
    user["data"] = {}
    q = SCENARIOS["medicine_advice"]["questions"][0]
    await message.answer(q["text"])

@dp.message(lambda message: "Бюджет" in message.text)
async def process_budget(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"children": [], "step": 0, "scenario": None, "data": {}}
    user = user_profiles[user_id]
    user["scenario"] = "budget_plan"
    user["step"] = 0
    user["data"] = {}
    q = SCENARIOS["budget_plan"]["questions"][0]
    await message.answer(q["text"])

@dp.message(lambda message: "Развитие" in message.text)
async def process_development(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"children": [], "step": 0, "scenario": None, "data": {}}
    user = user_profiles[user_id]
    user["scenario"] = "development_plan"
    user["step"] = 0
    user["data"] = {}
    q = SCENARIOS["development_plan"]["questions"][0]
    await message.answer(q["text"])

@dp.message()
async def handle_scenario_response(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"children": [], "step": 0, "scenario": None, "data": {}}
    user = user_profiles[user_id]
    text = message.text
    
    if user.get("scenario") and "scenario" in user and user["scenario"]:
        scenario = SCENARIOS[user["scenario"]]
        if user["step"] < len(scenario["questions"]):
            q = scenario["questions"][user["step"]]
            user["data"][q["key"]] = text
            user["step"] += 1
            
            if user["step"] < len(scenario["questions"]):
                next_q = scenario["questions"][user["step"]]
                await message.answer(next_q["text"])
            else:
                await message.answer("✨ Получен ваш ответ. Ответ выгенерирован. Пожалуйста, подождите...")
                data = user["data"].copy()
                data["child_profile"] = "Ребенок 3-5 лет"
                prompt = scenario["prompt_template"].format(**data)
                answer = "**" + scenario["title"] + ":**\n" + prompt
                await message.answer(answer)
                user["scenario"] = None
                await message.answer("Выбери еще одну категорию:", reply_markup=main_menu_keyboard())
    else:
        await message.answer("Открый категорию используя кнопки:", reply_markup=main_menu_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

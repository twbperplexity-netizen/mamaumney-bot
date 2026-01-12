import asyncio
import json
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TELEGRAM_TOKEN = "8536636860:AAF9rlg-s-ykbfEJ6h3H9-RaxAvHWyLXIPM"
AUTH_KEY = "MDE5YmE5ZGEtYzEyMy03MjhlLThhNGEtODA3MGQ4ZDJhNzAxOjEwNjRlMzEyLWY2MjEtNGZjNS1hNDFiLWFjNTE4MDJhOGE4Zg=="
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
            {
                "key": "for_who",
                "text": (
                    "Для кого делаем меню — только для этого ребёнка или для всей семьи "
                    "(ребёнок + мама/папа)?"
                ),
            },
            {
                "key": "food_profile",
                "text": (
                    "Напиши по пунктам:\n"
                    "1) Аллергии и непереносимости (если нет — напиши «нет аллергий»).\n"
                    "2) Продукты, которых дома не бывает принципиально.\n"
                    "3) Что ребёнок особенно любит."
                ),
            },
            {
                "key": "budget",
                "text": (
                    "Сколько примерно можете тратить на еду: в день или в неделю?\n"
                    "Пример: «700₽ в день» или «5000₽ в неделю»."
                ),
            },
        ],
        "prompt_template": (
            "Ты нутриционист и планировщик питания для мамы из России. "
            "Твоя задача — предложить простое, бюджетное и безопасное питание для ребёнка и семьи.\n\n"
            "Профиль ребёнка: {child_profile}.\n"
            "Для кого меню: {for_who}.\n"
            "Особенности питания семьи: {food_profile}.\n"
            "Бюджет на еду: {budget}.\n\n"
            "Составь результат строго в этом формате:\n"
            "1) Кратко оцени бюджет как минимальный / средний / комфортный.\n"
            "2) Дай список продуктов на неделю по категориям:\n"
            "   - крупы;\n"
            "   - мясо/рыба;\n"
            "   - овощи;\n"
            "   - фрукты;\n"
            "   - молочная группа;\n"
            "   - перекусы ребёнку;\n"
            "   - «мамины радости».\n"
            "3) Примерное меню на 3 дня: завтрак, обед, ужин + один перекус ребёнку на каждый день.\n\n"
            "Используй только привычные продукты из обычного супермаркета. "
            "Пиши по пунктам, без сложных терминов и без рекомендаций по БАДам."
        ),
        "system": (
            "Ты нутриционист и планировщик питания для мамы из России. "
            "Отвечаешь простым, поддерживающим языком, без стыда и морализаторства. "
            "Если данных недостаточно, сначала задаёшь один уточняющий вопрос, "
            "а уже потом даёшь рекомендации."
        ),
    },
    "food_recipes": {
        "category": "food",
        "title": "Быстрые рецепты для мамы",
        "questions": [
            {
                "key": "time",
                "text": "Сколько у тебя обычно есть времени на готовку одного блюда (в минутах)?",
            },
            {
                "key": "servings",
                "text": "На сколько человек ты чаще всего готовишь (ты + ребёнок/семья)?",
            },
            {
                "key": "limits",
                "text": (
                    "Есть ли ограничения по продуктам: аллергии, непереносимость, вегетарианство, «не ем молочку»? "
                    "Если никаких особенностей нет, напиши «нет»."
                ),
            },
        ],
        "prompt_template": (
            "Ты помогаешь уставшей маме подобрать простые и быстрые рецепты.\n\n"
            "Ребёнок: {child_profile}.\n"
            "Время на готовку одного блюда: {time} минут.\n"
            "Количество порций: {servings}.\n"
            "Ограничения и пожелания по продуктам: {limits}.\n\n"
            "Подбери 5 быстрых рецептов. Для каждого рецепта напиши:\n"
            "— название;\n"
            "— список продуктов (не больше 7 позиций, всё доступно в обычном супермаркете);\n"
            "— 3–4 шага приготовления простым языком;\n"
            "— как адаптировать блюдо под ребёнка указанного возраста.\n\n"
            "Не предлагай десерты из чистого сахара, никакого алкоголя и экзотических ингредиентов."
        ),
        "system": (
            "Ты дружелюбный помощник по быстрым рецептам для мамы. "
            "Главный фокус — простые блюда, минимум посуды и шагов, максимум пользы. "
            "Если данных мало, сначала задаёшь уточняющий вопрос, а не придумываешь за пользователя."
        ),
    },
}


def get_gigachat_token_sync():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "3a9b25c1-0c15-4b39-b95b-ba47cc4ec458",
        "Authorization": f"Basic {AUTH_KEY}",
    }
    payload = {"scope": SCOPE}
    resp = requests.post(url, headers=headers, data=payload, verify=False)
    if resp.status_code != 200:
        print("TOKEN ERROR:", resp.status_code, resp.text)
        return None
    data = resp.json()
    token = data.get("access_token")
    print("NEW TOKEN OK:", token[:20] + "...")
    return token


async def ensure_token():
    global access_token
    loop = asyncio.get_running_loop()
    access_token = await loop.run_in_executor(None, get_gigachat_token_sync)


async def call_gigachat(messages: list[dict]) -> str:
    global access_token
    if not access_token:
        await ensure_token()

    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "model": "GigaChat:latest",
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 800,
    }

    loop = asyncio.get_running_loop()

    def _call():
        return requests.post(url, headers=headers, data=json.dumps(payload), verify=False)

    resp = await loop.run_in_executor(None, _call)

    try:
        data = resp.json()
    except Exception:
        return f"❌ Ошибка: {resp.status_code} {resp.text[:200]}"

    if resp.status_code == 401 or ("token" in str(data).lower() and "expired" in str(data).lower()):
        await ensure_token()
        resp = await loop.run_in_executor(None, _call)
        data = resp.json()

    if "choices" not in data:
        return f"❌ Нейросеть вернула ошибку: {data}"

    return data["choices"][0]["message"]["content"].strip()


async def ask_gigachat_single(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return await call_gigachat(messages)


def get_user(uid: int) -> dict:
    prof = user_profiles.setdefault(uid, {})
    prof.setdefault("state", "idle")
    prof.setdefault("mode", "scenario")    # "scenario" | "chat"
    prof.setdefault("category", None)
    prof.setdefault("scenario", None)
    prof.setdefault("step", 0)
    prof.setdefault("data", {})
    prof.setdefault("history", [])
    # несколько детей: dict {имя: описание}, active_child: имя
    prof.setdefault("children", {})
    prof.setdefault("active_child", None)
    # служебное состояние для управления профилями
    prof.setdefault("profile_mode", None)  # None | "create_child" | "delete_child" | "switch_child"
    return prof


def main_menu_keyboard():
    kb = [
        [types.KeyboardButton(text="🍎 Питание и здоровье")],
        [types.KeyboardButton(text="⚕️ Всё о медицине")],
        [types.KeyboardButton(text="💸 Всё о бюджете")],
        [types.KeyboardButton(text="🧸 Развитие и досуг")],
        [types.KeyboardButton(text="👶 Профили детей")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def food_menu_keyboard():
    kb = [
        [types.KeyboardButton(text="📅 Меню и список продуктов")],
        [types.KeyboardButton(text="👩‍🍳 Быстрые рецепты")],
        [types.KeyboardButton(text="⬅️ В главное меню")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def profiles_menu_keyboard(user: dict):
    kb = [
        [types.KeyboardButton(text="➕ Добавить ребёнка")],
    ]
    if user["children"]:
        kb.append([types.KeyboardButton(text="🔁 Выбрать активного ребёнка")])
        kb.append([types.KeyboardButton(text="🗑 Удалить ребёнка")])
    kb.append([types.KeyboardButton(text="⬅️ В главное меню")])
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def chat_mode_keyboard():
    kb = [
        [types.KeyboardButton(text="⬅️ В главное меню")],
        [types.KeyboardButton(text="✏️ Новый вопрос по этой теме")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def children_list_keyboard(user: dict, include_back: bool = True):
    kb = []
    for name in user["children"].keys():
        label = name
        if user["active_child"] == name:
            label = f"⭐ {name}"
        kb.append([types.KeyboardButton(text=label)])
    if include_back:
        kb.append([types.KeyboardButton(text="⬅️ Назад к профилям")])
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    user = get_user(uid)
    user.update(
        {
            "state": "idle",
            "mode": "scenario",
            "category": None,
            "scenario": None,
            "step": 0,
            "data": {},
            "history": [],
            "profile_mode": None,
        }
    )

    await message.answer(
        "👋 Привет! Я MAMAUMNEY — помощник мамы.\n\n"
        "Сначала выбери, с чем помочь:",
        reply_markup=main_menu_keyboard(),
    )


@dp.message()
async def handle_message(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    user = get_user(uid)

    # глобальная кнопка назад в главное меню
    if text == "⬅️ В главное меню":
        user.update(
            {
                "state": "idle",
                "mode": "scenario",
                "category": None,
                "scenario": None,
                "step": 0,
                "data": {},
                "history": [],
                "profile_mode": None,
            }
        )
        await message.answer("Выбирай, с чем помочь дальше:", reply_markup=main_menu_keyboard())
        return

    # назад в меню профилей
    if text == "⬅️ Назад к профилям":
        user["profile_mode"] = None
        await show_profiles_menu(message, user)
        return

    # если сейчас идёт сценарий – все сообщения в run_scenario
    if user["mode"] == "scenario" and user["scenario"] is not None:
        await run_scenario(message, user, text)
        return

    # режим управления профилями детей
    if user["profile_mode"] is not None:
        await handle_profiles_flow(message, user, text)
        return

    # чат‑режим (после того, как сценарий уже отработал)
    if user["mode"] == "chat":
        await handle_chat_mode(message, user, text)
        return

    # запуск сценариев питания из подменю
    if text == "📅 Меню и список продуктов":
        await start_food_scenario(message, "food_menu")
        return

    if text == "👩‍🍳 Быстрые рецепты":
        await start_food_scenario(message, "food_recipes")
        return

    # меню профилей детей
    if text == "👶 Профили детей":
        await show_profiles_menu(message, user)
        return

    # выбор категории (когда сценарий не активен)
    await handle_category_choice(message, user, text)


async def show_profiles_menu(message: types.Message, user: dict):
    children = user["children"]
    if not children:
        txt = (
            "Пока нет ни одного профиля ребёнка.\n\n"
            "Нажми «➕ Добавить ребёнка», чтобы создать первый профиль."
        )
    else:
        lines = ["Текущие профили детей:"]
        for name, desc in children.items():
            mark = "⭐" if user["active_child"] == name else "•"
            lines.append(f"{mark} {name}: {desc}")
        txt = "\n".join(lines)

    await message.answer(txt, reply_markup=profiles_menu_keyboard(user))


async def handle_profiles_flow(message: types.Message, user: dict, text: str):
    mode = user["profile_mode"]

    # создание нового ребёнка
    if mode == "create_child":
        # ожидаем формат: Имя: описание
        if ":" not in text:
            await message.answer(
                "Напиши в формате: Имя: короткое описание (возраст, пол).\n"
                "Пример: «Мира: девочка, 3 года 2 месяца»."
            )
            return
        name, desc = [p.strip() for p in text.split(":", 1)]
        if not name:
            await message.answer("Имя не должно быть пустым. Попробуй ещё раз.")
            return
        user["children"][name] = desc
        user["active_child"] = name
        user["profile_mode"] = None
        await message.answer(
            f"Профиль «{name}» сохранён и выбран как активный.",
            reply_markup=profiles_menu_keyboard(user),
        )
        return

    # выбор активного ребёнка
    if mode == "switch_child":
        # на кнопках активный помечен «⭐», уберём её если есть
        clean = text.replace("⭐", "").strip()
        if clean not in user["children"]:
            await message.answer("Выбери ребёнка кнопкой из списка ниже.", reply_markup=children_list_keyboard(user))
            return
        user["active_child"] = clean
        user["profile_mode"] = None
        await message.answer(
            f"Активный ребёнок: {clean}.",
            reply_markup=profiles_menu_keyboard(user),
        )
        return

    # удаление ребёнка
    if mode == "delete_child":
        clean = text.replace("⭐", "").strip()
        if clean not in user["children"]:
            await message.answer("Выбери ребёнка для удаления кнопкой из списка.", reply_markup=children_list_keyboard(user))
            return
        del user["children"][clean]
        if user["active_child"] == clean:
            user["active_child"] = next(iter(user["children"]), None)
        user["profile_mode"] = None
        await message.answer(
            f"Профиль «{clean}» удалён.",
            reply_markup=profiles_menu_keyboard(user),
        )
        return


async def handle_chat_mode(message: types.Message, user: dict, text: str):
    if text == "✏️ Новый вопрос по этой теме":
        await message.answer("Задай свой вопрос по этой теме — доработаем план.")
        return

    history = user.get("history", [])
    if not history:
        user["mode"] = "scenario"
        user["state"] = "idle"
        await message.answer("Давай начнём заново и выберем категорию:", reply_markup=main_menu_keyboard())
        return

    history.append({"role": "user", "content": text})
    answer = await call_gigachat(history)
    history.append({"role": "assistant", "content": answer})
    user["history"] = history

    await message.answer(answer, reply_markup=chat_mode_keyboard())


async def handle_category_choice(message: types.Message, user: dict, text: str):
    if text == "🍎 Питание и здоровье":
        user["category"] = "food"
        user["scenario"] = None
        user["step"] = 0
        user["data"] = {}
        await message.answer(
            "🍎 Категория «Питание и здоровье».\n\n"
            "Что тебе нужно сейчас?",
            reply_markup=food_menu_keyboard(),
        )
        return

    elif text.startswith("⚕️") or text.startswith("💸") or text.startswith("🧸"):
        await message.answer("Сейчас в приоритете доработка питания. Остальные категории временно отключены.")
    else:
        await message.answer("Выбери одну из категорий ниже:", reply_markup=main_menu_keyboard())


async def run_scenario(message: types.Message, user: dict, text: str):
    scenario_key = user["scenario"]
    scenario = SCENARIOS[scenario_key]
    step = user["step"]

    # шаг -1: создаём первый (или новый) профиль ребёнка через быстрый ввод
    if step == -1:
        # здесь мы ожидаем только описание ребёнка, имя берём из «по умолчанию»
        # но раз у нас уже есть система профилей, делаем так:
        # имя попросим отдельно: формат «Имя: описание»
        if ":" not in text:
            await message.answer(
                "Напиши в формате: Имя: короткое описание (возраст, пол).\n"
                "Пример: «Мира: девочка, 3 года 2 месяца»."
            )
            return
        name, desc = [p.strip() for p in text.split(":", 1)]
        if not name:
            await message.answer("Имя не должно быть пустым. Попробуй ещё раз.")
            return
        user["children"][name] = desc
        user["active_child"] = name
        user["step"] = 0
        await ask_next_question(message, user)
        return

    # сохраняем ответ на предыдущий вопрос
    if step > 0:
        prev_question = scenario["questions"][step - 1]
        user["data"][prev_question["key"]] = text

    await ask_next_question(message, user)


async def ask_next_question(message: types.Message, user: dict):
    scenario_key = user["scenario"]
    scenario = SCENARIOS[scenario_key]
    step = user["step"]

    if step < len(scenario["questions"]):
        q = scenario["questions"][step]
        user["step"] += 1
        await message.answer(q["text"])
        return

    # все ответы собраны — формируем запрос в модель
    data = user["data"].copy()
    active_name = user.get("active_child")
    if active_name and active_name in user["children"]:
        child_profile = f"{active_name}: {user['children'][active_name]}"
    else:
        child_profile = "не указан"
    data["child_profile"] = child_profile

    prompt = scenario["prompt_template"].format(**data)
    system_prompt = scenario["system"]

    await message.answer("✨ Вжух — готовлю для тебя персональный ответ по питанию.")
    answer = await ask_gigachat_single(system_prompt, prompt)

    # переключаем в режим чата
    user["mode"] = "chat"
    user["state"] = "idle"
    user["history"] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": answer},
    ]
    user["data"] = {}
    user["step"] = 0
    user["scenario"] = None

    if scenario_key == "food_menu":
        header = "🍎 Твой план по меню и продуктам:\n\n"
    else:
        header = "👩‍🍳 Твои быстрые рецепты:\n\n"

    await message.answer(header + answer, reply_markup=chat_mode_keyboard())


async def start_food_scenario(message: types.Message, scenario_key: str):
    uid = message.from_user.id
    user = get_user(uid)
    user["category"] = "food"
    user["mode"] = "scenario"
    user["scenario"] = scenario_key
    user["data"] = {}
    user["history"] = []

    # если нет ни одного профиля ребёнка — создаём через шаг -1
    if not user["children"] or not user["active_child"]:
        user["step"] = -1
        await message.answer(
            "Сначала создай профиль ребёнка.\n"
            "Напиши в формате: Имя: короткое описание (возраст, пол).\n"
            "Пример: «Мира: девочка, 3 года 2 месяца»."
        )
        return

    user["step"] = 0
    await ask_next_question(message, user)


# --------- ПРОФИЛИ: ВХОД ИЗ МЕНЮ ---------

@dp.message(lambda m: m.text in ["➕ Добавить ребёнка", "🔁 Выбрать активного ребёнка", "🗑 Удалить ребёнка"])
async def profiles_buttons(message: types.Message):
    uid = message.from_user.id
    user = get_user(uid)

    if message.text == "➕ Добавить ребёнка":
        user["profile_mode"] = "create_child"
        await message.answer(
            "Напиши в формате: Имя: короткое описание (возраст, пол).\n"
            "Пример: «Мира: девочка, 3 года 2 месяца»."
        )
        return

    if message.text == "🔁 Выбрать активного ребёнка":
        if not user["children"]:
            await message.answer("Пока нет ни одного ребёнка. Сначала добавь профиль.", reply_markup=profiles_menu_keyboard(user))
            return
        user["profile_mode"] = "switch_child"
        await message.answer("Выбери ребёнка, который сейчас актуален:", reply_markup=children_list_keyboard(user))
        return

    if message.text == "🗑 Удалить ребёнка":
        if not user["children"]:
            await message.answer("Удалять пока некого — профили ещё не созданы.", reply_markup=profiles_menu_keyboard(user))
            return
        user["profile_mode"] = "delete_child"
        await message.answer("Выбери ребёнка, профиль которого нужно удалить:", reply_markup=children_list_keyboard(user))
        return


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

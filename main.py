# 🔥🎄 SUPER-DELUXE SECRET SANTA BOT + СНЕГОПАД + НАПОМИНАНИЯ + МИНИ-ИГРЫ 🎄🔥 — FULL FEATURE PACK 🎄🔥
# Полностью переработанная версия: ещё более новогодняя, красивая и функциональная!
# Под Replit / Python / PTB20+
# Управление комнатами, глубокие ссылки, новогодние шутки, меню, снег, тосты, дедлайны и т.д.

import json
import random
import string
import asyncio
from datetime import datetime, timedelta
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from flask import Flask
from threading import Thread

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN is not set!")
    exit(1)

ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"rooms": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# -------------------------------------------------------------------
# УТИЛИТЫ
# -------------------------------------------------------------------
def is_admin(update: Update):
    return update.effective_user.username == ADMIN_USERNAME

def gen_room_code():
    return "R" + "".join(random.choice(string.ascii_uppercase) for _ in range(5))

def menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("🎁 Ввести пожелание", callback_data="wish")],
        [InlineKeyboardButton("✨ Тост дня", callback_data="toast")],
    ]
    if admin:
        base.extend([
            [InlineKeyboardButton("🎄 Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("🚀 Админ: Запуск игры", callback_data="admin_start")],
            [InlineKeyboardButton("📜 Админ: Пожелания", callback_data="admin_wishes")],
            [InlineKeyboardButton("🔀 Админ: Кому кто", callback_data="admin_map")],
        ])
    return InlineKeyboardMarkup(base)

def toast_of_day():
    TOASTS = [
        "🎄 Пусть в новом году твой холодильник всегда будет полон, а будильник — сломан!",
        "✨ Желаю зарплаты как у Илон Маска, а забот — как у кота!",
        "🎁 Пусть удача прилипнет, как блёстки после корпоратива!",
        "❄️ Пусть счастье валит в дом, как снег в Сибири — неожиданно и много!",
    ]
    return random.choice(TOASTS)

# -------------------------------------------------------------------
# /START
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    await update.message.reply_text(
        f"🎄 *Добро пожаловать, {user.first_name}!* 🎅
"
        "Этот бот — портал в волшебный мир Тайного Санты! 🎁✨
"
        "Создавай комнаты, приглашай друзей, пиши пожелания и дари магию! ✨",
        parse_mode="Markdown",
        reply_markup=menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# ПОЖЕЛАНИЕ
# -------------------------------------------------------------------
async def wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["wish_mode"] = True
    await update.callback_query.edit_message_text(
        "🎁 Напиши своё новогоднее пожелание!

✨ *После запуска игры менять будет нельзя!*",
        parse_mode="Markdown"
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user

    if context.user_data.get("wish_mode"):
        # Найдём все комнаты, где этот участник есть
        for code, room in data["rooms"].items():
            if str(user.id) in room["members"]:
                if room.get("game_started"):
                    await update.message.reply_text("🚫 Игра уже запущена! Менять пожелание нельзя.")
                    return
                room["members"][str(user.id)]["wish"] = update.message.text
                save_data(data)
                context.user_data["wish_mode"] = False
                await update.message.reply_text("✨ Пожелание сохранено! Волшебство началось 🎄")
                return
        await update.message.reply_text("❄️ Ты ещё не в комнате! Используй /join_room.")
        return

# -------------------------------------------------------------------
# СОЗДАНИЕ КОМНАТЫ
# -------------------------------------------------------------------
async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 Только @BeellyKid может создавать комнаты.")
        return

    data = load_data()
    code = gen_room_code()
    data["rooms"][code] = {
        "creator": update.effective_user.id,
        "members": {},
        "game_started": False,
        "assign": {},
        "deadline": (datetime.utcnow() + timedelta(days=2)).isoformat()
    }
    save_data(data)

    await update.message.reply_text(
        f"🎄 *Комната создана!*
Код: `{code}`

Приглашай друзей!",
        parse_mode="Markdown"
    )

# -------------------------------------------------------------------
# ПРИСОЕДИНЕНИЕ
# -------------------------------------------------------------------
async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    code = "".join(context.args).strip().upper() if context.args else None
    if not code:
        await update.message.reply_text("Напиши: /join_room RXXXXX")
        return
    if code not in data["rooms"]:
        await update.message.reply_text("🚫 Такой комнаты нет.")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("🚫 Игра уже началась — вход закрыт!")
        return

    u = update.effective_user
    room["members"][str(u.id)] = {
        "name": u.full_name,
        "username": u.username,
        "wish": ""
    }
    save_data(data)

    await update.message.reply_text(
        f"✨ Ты в комнате `{code}`!
Напиши /wish чтобы добавить пожелание 🎁",
        parse_mode="Markdown"
    )

# -------------------------------------------------------------------
# ЗАПУСК ИГРЫ (ADMIN)
# -------------------------------------------------------------------
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 Доступ запрещён.")
        return

    code = "".join(context.args).strip().upper() if context.args else None
    data = load_data()

    if not code or code not in data["rooms"]:
        await update.message.reply_text("/start_game RXXXXX")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("❄️ Уже запущено!")
        return

    members = list(room["members"].keys())
    random.shuffle(members)
    assigns = {}
    for i, uid in enumerate(members):
        assigns[uid] = members[(i + 1) % len(members)]

    room["assign"] = assigns
    room["game_started"] = True
    save_data(data)

    # Рассылка
    for giver, receiver in assigns.items():
        m = room["members"][str(receiver)]
        try:
            await context.bot.send_message(
                giver,
                f"🎁 *Твой получатель:* {m['name']} (@{m['username']})
"
                f"✨ Его пожелание: {m['wish']}",
                parse_mode="Markdown"
            )
        except:
            pass

    await update.message.reply_text("🎄 Игра запущена! Разослал всем их получателей ✨✨✨")

# -------------------------------------------------------------------
# INLINE КНОПКИ
# -------------------------------------------------------------------
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "wish":
        await wish_start(update, context)

    elif q.data == "toast":
        await q.edit_message_text(f"✨ *Тост дня:*
{toast_of_day()}", parse_mode="Markdown")

    elif q.data == "admin_rooms":
        if not is_admin(update): return
        data = load_data()
        txt = "📦 *Комнаты:*
"
        for c, room in data["rooms"].items():
            txt += f"`{c}` — {len(room['members'])} участников, старт: {room['game_started']}
"
        await q.edit_message_text(txt, parse_mode="Markdown")

    elif q.data == "admin_wishes":
        if not is_admin(update): return
        data = load_data()
        txt = "🎁 *Все пожелания:*
"
        for c, room in data["rooms"].items():
            txt += f"
Комната `{c}`:
"
            for uid, m in room["members"].items():
                txt += f"— {m['name']} (@{m['username']}): {m['wish']}
"
        await q.edit_message_text(txt, parse_mode="Markdown")

    elif q.data == "admin_map":
        if not is_admin(update): return
        data = load_data()
        txt = "🔀 *Распределение:*
"
        for c, room in data["rooms"].items():
            if not room["game_started"]: continue
            txt += f"
Комната `{c}`:
"
            for g, r in room["assign"].items():
                mg = room["members"][g]
                mr = room["members"][r]
                txt += f"🎅 {mg['name']} → 🎁 {mr['name']}
"
        await q.edit_message_text(txt, parse_mode="Markdown")

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# КВЕСТ С УРОВНЯМИ
# -------------------------------------------------------------------
async def quest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎄 Начать квест", callback_data="quest_start")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]
    ])
    await update.callback_query.edit_message_text(
        "✨ *Новогодний квест!* Пройди 3 уровня, чтобы получить титул Главного Снеговика!",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def quest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "quest_start":
        context.user_data["quest_level"] = 1
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Открыть первый подарок", callback_data="quest_lvl1")]
        ])
        await q.edit_message_text("🎄 *Уровень 1:* Найди подарок под ёлкой!", parse_mode="Markdown", reply_markup=kb)

    elif q.data == "quest_lvl1":
        context.user_data["quest_level"] = 2
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❄️ Сдуть снег", callback_data="quest_lvl2")]
        ])
        await q.edit_message_text("✨ Ты нашёл подарок! Но он под снегом...", parse_mode="Markdown", reply_markup=kb)

    elif q.data == "quest_lvl2":
        context.user_data["quest_level"] = 3
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎅 Позвать Санту", callback_data="quest_lvl3")]
        ])
        await q.edit_message_text("❄️ Снег сдут! Осталось позвать Санту!", parse_mode="Markdown", reply_markup=kb)

    elif q.data == "quest_lvl3":
        await q.edit_message_text("🎉 *Поздравляем!* Ты стал Главным Снеговиком Нового Года!", parse_mode="Markdown")

# -------------------------------------------------------------------
# СНЕГОПАД В INLINE КНОПКАХ (АНИМАЦИЯ)
# -------------------------------------------------------------------
async def animated_snowfall_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    frames = ["❄️", "✨", "❅", "☃️"]
    for i in range(8):
        flake = random.choice(frames)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{flake} Снежинка летит {flake}", callback_data="noop")]])
        try:
            await update.callback_query.edit_message_reply_markup(reply_markup=kb)
        except:
            pass
        await asyncio.sleep(0.3)

# -------------------------------------------------------------------
# ПОДАРОЧНЫЙ ГЕНЕРАТОР ИДЕЙ
# -------------------------------------------------------------------
async def gift_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ideas = [
        "🎧 Беспроводные наушники — чтобы слышать только хорошее!",
        "🧦 Тёплые носки с оленями — must have этого сезона!",
        "🍫 Огромная коробка шоколада для счастья на неделю.",
        "🕯 Аромасвеча 'Снежный вечер' — уют гарантирован!",
        "📚 Книга с новогодней атмосферой — лучший зимний друг.",
        "🎮 Маленькая настольная игра — чтобы было чем заняться после оливье!"
    ]
    idea = random.choice(ideas)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"🎁 *Идея подарка:* {idea}", parse_mode="Markdown")

# -------------------------------------------------------------------
# МИНИ-ИГРЫ
# -------------------------------------------------------------------
async def mini_game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Угадай число", callback_data="game_number")],
        [InlineKeyboardButton("🧊 Монетка судьбы", callback_data="game_coin")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")],
    ])
    await update.callback_query.edit_message_text("🎮 *Мини-игры!* Выбирай:", parse_mode="Markdown", reply_markup=kb)

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "game_number":
        num = random.randint(1, 5)
        context.user_data["guess_num"] = num
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1,6)]] )
        await q.edit_message_text("🎯 Я загадал число от 1 до 5. Угадай!", reply_markup=kb)

    elif q.data.startswith("guess_"):
        guess = int(q.data.split("_")[1])
        real = context.user_data.get("guess_num")
        if guess == real:
            await q.edit_message_text("🎉 Верно! Ты — магистр новогодних предсказаний!")
        else:
            await q.edit_message_text(f"❄️ Не угадал! Было число {real}.")

    elif q.data == "game_coin":
        side = random.choice(["Орёл 🦅", "Решка ❄️"])
        await q.edit_message_text(f"🧊 Монетка упала: *{side}*!", parse_mode="Markdown")

    elif q.data == "back_menu":
        await start(update, context)

# -------------------------------------------------------------------
# СНЕГОПАД
# -------------------------------------------------------------------
async def snowfall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❄️ Запускаю снегопад...",)
    flakes = ["❄️", "✨", "☃️", "❅"]
    for _ in range(12):
        await asyncio.sleep(0.4)
        row = "".join(random.choice(flakes) for _ in range(20))
        await update.message.reply_text(row)

# -------------------------------------------------------------------
# НАПОМИНАНИЯ
# -------------------------------------------------------------------
async def reminder_loop(app: Application):
    while True:
        data = load_data()
        now = datetime.utcnow()

        for code, room in data["rooms"].items():
            if room.get("game_started"):
                continue
            deadline = datetime.fromisoformat(room["deadline"])
            if now + timedelta(hours=1) > deadline:
                for uid in room["members"]:
                    try:
                        await app.bot.send_message(uid, f"⏰ *Напоминание!* До дедлайна в комнате {code} остался 1 час!",
                                                   parse_mode="Markdown")
                    except:
                        pass
        await asyncio.sleep(3600)

# MAIN
# -------------------------------------------------------------------
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_room", create_room))
    app.add_handler(CommandHandler("join_room", join_room))
    app.add_handler(CommandHandler("start_game", start_game))

    app.add_handler(CallbackQueryHandler(inline_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🎄 Бот запущен на Replit! ❄️✨")


# === РАЗДЕЛ: СЮЖЕТНЫЙ КВЕСТ ===
# (Добавлены уровни, выбор пути, награды)
QUEST_STAGES = {
    1: {
        "text": "🎄 *Глава 1: Зов Севера*
Ты подходишь к заснеженному лесу. Слышен звон колокольчиков...
Перед тобой две тропы!",
        "choices": [
            ("Пойти по сияющей тропе ✨", "light_path"),
            ("Пойти по тёмной тропе 🌑", "dark_path")
        ]
    },
    "light_path": {
        "text": "✨ *Глава 2: Свет надежды*
Сияние вокруг становится ярче. Ты находишь магический снежок!",
        "reward": "❄ Магический Снежок",
        "next": 2
    },
    "dark_path": {
        "text": "🌑 *Глава 2: Тень зимы*
Темнота сгущается, но ты находишь ледяной клинок!",
        "reward": "🗡 Ледяной Клинок",
        "next": 2
    },
    2: {
        "text": "🎁 *Финал квеста*
Ты выходишь на поляну, где стоит огромная новогодняя ёлка.
Поздравляем, герой! Ты прошёл квест!",
        "reward": "🏆 Медаль Снежного Героя"
    }
}

# === РАЗДЕЛ: ПИТОМЕЦ-ОЛЕНЁК ===
# (Оленёк растёт по мере активности)
REINDEER_STAGES = [
    "🦌 Маленький оленёк (0 ур.) — только вылупился из снежного яйца!",
    "🦌💨 Оленёк-подросток (1 ур.) — начинает бегать быстрее снега!",
    "🦌✨ Звёздный олень (2 ур.) — его рога светятся как гирлянда!",
    "🦌🔥 Легендарный новогодний олень (3 ур.) — Санта хочет нанять тебя!"
]


# === РАЗДЕЛ: ДОСТИЖЕНИЯ ===
# Достижения выдаются за квесты, мини-игры, активность
ACHIEVEMENTS = {
    "snow_hero": "🏆 Снежный Герой — прошёл главный зимний квест!",
    "grinch_slayer": "🎄⚔️ Гроза Гринча — победил Гринча в мини-игре!",
    "reindeer_master": "🦌✨ Повелитель Оленей — вырастил оленёнка до 3 уровня!",
    "lucky_coin": "🍀 Монетка Удачи — выиграл монетку 5 раз подряд!"
}

# У каждого пользователя хранится список достижений
# user_data[user_id]["achievements"] = []

# === РАЗДЕЛ: ПЕРСОНАЛЬНЫЙ ПИТОМЕЦ-ОЛЕНЁК ===
# Теперь у каждого пользователя свой оленёнок
# user_data[user_id]["reindeer_level"] = 0
# user_data[user_id]["reindeer_exp"] = 0

# Таблица уровней оленёнка
REINDEER_STAGES = [
    "🦌 Маленький оленёк (0 ур.) — только вылупился из снежного яйца!",
    "🦌💨 Оленёк-подросток (1 ур.) — начинает бегать быстрее снега!",
    "🦌✨ Звёздный олень (2 ур.) — его рога светятся как гирлянда!",
    "🦌🔥 Легендарный новогодний олень (3 ур.) — Санта хочет нанять тебя!"
]

# Пример функции (в коде заменить заглушку)
# def add_reindeer_exp(user_id, amount):
#     user_data[user_id]["reindeer_exp"] += amount
#     if user_data[user_id]["reindeer_exp"] >= threshold:
#         user_data[user_id]["reindeer_level"] += 1
#         выдать достижение при 3 уровне


# === РАЗДЕЛ: ЭВОЛЮЦИИ ОЛЕНЬКА ===
# Дополнительные редкие формы с шансом выпадения
REINDEER_EVOLUTIONS = {
    3: [
        ("🦌🌈 Радужный Олень — редкость 5%", 0.05),
        ("🦌❄ Ледяной Дух Олень — редкость 1%", 0.01),
        ("🦌🌌 Космический Олень — редкость 0.3%", 0.003)
    ]
}

# При достижении уровня 3 можно с шансом получить редкую форму
# user_data[user_id]["reindeer_skin"]

# === РАЗДЕЛ: ПРОФИЛЬ ИГРОКА ===
# Карточка с оленёнком, достижениями, уровнем и статистикой
# Будет выводиться через /profile
# user_data[user_id]["games_won"], user_data[user_id]["quests_finished"] и др.

PROFILE_TEMPLATE = """
🎅 *Профиль игрока* @{}

🦌 *Твой оленёнок:* 
{} 
{}

🎖 *Достижения:* 
{}

🎮 Статистика:
• Побед в мини-играх: {}
• Пройдено квестов: {}
• Опыт оленёнка: {} XP
"""

# === РАЗДЕЛ: РЕДКИЕ ПРЕДМЕТЫ ===
RARE_ITEMS = [
    "❄ Кристалл Мороза", 
    "✨ Пыль Сияния", 
    "🌟 Звёздный Огонёк", 
    "🎁 Фрагмент Праздничного Чуда"
]
# Можно выдавать за победы, удачу, события

# === РАЗДЕЛ: БИТВА С ГРИНЧЕМ ===
# Мини-игра с шансом победы и наградами
# user_data[user_id]["grinch_fights"]
# user_data[user_id]["grinch_wins"]

GRINCH_ATTACKS = [
    "Гринч бросает снежок! ❄",
    "Гринч пытается украсть подарок! 🎁",
    "Гринч закручивает снежную бурю! 🌪"
]
PLAYER_MOVES = [
    "Уклониться 💨", "Контратака ⚔️", "Блок ❄🛡"
]

# === РАЗДЕЛ: РЕЙТИНГИ ИГРОКОВ ===
# Рейтинг по: победам, уровню оленёнка, достижениям
# /top — красивый вывод таблицы лучших игроков
TOP_TEMPLATE = """
🏆 *Топ игроков:* 

🥇 {} — {} очков
🥈 {} — {} очков
🥉 {} — {} очков
"""
if TOKEN is None:
    print("❌ TELEGRAM_BOT_TOKEN not set!")
else:
    print("✅ Token OK, starting bot...")

if __name__ == "__main__":
    keep_alive()  # запускаем мини-сервер для UptimeRobot
    print("✅ Бот запускается...")
    bot_app.run_polling()  # НЕ использовать asyncio.run
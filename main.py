# 🔥🎄 SUPER-DELUXE SECRET SANTA BOT + СНЕГОПАД + НАПОМИНАНИЯ + МИНИ-ИГРЫ 🎄🔥 — FULL FEATURE PACK 🎄🔥
# Полностью переработанная версия: ещё более новогодняя, красивая и функциональная!
# Под Replit / Python / PTB20+
# Управление комнатами, глубокие ссылки, новогодние шутки, меню, снег, тосты, дедлайны и т.д.

import json
import random
import string
import asyncio
import os
from datetime import datetime, timedelta, timezone
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# Безопасное получение токена для Replit
TOKEN = os.environ.get("TELEGRAM_TOKEN", "1667037381:AAFdA7l6LcMidWsgrerdOkpBXfNF2gbNsvo")
ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"

# Глобальная переменная для хранения данных
user_data = {}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Инициализируем user_data если её нет в файле
            if "users" not in data:
                data["users"] = {}
            global user_data
            user_data = data["users"]
            return data
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"rooms": {}, "users": {}}

def save_data(data):
    # Сохраняем user_data в общую структуру
    data["users"] = user_data
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

# -------------------------------------------------------------------
# УТИЛИТЫ
# -------------------------------------------------------------------
def is_admin(update: Update):
    return update.effective_user.username == ADMIN_USERNAME

def gen_room_code():
    return "R" + "".join(random.choice(string.ascii_uppercase) for _ in range(5))

def menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("🎁 Ввести пожелание", callback_data="wish"),
         InlineKeyboardButton("✨ Тост дня", callback_data="toast")],
        [InlineKeyboardButton("🎮 Мини-игры", callback_data="mini_games"),
         InlineKeyboardButton("❄️ Снегопад", callback_data="snowfall")],
        [InlineKeyboardButton("🎁 Идея подарка", callback_data="gift_idea"),
         InlineKeyboardButton("🎄 Квест", callback_data="quest_menu")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")]
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
        "🎄 Пусть в новом году твой холодильник всегда будет полен, а будильник — сломан!",
        "✨ Желаю зарплаты как у Илон Маска, а забот — как у кота!",
        "🎁 Пусть удача прилипнет, как блёстки после корпоратива!",
        "❄️ Пусть счастье валит в дом, как снег в Сибири — неожиданно и много!",
    ]
    return random.choice(TOASTS)

# Инициализация данных пользователя
def init_user_data(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "reindeer_level": 0,
            "reindeer_exp": 0,
            "achievements": [],
            "games_won": 0,
            "quests_finished": 0,
            "reindeer_skin": "default",
            "grinch_fights": 0,
            "grinch_wins": 0,
            "rare_items": []
        }

def add_achievement(user_id, achievement_key):
    init_user_data(user_id)
    if achievement_key not in user_data[str(user_id)]["achievements"]:
        user_data[str(user_id)]["achievements"].append(achievement_key)

def add_reindeer_exp(user_id, amount):
    init_user_data(user_id)
    user_data[str(user_id)]["reindeer_exp"] += amount
    
    # Проверка повышения уровня
    current_level = user_data[str(user_id)]["reindeer_level"]
    exp_needed = (current_level + 1) * 100
    
    if user_data[str(user_id)]["reindeer_exp"] >= exp_needed and current_level < 3:
        user_data[str(user_id)]["reindeer_level"] += 1
        user_data[str(user_id)]["reindeer_exp"] = 0
        
        # Проверка на редкую эволюцию
        if current_level + 1 == 3:
            if random.random() < 0.05:  # 5% шанс
                user_data[str(user_id)]["reindeer_skin"] = "rainbow"
                add_achievement(user_id, "rainbow_reindeer")
            elif random.random() < 0.01:  # 1% шанс
                user_data[str(user_id)]["reindeer_skin"] = "ice_spirit"
                add_achievement(user_id, "ice_spirit_reindeer")
            elif random.random() < 0.003:  # 0.3% шанс
                user_data[str(user_id)]["reindeer_skin"] = "cosmic"
                add_achievement(user_id, "cosmic_reindeer")
        
        if current_level + 1 == 3:
            add_achievement(user_id, "reindeer_master")

# -------------------------------------------------------------------
# /START
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    init_user_data(user.id)
    
    await update.message.reply_text(
        f"🎄 *Добро пожаловать, {user.first_name}!* 🎅\n\n"
        "Этот бот — портал в волшебный мир Тайного Санты! 🎁✨\n\n"
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
        "🎁 Напиши своё новогоднее пожелание!\n\n"
        "✨ *После запуска игры менять будет нельзя!*",
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
                add_reindeer_exp(user.id, 10)
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
        "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    }
    save_data(data)

    await update.message.reply_text(
        f"🎄 *Комната создана!*\nКод: `{code}`\n\nПриглашай друзей!",
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
    add_reindeer_exp(u.id, 20)

    await update.message.reply_text(
        f"✨ Ты в комнате `{code}`!\nНапиши /wish чтобы добавить пожелание 🎁",
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
    if len(members) < 2:
        await update.message.reply_text("🚫 Нужно минимум 2 участника!")
        return
        
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
                f"🎁 *Твой получатель:* {m['name']} (@{m['username']})\n\n"
                f"✨ Его пожелание: {m['wish']}",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")

    await update.message.reply_text("🎄 Игра запущена! Разослал всем их получателей ✨✨✨")

# -------------------------------------------------------------------
# ПРОФИЛЬ ИГРОКА
# -------------------------------------------------------------------
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    init_user_data(user.id)
    
    user_info = user_data[str(user.id)]
    
    # Получаем информацию об оленёнке
    reindeer_level = user_info["reindeer_level"]
    reindeer_exp = user_info["reindeer_exp"]
    
    REINDEER_STAGES = [
        "🦌 Маленький оленёк (0 ур.) — только вылупился из снежного яйца!",
        "🦌💨 Оленёк-подросток (1 ур.) — начинает бегать быстрее снега!",
        "🦌✨ Звёздный олень (2 ур.) — его рога светятся как гирлянда!",
        "🦌🔥 Легендарный новогодний олень (3 ур.) — Санта хочет нанять тебя!"
    ]
    
    reindeer_text = REINDEER_STAGES[reindeer_level]
    
    # Добавляем информацию о скине
    skin_info = ""
    if user_info["reindeer_skin"] == "rainbow":
        skin_info = "\n🌈 *Особый вид:* Радужный Олень!"
    elif user_info["reindeer_skin"] == "ice_spirit":
        skin_info = "\n❄️ *Особый вид:* Ледяной Дух Олень!"
    elif user_info["reindeer_skin"] == "cosmic":
        skin_info = "\n🌌 *Особый вид:* Космический Олень!"
    
    # Получаем достижения
    ACHIEVEMENTS = {
        "snow_hero": "🏆 Снежный Герой — прошёл главный зимний квест!",
        "grinch_slayer": "🎄⚔️ Гроза Гринча — победил Гринча в мини-игре!",
        "reindeer_master": "🦌✨ Повелитель Оленей — вырастил оленёнка до 3 уровня!",
        "lucky_coin": "🍀 Монетка Удачи — выиграл монетку 5 раз подряд!",
        "rainbow_reindeer": "🌈 Радужный Олень — получил редкую эволюцию!",
        "ice_spirit_reindeer": "❄️ Ледяной Дух — получил уникальную эволюцию!",
        "cosmic_reindeer": "🌌 Космический Олень — получил легендарную эволюцию!"
    }
    
    achievements_text = ""
    for achievement in user_info["achievements"]:
        if achievement in ACHIEVEMENTS:
            achievements_text += f"• {ACHIEVEMENTS[achievement]}\n"
    
    if not achievements_text:
        achievements_text = "Пока нет достижений. Будь активнее! 🎄"
    
    profile_text = f"""
🎅 *Профиль игрока* @{user.username if user.username else user.first_name}

🦌 *Твой оленёнок:* 
{reindeer_text} 
{skin_info}

🎖 *Достижения:* 
{achievements_text}

🎮 Статистика:
• Побед в мини-играх: {user_info['games_won']}
• Пройдено квестов: {user_info['quests_finished']}
• Опыт оленёнка: {reindeer_exp} XP
• Битв с Гринчем: {user_info['grinch_fights']} (побед: {user_info['grinch_wins']})
• Редких предметов: {len(user_info['rare_items'])}
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(profile_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(profile_text, parse_mode="Markdown")

# -------------------------------------------------------------------
# INLINE КНОПКИ
# -------------------------------------------------------------------
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "wish":
        await wish_start(update, context)

    elif q.data == "toast":
        await q.edit_message_text(f"✨ *Тост дня:*\n{toast_of_day()}", parse_mode="Markdown")

    elif q.data == "admin_rooms":
        if not is_admin(update): 
            await q.edit_message_text("🚫 Доступ запрещён.")
            return
        data = load_data()
        txt = "📦 *Комнаты:*\n"
        for c, room in data["rooms"].items():
            txt += f"`{c}` — {len(room['members'])} участников, старт: {room['game_started']}\n"
        await q.edit_message_text(txt, parse_mode="Markdown")

    elif q.data == "admin_wishes":
        if not is_admin(update): 
            await q.edit_message_text("🚫 Доступ запрещён.")
            return
        data = load_data()
        txt = "🎁 *Все пожелания:*\n"
        for c, room in data["rooms"].items():
            txt += f"\nКомната `{c}`:\n"
            for uid, m in room["members"].items():
                txt += f"— {m['name']} (@{m['username']}): {m['wish']}\n"
        await q.edit_message_text(txt, parse_mode="Markdown")

    elif q.data == "admin_map":
        if not is_admin(update): 
            await q.edit_message_text("🚫 Доступ запрещён.")
            return
        data = load_data()
        txt = "🔀 *Распределение:*\n"
        for c, room in data["rooms"].items():
            if not room["game_started"]: continue
            txt += f"\nКомната `{c}`:\n"
            for g, r in room["assign"].items():
                mg = room["members"][g]
                mr = room["members"][r]
                txt += f"🎅 {mg['name']} → 🎁 {mr['name']}\n"
        await q.edit_message_text(txt, parse_mode="Markdown")
        
    elif q.data == "profile":
        await show_profile(update, context)
        
    elif q.data == "mini_games":
        await mini_game_menu(update, context)
        
    elif q.data == "quest_menu":
        await quest_menu(update, context)
        
    elif q.data == "gift_idea":
        await gift_idea(update, context)
        
    elif q.data == "snowfall":
        await animated_snowfall_buttons(update, context)
        
    elif q.data == "back_menu":
        admin = is_admin(update)
        await q.edit_message_text(
            "🎄 Возвращаемся в главное меню...",
            reply_markup=menu_keyboard(admin)
        )

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
        user = update.effective_user
        init_user_data(user.id)
        user_data[str(user.id)]["quests_finished"] += 1
        add_reindeer_exp(user.id, 50)
        add_achievement(user.id, "snow_hero")
        
        # Добавляем редкий предмет
        RARE_ITEMS = [
            "❄ Кристалл Мороза", 
            "✨ Пыль Сияния", 
            "🌟 Звёздный Огонёк", 
            "🎁 Фрагмент Праздничного Чуда"
        ]
        rare_item = random.choice(RARE_ITEMS)
        user_data[str(user.id)]["rare_items"].append(rare_item)
        
        await q.edit_message_text(
            f"🎉 *Поздравляем!* Ты стал Главным Снеговиком Нового Года!\n\n"
            f"✨ Награды:\n"
            f"• +50 опыта оленёнку\n"
            f"• Достижение 'Снежный Герой'\n"
            f"• Редкий предмет: {rare_item}",
            parse_mode="Markdown"
        )

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
    
    # Возвращаем нормальное меню
    admin = is_admin(update)
    await update.callback_query.edit_message_text(
        "❄️ Снегопад завершён! Волшебство продолжается...",
        reply_markup=menu_keyboard(admin)
    )

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
        [InlineKeyboardButton("⚔️ Битва с Гринчем", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")],
    ])
    await update.callback_query.edit_message_text("🎮 *Мини-игры!* Выбирай:", parse_mode="Markdown", reply_markup=kb)

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "game_number":
        num = random.randint(1, 5)
        context.user_data["guess_num"] = num
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1,6)]])
        await q.edit_message_text("🎯 Я загадал число от 1 до 5. Угадай!", reply_markup=kb)

    elif q.data.startswith("guess_"):
        guess = int(q.data.split("_")[1])
        real = context.user_data.get("guess_num")
        user = update.effective_user
        init_user_data(user.id)
        
        if guess == real:
            user_data[str(user.id)]["games_won"] += 1
            add_reindeer_exp(user.id, 15)
            await q.edit_message_text("🎉 Верно! Ты — магистр новогодних предсказаний!")
        else:
            await q.edit_message_text(f"❄️ Не угадал! Было число {real}.")

    elif q.data == "game_coin":
        side = random.choice(["Орёл 🦅", "Решка ❄️"])
        user = update.effective_user
        init_user_data(user.id)
        
        # Проверяем серию побед
        if "coin_wins" not in context.user_data:
            context.user_data["coin_wins"] = 0
            
        if side == "Орёл 🦅":
            context.user_data["coin_wins"] += 1
            if context.user_data["coin_wins"] >= 5:
                add_achievement(user.id, "lucky_coin")
                await q.edit_message_text(f"🧊 Монетка упала: *{side}!*\n\n🎉 Ты выиграл 5 раз подряд! Получено достижение 'Монетка Удачи'!", parse_mode="Markdown")
                context.user_data["coin_wins"] = 0
            else:
                await q.edit_message_text(f"🧊 Монетка упала: *{side}!*", parse_mode="Markdown")
        else:
            context.user_data["coin_wins"] = 0
            await q.edit_message_text(f"🧊 Монетка упала: *{side}!*", parse_mode="Markdown")

    elif q.data == "game_grinch":
        await grinch_battle(update, context)
        
    elif q.data == "back_menu":
        admin = is_admin(update)
        await q.edit_message_text(
            "🎄 Возвращаемся в главное меню...",
            reply_markup=menu_keyboard(admin)
        )

# -------------------------------------------------------------------
# БИТВА С ГРИНЧЕМ
# -------------------------------------------------------------------
async def grinch_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    user_data[str(user.id)]["grinch_fights"] += 1
    
    GRINCH_ATTACKS = [
        "Гринч бросает снежок! ❄",
        "Гринч пытается украсть подарок! 🎁",
        "Гринч закручивает снежную бурю! 🌪"
    ]
    PLAYER_MOVES = [
        "Уклониться 💨", "Контратака ⚔️", "Блок ❄🛡"
    ]
    
    grinch_attack = random.choice(GRINCH_ATTACKS)
    player_move = random.choice(PLAYER_MOVES)
    
    # Определяем результат битвы (50% шанс победы)
    if random.random() > 0.5:
        result = "🎉 Ты победил Гринча! Новый год спасён!"
        user_data[str(user.id)]["grinch_wins"] += 1
        user_data[str(user.id)]["games_won"] += 1
        add_reindeer_exp(user.id, 25)
        
        # Шанс получить достижение
        if user_data[str(user.id)]["grinch_wins"] >= 3:
            add_achievement(user.id, "grinch_slayer")
            result += "\n\n🎖 Получено достижение 'Гроза Гринча'!"
    else:
        result = "💔 Гринч победил... Но ты сможешь в следующий раз!"
    
    battle_text = f"""
⚔️ *Битва с Гринчем!*

{grinch_attack}
Ты используешь: {player_move}

{result}
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Сразиться снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(battle_text, parse_mode="Markdown", reply_markup=kb)

# -------------------------------------------------------------------
# СНЕГОПАД
# -------------------------------------------------------------------
async def snowfall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❄️ Запускаю снегопад...")
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
        try:
            data = load_data()
            now = datetime.now(timezone.utc)

            for code, room in data["rooms"].items():
                if room.get("game_started"):
                    continue
                deadline = datetime.fromisoformat(room["deadline"])
                if now + timedelta(hours=1) > deadline:
                    for uid in room["members"]:
                        try:
                            await app.bot.send_message(
                                int(uid), 
                                f"⏰ *Напоминание!* До дедлайна в комнате {code} остался 1 час!",
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            print(f"Ошибка отправки напоминания: {e}")
            await asyncio.sleep(3600)  # Проверка каждый час
        except Exception as e:
            print(f"Ошибка в reminder_loop: {e}")
            await asyncio.sleep(60)

# -------------------------------------------------------------------
# КОМАНДА ДЛЯ РУЧНОГО ЗАПУСКА НАПОМИНАНИЙ
# -------------------------------------------------------------------
async def start_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 Доступ запрещён.")
        return
        
    # Запускаем в фоне без создания новой задачи
    asyncio.get_event_loop().create_task(reminder_loop(context.application))
    await update.message.reply_text("🔔 Напоминания запущены!")

# -------------------------------------------------------------------
# ТОП ИГРОКОВ
# -------------------------------------------------------------------
async def show_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Собираем статистику всех пользователей
    player_stats = []
    
    for user_id, data in user_data.items():
        score = (
            data.get("games_won", 0) * 10 +
            data.get("quests_finished", 0) * 20 +
            data.get("reindeer_level", 0) * 30 +
            data.get("grinch_wins", 0) * 15 +
            len(data.get("achievements", [])) * 25
        )
        player_stats.append((user_id, score, data))
    
    # Сортируем по очкам
    player_stats.sort(key=lambda x: x[1], reverse=True)
    
    top_text = "🏆 *Топ игроков:* \n\n"
    
    if not player_stats:
        top_text += "Пока никто не играл... Будь первым! 🎄"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, score, data) in enumerate(player_stats[:10]):
            if i < 3:
                medal = medals[i]
            else:
                medal = f"{i+1}."
            
            # Пытаемся получить имя пользователя
            try:
                user = await context.bot.get_chat(int(user_id))
                name = f"@{user.username}" if user.username else user.first_name
            except:
                name = f"Игрок {user_id}"
                
            top_text += f"{medal} {name} — {score} очков\n"
    
    await update.message.reply_text(top_text, parse_mode="Markdown")

# MAIN
# -------------------------------------------------------------------
def main():
    # Загружаем данные при старте
    load_data()
    
    app = Application.builder().token(TOKEN).build()

    # Основные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_room", create_room))
    app.add_handler(CommandHandler("join_room", join_room))
    app.add_handler(CommandHandler("start_game", start_game))
    app.add_handler(CommandHandler("snowfall", snowfall))
    app.add_handler(CommandHandler("top", show_top))
    app.add_handler(CommandHandler("start_reminders", start_reminders))
    app.add_handler(CommandHandler("profile", show_profile))

    # Обработчики callback'ов
    app.add_handler(CallbackQueryHandler(inline_handler, pattern="^(wish|toast|admin_rooms|admin_wishes|admin_map|profile|mini_games|quest_menu|gift_idea|snowfall|back_menu)$"))
    app.add_handler(CallbackQueryHandler(quest_handler, pattern="^quest"))
    app.add_handler(CallbackQueryHandler(game_handler, pattern="^game"))
    app.add_handler(CallbackQueryHandler(grinch_battle, pattern="^game_grinch"))
    
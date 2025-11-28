# -*- coding: utf-8 -*-
# ???? SUPER-DELUXE SECRET SANTA BOT v3.1 — Исправленная полная версия для Replit
# Убедитесь, что в Replit в переменных окружения задан TELEGRAM_TOKEN
# Требуется python-telegram-bot v20+ (async API)
# pip install python-telegram-bot --upgrade

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

# -------------------- Конфигурация --------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"

print("?? Запуск Secret Santa Bot v3.1...")

# -------------------- Хранилище --------------------
user_data = {}  # локальный кэш пользователей

def load_data():
    global user_data
    try:
        if not os.path.exists(DATA_FILE):
            data = {"rooms": {}, "users": {}}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            user_data = data["users"]
            return data

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "rooms" not in data:
                data["rooms"] = {}
            if "users" not in data:
                data["users"] = {}
            user_data = data["users"]
            return data
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"rooms": {}, "users": {}}

def save_data(data):
    global user_data
    try:
        data["users"] = user_data
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

# -------------------- Утилиты --------------------
def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

def gen_room_code():
    return "R" + "".join(random.choice(string.ascii_uppercase) for _ in range(5))

def back_to_menu_keyboard(admin=False):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Назад в меню", callback_data="back_menu")]
    ])

def enhanced_menu_keyboard(admin=False):
    # Главное меню — кнопки в зависимости от прав
    buttons = [
        [InlineKeyboardButton("?? Написать пожелание", callback_data="wish_start")],
        [InlineKeyboardButton("?? Присоединиться к комнате", callback_data="join_room_menu"),
         InlineKeyboardButton("? Создать комнату", callback_data="create_room")],
        [InlineKeyboardButton("?? Показать участников комнаты", callback_data="show_members")],
        [InlineKeyboardButton("?? Генератор идей подарков", callback_data="gift_idea")]
    ]
    if admin:
        buttons.append([InlineKeyboardButton("?? Админ: Запустить игру", callback_data="admin_start_game")])
        buttons.append([InlineKeyboardButton("?? Админ: Рассылка", callback_data="admin_broadcast")])
    return InlineKeyboardMarkup(buttons)

def toast_of_day():
    TOASTS = [
        "?? Пусть в новом году твой холодильник всегда будет полон, а будильник — сломан!",
        "? Желаю зарплаты как у Илон Маска, а забот — как у кота!",
        "?? Пусть удача прилипнет, как блёстки после корпоратива!",
        "?? Пусть счастье валит в дом, как снег в Сибири — неожиданно и много!",
        "?? Пусть каждый день нового года будет как первый день отпуска!",
        "?? Желаю, чтобы под ёлкой всегда находилось именно то, о чём мечталось!",
        "?? Пусть звёзды с неба достаются без особых усилий!",
        "?? Пусть печеньки всегда будут свежими, а настроение — отличным!",
        "?? Желаю, чтобы олени в жизни были только послушными!",
        "?? Пусть новогодние песни звучат только в радость!",
        "?? Желаю, чтобы шампанское било через край, а проблемы — мимо!",
        "??? Пусть огоньки гирлянд освещают только счастливые моменты!",
        "?? Желаю морозных узоров на окнах и тепла в сердце!",
        "?? Пусть сюрпризы будут только приятными!",
        "?? Желаю сладкой жизни без горьких проблесков!",
        "??? Пусть бой курантов приносит только хорошие новости!",
        "?? Желаю, чтобы жизнь была цирком, где ты — главный акробат!",
        "?? Пусть носки всегда парные, а мысли — ясные!",
        "?? Желаю, чтобы камин горел, а проблемы — нет!",
        "?? Пусть фейерверки эмоций затмят все печали!"
    ]
    return random.choice(TOASTS)

# -------------------- Система очков и профиля --------------------
def init_user_data(user_id):
    global user_data
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {
            "reindeer_level": 0,
            "reindeer_exp": 0,
            "santa_points": 100,
            "achievements": [],
            "games_won": 0,
            "quests_finished": 0,
            "reindeer_skin": "default",
            "grinch_fights": 0,
            "grinch_wins": 0,
            "rare_items": [],
            "unlocked_reindeers": ["default"],
            "current_reindeer": "default",
            "checkers_wins": 0,
            "checkers_losses": 0,
            "quiz_wins": 0,
            "total_points": 0,
            "name": "",
            "username": "",
            "answered_quiz_questions": [],
            "last_checkers_win": None
        }

def add_santa_points(user_id, points, context: ContextTypes.DEFAULT_TYPE = None):
    init_user_data(user_id)
    uid = str(user_id)
    user_data[uid]["santa_points"] += points
    user_data[uid]["total_points"] += points
    # уведомление при больших изменениях
    if context and abs(points) >= 50:
        try:
            asyncio.create_task(context.bot.send_message(
                chat_id=user_id,
                text=f"?? {'Получено' if points > 0 else 'Потеряно'} {abs(points)} очков Санты!"
            ))
        except Exception:
            pass

def add_reindeer_exp(user_id, amount):
    init_user_data(user_id)
    uid = str(user_id)
    user_data[uid]["reindeer_exp"] += amount
    current_level = user_data[uid]["reindeer_level"]
    exp_needed = (current_level + 1) * 100
    if user_data[uid]["reindeer_exp"] >= exp_needed and current_level < 5:
        user_data[uid]["reindeer_level"] += 1
        user_data[uid]["reindeer_exp"] = 0
        new_skin = None
        evolution_chance = random.random()
        lvl = current_level + 1
        if lvl == 3:
            if evolution_chance < 0.02:
                new_skin = "ice_spirit"
            elif evolution_chance < 0.1:
                new_skin = "rainbow"
        elif lvl == 4:
            if evolution_chance < 0.015:
                new_skin = "crystal"
            elif evolution_chance < 0.08:
                new_skin = "golden"
        elif lvl == 5:
            if evolution_chance < 0.01:
                new_skin = "phantom"
            elif evolution_chance < 0.05:
                new_skin = "cosmic"
        if new_skin:
            user_data[uid]["reindeer_skin"] = new_skin
            if new_skin not in user_data[uid]["unlocked_reindeers"]:
                user_data[uid]["unlocked_reindeers"].append(new_skin)
            add_achievement(user_id, f"{new_skin}_reindeer")
        if lvl == 5:
            add_achievement(user_id, "reindeer_master")

def add_achievement(user_id, achievement_key):
    init_user_data(user_id)
    uid = str(user_id)
    if achievement_key not in user_data[uid]["achievements"]:
        user_data[uid]["achievements"].append(achievement_key)
        add_santa_points(user_id, 50)

# -------------------- Генератор идей подарков --------------------
def generate_gift_idea():
    CATEGORIES = {
        "?? Техника и гаджеты": [
            "Умная колонка с голосовым помощником",
            "Беспроводные наушники с шумоподавлением",
            "Портативное зарядное устройство 10000 mAh",
            "Электронная книга с подсветкой",
            "Умные часы с отслеживанием активности",
            "Игровая консоль портативная",
            "Bluetooth-колонка водонепроницаемая",
            "Фитнес-браслет с пульсометром",
            "Внешний аккумулятор с беспроводной зарядкой",
            "Смарт-лампа с изменением цветовой температуры",
            "Робот-пылесос для уборки",
            "Электрическая зубная щетка",
            "Массажер для шеи и плеч",
            "Электронный планшет для рисования"
        ],
        "?? Творчество и хобби": [
            "Набор для рисования светом",
            "Конструктор для взрослых с мелкими деталями",
            "Набор для создания свечей ручной работы",
            "Алмазная вышивка с новогодним сюжетом",
            "Гончарный набор миниатюрный",
            "Набор для каллиграфии",
            "Набор для вязания с пряжей",
            "Краски по номерам с новогодним пейзажем",
            "Набор для вышивания крестиком",
            "3D-пазл архитектурного сооружения",
            "Набор для создания украшений",
            "Скетчбук и профессиональные маркеры"
        ],
        "?? Уют и дом": [
            "Плед с подогревом и таймером",
            "Аромадиффузер с эфирными маслами",
            "Набор чайных пар с новогодним дизайном",
            "Проектор звёздного неба для комнаты",
            "Кресло-мешок с памятью формы",
            "Гирлянда с управлением со смартфона",
            "Электрический камин для уюта",
            "Набор ароматических свечей",
            "Термос с подогревом",
            "Электрическое одеяло",
            "Массажный коврик для ног",
            "Набор постельного белья с новогодним принтом",
            "Подставка для кружки с подогревом"
        ],
        "?? Гастрономия и вкусности": [
            "Набор крафтового шоколада от локальных производителей",
            "Подарочная корзина с сырами и мёдом",
            "Набор для приготовления сыра или йогурта",
            "Экзотические специи в красивой упаковка",
            "Коробка полезных снеков без сахара",
            "Набор для создания собственного чая",
            "Подарочный набор элитного кофе",
            "Набор для приготовления суши",
            "Корзина с фруктами премиум-класса",
            "Набор крафтового пива или сидра",
            "Подарочный сертификат в ресторан",
            "Набор для фондю",
            "Коробка с деликатесами"
        ],
        "?? Опыты и приключения": [
            "Сертификат на мастер-класс по кулинарии",
            "Билеты на квест в реальности новогодней тематики",
            "Подписка на онлайн-курс по хобби получателя",
            "Подарочный набор для пикника в зимнем стиле",
            "Сертификат в СПА или на массаж",
            "Билеты в кино или на концерт",
            "Сертификат на прыжок с парашютом",
            "Подарочная карта в книжный магазин",
            "Абонемент в фитнес-клуб",
            "Сертификат на фотосессию",
            "Билеты в театр или на выставку",
            "Подарочный сертификат на мастер-класс по гончарному делу"
        ],
        "?? Для особенных случаев": [
            "Персонализированный фотоальбом",
            "Именная звезда на небе",
            "Сертификат на полет на воздушном шаре",
            "Набор для кастомизации одежды",
            "Подарочная карта в магазин техники",
            "Экскурсия по местным достопримечательностям",
            "Набор для барбекю",
            "Подарочный сертификат на стрижку и укладку",
            "Набор для кемпинга",
            "Сертификат на катание на лошадях",
            "Подарочная корзина с косметикой",
            "Набор для йоги и медитации"
        ]
    }
    category = random.choice(list(CATEGORIES.keys()))
    gift = random.choice(CATEGORIES[category])
    budget_options = [
        "?? Бюджет до 2000?",
        "?? Средний бюджет 2000-5000?",
        "?? Премиум от 5000?",
        "?? Люкс от 10000?"
    ]
    budget_weights = [0.4, 0.35, 0.2, 0.05]
    budget = random.choices(budget_options, weights=budget_weights)[0]
    return f"{category}:\n{gift}\n{budget}"

# -------------------- Команды и обработчики --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    init_user_data(user.id)
    uid = str(user.id)
    user_data[uid]["name"] = user.full_name
    user_data[uid]["username"] = user.username or "без username"
    welcome_text = (
        f"?? Добро пожаловать, {user.first_name}! ??\n\n"
        "? <b>Правила Тайного Санты:</b>\n"
        "1. Создай или присоединись к комнате\n"
        "2. Напиши своё пожелание подарка\n"
        "3. Дождись запуска игры организатором\n"
        "4. Получи имя своего получателя и подари ему подарок!\n\n"
        "?? <b>Что можно делать в боте:</b>\n"
        "• Создавать комнаты и приглашать друзей\n"
        "• Писать пожелания подарков\n"
        "• Играть в новогодние мини-игры\n"
        "• Проходить квесты и получать достижения\n"
        "• Соревноваться с друзьями в рейтинге\n\n"
        "Выбери действие ниже ??\n"
    )
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # вызывается по callback
    await update.callback_query.answer()
    context.user_data["wish_mode"] = True
    wish_instructions = (
        "?? <b>Написание пожелания</b>\n\n"
        "? <b>Как это работает:</b>\n"
        "1. Напиши своё пожелание подарка в одном сообщении\n"
        "2. Будь конкретным, но оставляй пространство для фантазии\n"
        "3. Учитывай бюджет участников\n"
        "4. После запуска игры изменить пожелание будет нельзя!\n\n"
        "?? <b>Напиши своё пожелание ниже:</b>\n"
    )
    await update.callback_query.edit_message_text(
        wish_instructions,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user

    # Админская рассылка (если включена)
    if is_admin(update) and context.user_data.get("broadcast_mode"):
        await handle_broadcast_message(update, context)
        return

    # Обработка режима написания пожелания
    if context.user_data.get("wish_mode"):
        # Найдём комнату, где этот пользователь есть
        for code, room in data["rooms"].items():
            if str(user.id) in room["members"]:
                if room.get("game_started"):
                    await update.message.reply_text("?? Игра уже запущена! Менять пожелание нельзя.")
                    context.user_data["wish_mode"] = False
                    return
                room["members"][str(user.id)]["wish"] = update.message.text
                save_data(data)
                context.user_data["wish_mode"] = False
                add_reindeer_exp(user.id, 10)
                add_santa_points(user.id, 25, context)
                admin = is_admin(update)
                await update.message.reply_text(
                    "? Пожелание сохранено! +25 очков Санты! ??",
                    reply_markup=enhanced_menu_keyboard(admin)
                )
                return
        await update.message.reply_text("?? Ты ещё не в комнате! Используй кнопку 'Присоединиться к комнате'.")
        context.user_data["wish_mode"] = False
        return

    # Обработка режима присоединения к комнате
    if context.user_data.get("join_mode"):
        await join_room(update, context)
        return

    # Если текст похож на код комнаты
    text = update.message.text.strip()
    if len(text) == 6 and text.startswith('R'):
        context.user_data["join_mode"] = True
        await join_room(update, context)
        return

    # Если ничего не подошло - показываем меню
    admin = is_admin(update)
    await update.message.reply_text(
        "Выбери действие в меню:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------- Управление комнатами --------------------
async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Может вызываться как callback или команда
    caller = update.effective_user
    if not is_admin(update):
        if update.callback_query:
            await update.callback_query.answer("?? Только @BeellyKid может создавать комнаты!", show_alert=True)
        else:
            await update.message.reply_text("?? Только @BeellyKid может создавать комнаты.")
        return

    data = load_data()
    code = gen_room_code()
    data["rooms"][code] = {
        "creator": caller.id,
        "members": {},
        "game_started": False,
        "assign": {},
        "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    }
    save_data(data)
    admin = is_admin(update)
    bot_username = (await context.bot.get_me()).username
    success_text = (
        f"?? <b>Комната создана!</b>\n\n"
        f"<b>Код комнаты:</b> {code}\n"
        f"<b>Ссылка для приглашения:</b>\n"
        f"https://t.me/{bot_username}?start=join_{code}\n\n"
        f"Приглашай друзей! Они могут присоединиться через меню бота."
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(success_text, parse_mode='HTML', reply_markup=enhanced_menu_keyboard(admin))
    else:
        await update.message.reply_text(success_text, parse_mode='HTML', reply_markup=enhanced_menu_keyboard(admin))

async def join_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    join_instructions = (
        "?? <b>Присоединение к комнате</b>\n\n"
        "? <b>Как присоединиться:</b>\n"
        "1. Попроси у организатора код комнаты (формат: RXXXXX)\n"
        "2. Используй команду: /join_room RXXXXX\n"
        "3. Или просто напиши код комнаты в чат\n\n"
        "?? <b>Правила:</b>\n"
        "• Можно быть только в одной комнате\n"
        "• Присоединиться можно только до старта игры\n"
        "• Минимум 2 участника для запуска\n"
        "• Все участники должны написать пожелания\n\n"
        "?? <b>Напиши код комнаты ниже:</b>\n"
    )
    await update.callback_query.edit_message_text(join_instructions, parse_mode='HTML', reply_markup=back_to_menu_keyboard())
    context.user_data["join_mode"] = True

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user

    # Если вызвано командой /join_room
    code = None
    if update.message and update.message.text and update.message.text.startswith('/join_room'):
        # /join_room RXXXXX
        parts = update.message.text.split()
        code = parts[1].strip().upper() if len(parts) > 1 else None
    elif context.user_data.get("join_mode") and update.message:
        code = update.message.text.strip().upper()
        context.user_data["join_mode"] = False
    else:
        # Если callback или другое — ничего не делаем
        if update.callback_query and update.callback_query.data:
            # возможно передали код в callback_data (не используется сейчас)
            pass
        # Попытка взять текст как код
        if update.message and update.message.text:
            txt = update.message.text.strip().upper()
            if len(txt) == 6 and txt.startswith('R'):
                code = txt

    if not code:
        if update.message:
            await update.message.reply_text("Напиши: /join_room RXXXXX")
        elif update.callback_query:
            await update.callback_query.answer("Напиши: /join_room RXXXXX", show_alert=True)
        return

    if not code.startswith('R') or len(code) != 6:
        await update.message.reply_text("?? Неверный формат кода! Код должен быть в формате RXXXXX")
        return

    if code not in data["rooms"]:
        await update.message.reply_text("?? Такой комнаты нет. Проверь код или создай новую комнату.")
        return

    room = data["rooms"][code]
    if room.get("game_started"):
        await update.message.reply_text("?? Игра уже началась — вход закрыт!")
        return

    u = user
    if str(u.id) in room["members"]:
        await update.message.reply_text("?? Ты уже в этой комнате!")
        return

    # Проверка: пользователь не должен быть в другой комнате
    for c, r in data["rooms"].items():
        if str(u.id) in r["members"]:
            await update.message.reply_text(f"?? Ты уже в комнате {c}. Сначала покинь её.")
            return

    room["members"][str(u.id)] = {
        "name": u.full_name,
        "username": u.username or "без username",
        "wish": ""
    }
    save_data(data)
    add_reindeer_exp(u.id, 20)
    add_santa_points(u.id, 50, context)
    admin = is_admin(update)
    await update.message.reply_text(
        f"? <b>Ты присоединился к комнате! +50 очков Санты!</b> ??\n\n"
        f"<b>Код комнаты:</b> {code}\n"
        f"<b>Участников:</b> {len(room['members'])}\n\n"
        f"Теперь напиши своё пожелание подарка через меню! ??",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def show_room_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user

    # Найдём комнату, в которой находится пользователь
    user_room = None
    room_code = None
    for code, room in data["rooms"].items():
        if str(user.id) in room["members"]:
            user_room = room
            room_code = code
            break

    if not user_room:
        await update.callback_query.answer("Ты не в комнате!", show_alert=True)
        return

    members_text = f"?? <b>Участники комнаты {room_code}:</b>\n\n"
    for i, (user_id, member) in enumerate(user_room["members"].items(), 1):
        wish_status = "?" if member.get("wish") else "?"
        username = f"@{member['username']}" if member.get("username") != "без username" else "без username"
        members_text += f"{i}. {member.get('name')} ({username}) {wish_status}\n"

    members_text += f"\n<b>Всего участников:</b> {len(user_room['members'])}"
    await update.callback_query.edit_message_text(members_text, parse_mode='HTML', reply_markup=back_to_menu_keyboard())

# -------------------- Админ: запуск игры --------------------
async def start_game_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён.", show_alert=True)
        return

    data = load_data()
    # Список комнат, которые можно запустить
    keyboard = []
    for code, room in data["rooms"].items():
        if not room.get("game_started") and len(room.get("members", {})) >= 2:
            keyboard.append([InlineKeyboardButton(f"?? {code} ({len(room['members'])} участ.)", callback_data=f"start_{code}")])

    if not keyboard:
        await update.callback_query.edit_message_text(
            "?? Нет комнат для запуска! Нужны комнаты с минимум 2 участниками.",
            reply_markup=back_to_menu_keyboard(True)
        )
        return

    keyboard.append([InlineKeyboardButton("?? Назад", callback_data="back_menu")])
    await update.callback_query.edit_message_text(
        "?? <b>Запуск игры Тайный Санта</b>\n\nВыбери комнату для запуска:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_specific_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    code = q.data.replace("start_", "")
    data = load_data()
    if code not in data["rooms"]:
        await q.edit_message_text("?? Комната не найдена!")
        return

    room = data["rooms"][code]
    if room.get("game_started"):
        await q.edit_message_text("?? Игра уже запущена в этой комнате!")
        return

    members = list(room["members"].keys())
    if len(members) < 2:
        await q.edit_message_text("?? Нужно минимум 2 участника!")
        return

    # Проверяем, все ли написали пожелания
    members_without_wishes = []
    for uid, member in room["members"].items():
        if not member.get("wish"):
            members_without_wishes.append(member.get("name"))
    if members_without_wishes:
        await q.edit_message_text(
            f"?? <b>Не все участники написали пожелания:</b>\n"
            f"{', '.join(members_without_wishes)}\n\n"
            f"Попроси их написать пожелания через меню бота!",
            parse_mode='HTML'
        )
        return

    # Генерируем случайные назначения (секретный санта), избегая самоподарков
    uids = members[:]  # список строк user_id
    random.shuffle(uids)
    assigns = {}
    # Простая корректировка: если кто-то попал сам себе, меняем с соседем
    for i, uid in enumerate(uids):
        assigns[uid] = uids[(i + 1) % len(uids)]
    # Если есть самопары (в редких случаях), исправим
    for uid, target in list(assigns.items()):
        if uid == target:
            # поменяем с любым другим
            for other in assigns:
                if other != uid and assigns[other] != uid and other != assigns[uid]:
                    assigns[uid], assigns[other] = assigns[other], assigns[uid]
                    break

    room["assign"] = assigns
    room["game_started"] = True
    room["started_at"] = datetime.now(timezone.utc).isoformat()
    save_data(data)

    # Уведомляем участников в личку (если возможно)
    success_msg = f"?? Игра в комнате {code} запущена! Назначения разосланы в личные сообщения."
    await q.edit_message_text(success_msg, parse_mode='HTML')

    # Отправляем каждому участнику имя получателя и его пожелание
    for giver_id, receiver_id in assigns.items():
        try:
            giver_chat = int(giver_id)
            receiver = room["members"].get(receiver_id)
            if receiver:
                wish_text = receiver.get("wish", "Нет пожелания")
                name = receiver.get("name", "Аноним")
                await context.bot.send_message(
                    chat_id=giver_chat,
                    text=(
                        f"?? Тайный Санта — твоё задание:\n\n"
                        f"Ты даришь: <b>{name}</b>\n\n"
                        f"Пожелание получателя:\n{wish_text}\n\n"
                        f"{toast_of_day()}"
                    ),
                    parse_mode='HTML'
                )
        except Exception as e:
            print(f"Не удалось отправить сообщение {giver_id}: {e}")

# -------------------- Админ: рассылка --------------------
async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем текст рассылки в update.message
    if not update.message:
        return
    text = update.message.text
    data = load_data()
    count = 0
    for uid in data.get("users", {}):
        try:
            await context.bot.send_message(chat_id=int(uid), text=text)
            count += 1
        except Exception:
            pass
    context.user_data.pop("broadcast_mode", None)
    await update.message.reply_text(f"Рассылка отправлена примерно {count} пользователям.")

# -------------------- Callback router --------------------
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "back_menu":
        admin = is_admin(update)
        await q.edit_message_text("Меню:", reply_markup=enhanced_menu_keyboard(admin))
        return
    if data == "wish_start":
        await wish_start(update, context)
        return
    if data == "join_room_menu":
        await join_room_menu(update, context)
        return
    if data == "create_room":
        await create_room(update, context)
        return
    if data == "show_members":
        await show_room_members(update, context)
        return
    if data == "gift_idea":
        idea = generate_gift_idea()
        await q.edit_message_text(f"?? Идея подарка:\n\n{idea}", reply_markup=back_to_menu_keyboard())
        return
    if data == "admin_start_game":
        await start_game_admin(update, context)
        return
    if data.startswith("start_"):
        # запуск конкретной комнаты
        await start_specific_game(update, context)
        return
    if data == "admin_broadcast":
        if not is_admin(update):
            await q.answer("?? Доступ запрещён.", show_alert=True)
            return
        context.user_data["broadcast_mode"] = True
        await q.edit_message_text("?? Введи текст рассылки в чат. После отправки рассылка будет разослана всем пользователям.")
        return

    # Неизвестный callback
    await q.answer("Неизвестная команда.", show_alert=True)

# -------------------- Команды помощи --------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n"
        "/start — начать\n"
        "/join_room RXXXXX — присоединиться к комнате по коду\n"
        "Используй меню для остальных действий."
    )

# -------------------- Основная точка входа --------------------
def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("join_room", join_room))

    # CallbackQuery
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    # Текстовые сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Запуск
    print("Бот запущен. Ожидание сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()

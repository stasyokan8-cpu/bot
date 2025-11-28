# 🔥🎄 SUPER-DELUXE SECRET SANTA BOT v2.4 🎄🔥
# ПОЛНАЯ ВЕРСИЯ: исправленные мини-игры, инструкции, удаление комнат + Replit оптимизация

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

# Конфигурация для Replit
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8299215190:AAEqLfMOTjywx_jOeT-Kv1I5oKdgbdWzN9Y")
ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"

print(f"🎄 Запуск Secret Santa Bot v2.4 на Replit...")

user_data = {}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            global user_data
            user_data = data["users"]
            return data
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"rooms": {}, "users": {}}

def save_data(data):
    data["users"] = user_data
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

# -------------------------------------------------------------------
# БАЗОВЫЕ УТИЛИТЫ
# -------------------------------------------------------------------
def is_admin(update: Update):
    return update.effective_user.username == ADMIN_USERNAME

def gen_room_code():
    return "R" + "".join(random.choice(string.ascii_uppercase) for _ in range(5))

def back_to_menu_keyboard(admin=False):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")]
    ])

def toast_of_day():
    TOASTS = [
        "🎄 Пусть в новом году твой холодильник всегда будет полен, а будильник — сломан!",
        "✨ Желаю зарплаты как у Илон Маска, а забот — как у кота!",
        "🎁 Пусть удача прилипнет, как блёстки после корпоратива!",
        "❄️ Пусть счастье валит в дом, как снег в Сибири — неожиданно и много!",
        "🥂 Пусть каждый день нового года будет как первый день отпуска!",
        "🎅 Желаю, чтобы под ёлкой всегда находилось именно то, о чём мечталось!",
        "🌟 Пусть звёзды с неба достаются без особых усилий!",
        "🍪 Пусть печеньки всегда будут свежими, а настроение — отличным!",
        "🦌 Желаю, чтобы олени в жизни были только послушными!",
        "🎶 Пусть новогодние песни звучат только в радость!",
        "🍾 Желаю, чтобы шампанское било через край, а проблемы — мимо!",
        "🕯️ Пусть огоньки гирлянд освещают только счастливые моменты!",
        "❄️ Желаю морозных узоров на окнах и тепла в сердце!",
        "🎁 Пусть сюрпризы будут только приятными!",
        "🍬 Желаю сладкой жизни без горьких проблесков!",
        "🕰️ Пусть бой курантов приносит только хорошие новости!",
        "🎪 Желаю, чтобы жизнь была цирком, где ты — главный акробат!",
        "🧦 Пусть носки всегда парные, а мысли — ясные!",
        "🔥 Желаю, чтобы камин горел, а проблемы — нет!",
        "🎊 Пусть фейерверки эмоций затмят все печали!"
    ]
    return random.choice(TOASTS)

# -------------------------------------------------------------------
# СИСТЕМА ОЧКОВ И ОЛЕНЕЙ
# -------------------------------------------------------------------
def init_user_data(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
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
            "username": ""
        }

def add_santa_points(user_id, points, context: ContextTypes.DEFAULT_TYPE = None):
    init_user_data(user_id)
    user_data[str(user_id)]["santa_points"] += points
    user_data[str(user_id)]["total_points"] += points
    
    if context and abs(points) >= 50:
        try:
            context.bot.send_message(
                user_id,
                f"🎅 {'Получено' if points > 0 else 'Потеряно'} {abs(points)} очков Санты!"
            )
        except:
            pass

def add_reindeer_exp(user_id, amount):
    init_user_data(user_id)
    user_data[str(user_id)]["reindeer_exp"] += amount
    
    current_level = user_data[str(user_id)]["reindeer_level"]
    exp_needed = (current_level + 1) * 100
    
    if user_data[str(user_id)]["reindeer_exp"] >= exp_needed and current_level < 5:
        user_data[str(user_id)]["reindeer_level"] += 1
        user_data[str(user_id)]["reindeer_exp"] = 0
        
        new_skin = None
        evolution_chance = random.random()
        
        if current_level + 1 == 3:
            if evolution_chance < 0.1:
                new_skin = "rainbow"
            elif evolution_chance < 0.02:
                new_skin = "ice_spirit"
        elif current_level + 1 == 4:
            if evolution_chance < 0.08:
                new_skin = "golden"
            elif evolution_chance < 0.015:
                new_skin = "crystal"
        elif current_level + 1 == 5:
            if evolution_chance < 0.05:
                new_skin = "cosmic"
            elif evolution_chance < 0.01:
                new_skin = "phantom"
        
        if new_skin:
            user_data[str(user_id)]["reindeer_skin"] = new_skin
            user_data[str(user_id)]["unlocked_reindeers"].append(new_skin)
            add_achievement(user_id, f"{new_skin}_reindeer")
        
        if current_level + 1 == 5:
            add_achievement(user_id, "reindeer_master")

def add_achievement(user_id, achievement_key):
    init_user_data(user_id)
    if achievement_key not in user_data[str(user_id)]["achievements"]:
        user_data[str(user_id)]["achievements"].append(achievement_key)
        add_santa_points(user_id, 50)

# -------------------------------------------------------------------
# 🎁 РАЗДЕЛ: ГЕНЕРАТОР ИДЕЙ ПОДАРКОВ
# -------------------------------------------------------------------
def generate_gift_idea():
    CATEGORIES = {
        "💻 Техника": [
            "Умная колонка с голосовым помощником",
            "Беспроводные наушники с шумоподавлением", 
            "Портативное зарядное устройство 10000 mAh",
            "Электронная книга с подсветкой",
            "Умные часы с отслеживанием активности",
            "Игровая консоль портативная",
            "Bluetooth-колонка водонепроницаемая"
        ],
        "🎨 Творчество": [
            "Набор для рисования светом",
            "Конструктор для взрослых с мелкими деталями",
            "Набор для создания свечей ручной работы",
            "Алмазная вышивка с новогодним сюжетом",
            "Гончарный набор миниатюрный",
            "Набор для каллиграфии"
        ],
        "🏠 Уют": [
            "Плед с подогревом и таймером",
            "Аромадиффузер с эфирными маслами",
            "Набор чайных пар с новогодним дизайном",
            "Проектор звёздного неба для комнаты",
            "Кресло-мешок с памятью формы",
            "Гирлянда с управлением со смартфона"
        ],
        "🍫 Гастрономия": [
            "Набор крафтового шоколада от локальных производителей",
            "Подарочная корзина с сырами и мёдом",
            "Набор для приготовления сыра или йогурта",
            "Экзотические специи в красивой упаковке",
            "Коробка полезных снеков без сахара",
            "Набор для создания собственного чая"
        ],
        "🎪 Опыты": [
            "Сертификат на мастер-класс по кулинарии",
            "Билеты на квест в реальности новогодней тематики",
            "Подписка на онлайн-курс по хобби получателя",
            "Подарочный набор для пикника в зимнем стиле",
            "Сертификат в СПА или на массаж"
        ]
    }
    
    category = random.choice(list(CATEGORIES.keys()))
    gift = random.choice(CATEGORIES[category])
    budget = random.choice(["💰 Бюджет до 2000₽", "💸 Средний бюджет 2000-5000₽", "🎁 Премиум от 5000₽"])
    
    return f"{category}:\n{gift}\n{budget}"

# -------------------------------------------------------------------
# 🎮 РАЗДЕЛ: ОСНОВНЫЕ КОМАНДЫ И ИНТЕРФЕЙС
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    init_user_data(user.id)
    
    # Сохраняем данные пользователя
    user_data[str(user.id)]["name"] = user.full_name
    user_data[str(user.id)]["username"] = user.username or "без username"
    
    welcome_text = f"""
🎄 Добро пожаловать, {user.first_name}! 🎅

✨ <b>Правила Тайного Санты:</b>
1. Создай или присоединись к комнате
2. Напиши своё пожелание подарка
3. Дождись запуска игры организатором
4. Получи имя своего получателя и подари ему подарок!

🎁 <b>Что можно делать в боте:</b>
• Создавать комнаты и приглашать друзей
• Писать пожелания подарков
• Играть в новогодние мини-игры
• Проходить квесты и получать достижения
• Соревноваться с друзьями в рейтинге

Выбери действие ниже 👇
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["wish_mode"] = True
    
    wish_instructions = """
🎁 <b>Написание пожелания</b>

✨ <b>Как это работает:</b>
1. Напиши своё пожелание подарка в одном сообщении
2. Будь конкретным, но оставляй пространство для фантазии
3. Учитывай бюджет участников
4. После запуска игры изменить пожелание будет нельзя!

💡 <b>Примеры хороших пожеланий:</b>
• "Люблю читать, хотел бы интересную книгу"
• "Нужен тёплый плед для холодных вечеров"
• "Хочу сюрприз - угадайте мои интересы!"

📝 <b>Напиши своё пожелание ниже:</b>
"""
    
    await update.callback_query.edit_message_text(
        wish_instructions,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
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
                add_santa_points(user.id, 25, context)
                
                admin = is_admin(update)
                await update.message.reply_text(
                    "✨ Пожелание сохранено! +25 очков Санты! 🎄",
                    reply_markup=enhanced_menu_keyboard(admin)
                )
                return
        await update.message.reply_text("❄️ Ты ещё не в комнате! Используй кнопку 'Присоединиться к комнате'.")
        return

# -------------------------------------------------------------------
# 🏠 РАЗДЕЛ: УПРАВЛЕНИЕ КОМНАТАМИ
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

    admin = is_admin(update)
    await update.message.reply_text(
        f"🎄 <b>Комната создана!</b>\n\n"
        f"<b>Код комнаты:</b> {code}\n"
        f"<b>Ссылка для приглашения:</b>\n"
        f"https://t.me/{(await context.bot.get_me()).username}?start=join_{code}\n\n"
        f"Приглашай друзей! Они могут присоединиться через меню бота.",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def join_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    join_instructions = """
🎅 <b>Присоединение к комнате</b>

✨ <b>Как присоединиться:</b>
1. Попроси у организатора код комнаты (формат: RXXXXX)
2. Используй команду: /join_room RXXXXX
3. Или просто напиши код комнаты в чат

🔑 <b>Правила:</b>
• Можно быть только в одной комнате
• Присоединиться можно только до старта игры
• Минимум 2 участника для запуска
• Все участники должны написать пожелания

📝 <b>Напиши код комнаты ниже:</b>
"""
    
    await update.callback_query.edit_message_text(
        join_instructions,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
    )
    context.user_data["join_mode"] = True

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user
    
    # Обработка команды /join_room
    if update.message and update.message.text.startswith('/join_room'):
        code = "".join(context.args).strip().upper() if context.args else None
    # Обработка текстового сообщения с кодом
    elif context.user_data.get("join_mode"):
        code = update.message.text.strip().upper()
        context.user_data["join_mode"] = False
    else:
        # Если это просто текст, проверяем, не код ли комнаты
        if update.message and len(update.message.text.strip()) == 6 and update.message.text.strip().startswith('R'):
            code = update.message.text.strip().upper()
        else:
            return

    if not code:
        await update.message.reply_text("Напиши: /join_room RXXXXX")
        return
        
    if not code.startswith('R') or len(code) != 6:
        await update.message.reply_text("🚫 Неверный формат кода! Код должен быть в формате RXXXXX")
        return
        
    if code not in data["rooms"]:
        await update.message.reply_text("🚫 Такой комнаты нет. Проверь код или создай новую комнату.")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("🚫 Игра уже началась — вход закрыт!")
        return

    u = update.effective_user
    if str(u.id) in room["members"]:
        await update.message.reply_text("❄️ Ты уже в этой комнате!")
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
        f"✨ <b>Ты присоединился к комнате! +50 очков Санты!</b> 🎄\n\n"
        f"<b>Код комнаты:</b> {code}\n"
        f"<b>Участников:</b> {len(room['members'])}\n\n"
        f"Теперь напиши своё пожелание подарка через меню! 🎁",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def show_room_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user
    
    # Найдем комнату, в которой находится пользователь
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
    
    members_text = f"👥 <b>Участники комнаты {room_code}:</b>\n\n"
    for i, (user_id, member) in enumerate(user_room["members"].items(), 1):
        wish_status = "✅" if member["wish"] else "❌"
        username = f"@{member['username']}" if member["username"] != "без username" else "без username"
        members_text += f"{i}. {member['name']} ({username}) {wish_status}\n"
    
    members_text += f"\n<b>Всего участников:</b> {len(user_room['members'])}"
    
    await update.callback_query.edit_message_text(
        members_text,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
    )

# -------------------------------------------------------------------
# ⚙️ РАЗДЕЛ: АДМИН-ПАНЕЛЬ
# -------------------------------------------------------------------
async def start_game_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён.", show_alert=True)
        return

    data = load_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "🚫 Нет созданных комнат!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return

    # Показываем список комнат для запуска
    keyboard = []
    for code, room in data["rooms"].items():
        if not room["game_started"] and len(room["members"]) >= 2:
            keyboard.append([InlineKeyboardButton(f"🎄 {code} ({len(room['members'])} участ.)", callback_data=f"start_{code}")])
    
    if not keyboard:
        await update.callback_query.edit_message_text(
            "🚫 Нет комнат для запуска! Нужны комнаты с минимум 2 участниками.",
            reply_markup=back_to_menu_keyboard(True)
        )
        return
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "🚀 <b>Запуск игры Тайный Санта</b>\n\n"
        "Выбери комнату для запуска:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_specific_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    code = q.data.replace("start_", "")
    data = load_data()
    
    if code not in data["rooms"]:
        await q.edit_message_text("🚫 Комната не найдена!")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await q.edit_message_text("❄️ Игра уже запущена в этой комнате!")
        return

    members = list(room["members"].keys())
    if len(members) < 2:
        await q.edit_message_text("🚫 Нужно минимум 2 участника!")
        return
        
    # Проверяем, все ли написали пожелания
    members_without_wishes = []
    for uid, member in room["members"].items():
        if not member["wish"]:
            members_without_wishes.append(member["name"])
    
    if members_without_wishes:
        await q.edit_message_text(
            f"🚫 <b>Не все участники написали пожелания:</b>\n"
            f"{', '.join(members_without_wishes)}\n\n"
            f"Попроси их написать пожелания через меню бота!",
            parse_mode='HTML'
        )
        return
        
    random.shuffle(members)
    assigns = {}
    for i, uid in enumerate(members):
        assigns[uid] = members[(i + 1) % len(members)]

    room["assign"] = assigns
    room["game_started"] = True
    save_data(data)

    # Рассылка участникам
    successful_sends = 0
    for giver, receiver in assigns.items():
        m = room["members"][str(receiver)]
        try:
            await context.bot.send_message(
                giver,
                f"🎁 <b>Тайный Санта запущен!</b> 🎄\n\n"
                f"<b>Твой получатель:</b> {m['name']} (@{m['username']})\n\n"
                f"✨ <b>Его пожелание:</b> {m['wish']}\n\n"
                f"Удачи в выборе подарка! 🎅",
                parse_mode='HTML'
            )
            successful_sends += 1
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {giver}: {e}")

    admin = is_admin(update)
    await q.edit_message_text(
        f"🎄 <b>Игра запущена в комнате {code}!</b> ✨\n\n"
        f"<b>Участников:</b> {len(members)}\n"
        f"<b>Сообщений отправлено:</b> {successful_sends}/{len(members)}\n\n"
        f"Все участники получили своих получателей! 🎁",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def delete_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён.", show_alert=True)
        return

    data = load_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "🚫 Нет созданных комнат для удаления!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return

    keyboard = []
    for code, room in data["rooms"].items():
        status = "✅ Запущена" if room["game_started"] else "⏳ Ожидание"
        keyboard.append([InlineKeyboardButton(
            f"🗑️ {code} ({len(room['members'])} участ.) - {status}", 
            callback_data=f"delete_{code}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "🗑️ <b>Удаление комнат</b>\n\n"
        "Выбери комнату для удаления:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def delete_specific_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    code = q.data.replace("delete_", "")
    data = load_data()
    
    if code not in data["rooms"]:
        await q.edit_message_text("🚫 Комната не найдена!")
        return

    # Удаляем комнату
    room_info = data["rooms"][code]
    del data["rooms"][code]
    save_data(data)
    
    admin = is_admin(update)
    await q.edit_message_text(
        f"🗑️ <b>Комната {code} удалена!</b>\n\n"
        f"<b>Было участников:</b> {len(room_info['members'])}\n"
        f"<b>Статус игры:</b> {'Запущена' if room_info['game_started'] else 'Не запущена'}\n\n"
        f"Все данные комнаты безвозвратно удалены.",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# 🎮 РАЗДЕЛ: МИНИ-ИГРЫ (ИСПРАВЛЕННЫЕ)
# -------------------------------------------------------------------
async def mini_game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    games_info = """
🎮 <b>Новогодние мини-игры</b>

✨ <b>Доступные игры:</b>

🎯 <b>Угадай число</b> - Угадай число от 1 до 5
• Победа: 25-50 очков
• Поражение: -10-20 очков

🧊 <b>Монетка судьбы</b> - Орёл или решка?
• Орёл: +15-30 очков
• Решка: -5-15 очков
• Серия побед даёт достижение!

⚔️ <b>Битва с Гринчем</b> - Эпичная RPG-битва
• Победа: 80-150 очков + опыт
• Поражение: -30-60 очков
• 3 победы - достижение!

🎓 <b>Новогодний квиз</b> - Проверь знания
• 5 случайных вопросов
• До 150 очков за идеальный результат
• Интересные факты!

♟️ <b>Шашки</b> - Игра с друзьями
• Интеграция с @goplaybot
• Победа: 80-120 очков
• Поражение: -20-40 очков

Выбери игру:
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Угадай число", callback_data="game_number")],
        [InlineKeyboardButton("🧊 Монетка судьбы", callback_data="game_coin")],
        [InlineKeyboardButton("⚔️ Битва с Гринчем", callback_data="game_grinch")],
        [InlineKeyboardButton("🎓 Новогодний квиз", callback_data="game_quiz")],
        [InlineKeyboardButton("♟️ Шашки", callback_data="game_checkers")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")],
    ])
    await update.callback_query.edit_message_text(games_info, parse_mode='HTML', reply_markup=kb)

# 🎯 Игра: Угадай число
async def game_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    num = random.randint(1, 5)
    context.user_data["guess_num"] = num
    
    game_rules = """
🎯 <b>Угадай число</b>

✨ <b>Правила:</b>
• Я загадал число от 1 до 5
• У тебя одна попытка
• За правильный ответ: 25-50 очков
• За ошибку: -10-20 очков

Выбери число:
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1,6)],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# 🧊 Игра: Монетка судьбы
async def game_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    game_rules = """
🧊 <b>Монетка судьбы</b>

✨ <b>Правила:</b>
• Подбрасываю монетку - Орёл или Решка?
• Орёл: +15-30 очков
• Решка: -5-15 очков
• 5 побед подряд - достижение "Монетка Удачи"!

Нажимай "Подбросить монетку" 👇
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🪙 Подбросить монетку", callback_data="coin_flip")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# ⚔️ Игра: Битва с Гринчем
async def game_grinch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    game_rules = """
⚔️ <b>Битва с Гринчем</b>

✨ <b>Правила битвы:</b>
• У тебя 100 HP, у Гринча 120 HP
• 4 типа действий: атака, защита, магия, побег
• Магия лечит тебя и вредит Гринчу (3 заряда)
• Побег имеет 30% шанс успеха

🎁 <b>Награды:</b>
• Победа: 80-150 очков + 40 опыта
• Поражение: -30-60 очков
• 3 победы - достижение "Гроза Гринча"!

Готов сразиться? 🎅
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Начать битву!", callback_data="battle_start")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# 🎓 Игра: Новогодний квиз
async def game_quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    game_rules = """
🎓 <b>Новогодний квиз</b>

✨ <b>Правила:</b>
• 5 случайных вопросов о Новом годе
• За каждый правильный ответ +1 балл
• После вопроса - интересный факт!

🏆 <b>Награды:</b>
• 5/5: 150 очков + достижение
• 4/5: 100 очков
• 3/5: 60 очков
• 2/5 и меньше: 30 очков

Проверь свои знания! 🎄
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎄 Начать квиз!", callback_data="quiz_start")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# ♟️ Игра: Шашки
async def game_checkers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    game_rules = """
♟️ <b>Шашки с друзьями</b>

✨ <b>Как играть:</b>
1. Напиши @goplaybot в любом чате
2. Выбери "Checkers" (Шашки)
3. Пригласи друга из комнаты
4. После игры подтверди результат

📊 <b>Система очков:</b>
• Победа: 80-120 очков + 25 опыта
• Поражение: -20-40 очков
• Оба игрока получают уведомление

🎯 <b>Для подтверждения результата:</b>
Используй кнопки ниже или команды:
/report_win @username - после победы
/report_loss @username - после поражения
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Начать игру в шашки", url="https://t.me/goplaybot?start=checkers")],
        [InlineKeyboardButton("✅ Я победил", callback_data="confirm_win_menu")],
        [InlineKeyboardButton("❌ Я проиграл", callback_data="confirm_loss_menu")],
        [InlineKeyboardButton("📊 Статистика шашек", callback_data="checkers_stats")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=keyboard)

# -------------------------------------------------------------------
# 🎮 ОБРАБОТЧИКИ МИНИ-ИГР
# -------------------------------------------------------------------
async def game_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "game_number":
        await game_number_handler(update, context)
        
    elif q.data == "game_coin":
        await game_coin_handler(update, context)
        
    elif q.data == "game_grinch":
        await game_grinch_handler(update, context)
        
    elif q.data == "game_quiz":
        await game_quiz_handler(update, context)
        
    elif q.data == "game_checkers":
        await game_checkers_handler(update, context)
        
    elif q.data == "coin_flip":
        await coin_flip_handler(update, context)
        
    elif q.data == "battle_start":
        await epic_grinch_battle(update, context)
        
    elif q.data == "quiz_start":
        await start_quiz(update, context)

# Обработчик монетки
async def coin_flip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    side = random.choice(["Орёл 🦅", "Решка ❄️"])
    user = update.effective_user
    init_user_data(user.id)
    
    if "coin_wins" not in context.user_data:
        context.user_data["coin_wins"] = 0
        
    if side == "Орёл 🦅":
        context.user_data["coin_wins"] += 1
        points = random.randint(15, 30)
        add_santa_points(user.id, points, context)
        
        if context.user_data["coin_wins"] >= 5:
            add_achievement(user.id, "lucky_coin")
            result_text = f"🧊 Монетка: {side}! +{points} очков\n\n🎉 5 побед подряд! Достижение 'Монетка Удачи'!"
            context.user_data["coin_wins"] = 0
        else:
            result_text = f"🧊 Монетка: {side}! +{points} очков\nСерия побед: {context.user_data['coin_wins']}"
    else:
        points_lost = random.randint(5, 15)
        add_santa_points(user.id, -points_lost, context)
        context.user_data["coin_wins"] = 0
        result_text = f"🧊 Монетка: {side}! Потеряно {points_lost} очков"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Ещё раз", callback_data="game_coin")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(result_text, reply_markup=kb)

# Обработчик угадывания чисел
async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    guess = int(q.data.split("_")[1])
    real = context.user_data.get("guess_num")
    user = update.effective_user
    init_user_data(user.id)
    
    if guess == real:
        points = random.randint(25, 50)
        add_santa_points(user.id, points, context)
        user_data[str(user.id)]["games_won"] += 1
        add_reindeer_exp(user.id, 15)
        result_text = f"🎉 Верно! Было число {real}. Получено {points} очков Санты!"
    else:
        points_lost = random.randint(10, 20)
        add_santa_points(user.id, -points_lost, context)
        result_text = f"❄️ Не угадал! Было число {real}. Потеряно {points_lost} очков."
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Играть снова", callback_data="game_number")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(result_text, reply_markup=kb)

# -------------------------------------------------------------------
# ⚔️ ЭПИЧНАЯ БИТВА С ГРИНЧЕМ
# -------------------------------------------------------------------
async def epic_grinch_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    user_data[str(user.id)]["grinch_fights"] += 1
    
    # Система характеристик
    player_stats = {
        "hp": 100,
        "attack": random.randint(15, 25),
        "defense": random.randint(5, 15),
        "special_charges": 3
    }
    
    grinch_stats = {
        "hp": 120,
        "attack": random.randint(18, 28),
        "defense": random.randint(8, 18),
        "special_used": False
    }
    
    context.user_data["battle_state"] = {
        "player": player_stats,
        "grinch": grinch_stats,
        "round": 1
    }
    
    await show_battle_interface(update, context)

async def show_battle_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    battle_state = context.user_data["battle_state"]
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    battle_text = f"""
⚔️ <b>ЭПИЧНАЯ БИТВА С ГРИНЧЕМ - Раунд {battle_state['round']}</b>

❤️ <b>Твоё HP:</b> {player['hp']} ⚡ <b>Атака:</b> {player['attack']} 🛡 <b>Защита:</b> {player['defense']}
💚 <b>HP Гринча:</b> {grinch['hp']} ⚡ <b>Атака:</b> {grinch['attack']} 🛡 <b>Защита:</b> {grinch['defense']}

✨ <b>Особые умения:</b> {player['special_charges']} зарядов

Выбери действие:
"""
    
    keyboard = [
        [InlineKeyboardButton("⚔️ Атаковать", callback_data="battle_attack")],
        [InlineKeyboardButton("🛡 Укрепить защиту", callback_data="battle_defend")],
        [InlineKeyboardButton("✨ Новогоднее волшебство", callback_data="battle_special")],
        [InlineKeyboardButton("🏃 Сбежать", callback_data="battle_flee")]
    ]
    
    await update.callback_query.edit_message_text(battle_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    action = q.data.replace("battle_", "")
    battle_state = context.user_data["battle_state"]
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    battle_log = []
    
    # Ход игрока
    if action == "attack":
        damage = max(0, player["attack"] - grinch["defense"] // 2)
        grinch["hp"] -= damage
        battle_log.append(f"🎅 Ты атаковал и нанёс {damage} урона!")
        
    elif action == "defend":
        player["defense"] += 10
        battle_log.append("🛡 Ты укрепил защиту! +10 к защите")
        
    elif action == "special" and player["special_charges"] > 0:
        player["special_charges"] -= 1
        heal = random.randint(20, 35)
        player["hp"] = min(100, player["hp"] + heal)
        grinch["hp"] -= 15
        battle_log.append(f"✨ Новогоднее волшебство! Исцеление +{heal}, Гринч получает 15 урона!")
        
    elif action == "flee":
        flee_chance = random.random()
        if flee_chance > 0.7:  # 30% шанс сбежать
            await q.edit_message_text("🏃 Ты успешно сбежал от Гринча!", reply_markup=back_to_menu_keyboard())
            add_santa_points(update.effective_user.id, -20, context)
            return
        else:
            battle_log.append("🏃 Попытка сбежать провалилась! Гринч блокирует escape!")
    
    # Проверка победы
    if grinch["hp"] <= 0:
        await battle_victory(update, context, battle_log)
        return
    
    # Ход Гринча
    grinch_actions = ["attack", "attack", "special", "defend"]
    grinch_action = random.choice(grinch_actions)
    
    if grinch_action == "attack":
        damage = max(0, grinch["attack"] - player["defense"] // 2)
        player["hp"] -= damage
        battle_log.append(f"🎄 Гринч атаковал и нанёс {damage} урона!")
        
    elif grinch_action == "defend":
        grinch["defense"] += 8
        battle_log.append("🛡 Гринч укрепил защиту!")
        
    elif grinch_action == "special" and not grinch["special_used"]:
        grinch["special_used"] = True
        player["hp"] -= 25
        battle_log.append("💥 Гринч использует 'Крадущийся праздник'! -25 HP!")
    
    # Проверка поражения
    if player["hp"] <= 0:
        await battle_defeat(update, context, battle_log)
        return
    
    battle_state["round"] += 1
    
    # Показываем результат раунда
    result_text = f"⚔️ Раунд {battle_state['round']-1}:\n" + "\n".join(battle_log) + f"\n\n❤️ Твоё HP: {player['hp']}\n💚 HP Гринча: {grinch['hp']}"
    
    keyboard = [
        [InlineKeyboardButton("➡️ Следующий раунд", callback_data="battle_continue")],
        [InlineKeyboardButton("🏃 Сбежать", callback_data="battle_flee")]
    ]
    
    await q.edit_message_text(result_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_battle_interface(update, context)

async def battle_victory(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_log):
    user = update.effective_user
    user_data[str(user.id)]["grinch_wins"] += 1
    user_data[str(user.id)]["games_won"] += 1
    
    points_earned = random.randint(80, 150)
    add_santa_points(user.id, points_earned, context)
    add_reindeer_exp(user.id, 40)
    
    if user_data[str(user.id)]["grinch_wins"] >= 3:
        add_achievement(user.id, "grinch_slayer")
    
    victory_text = f"""
🎉 <b>ПОБЕДА НАД ГРИНЧЕМ!</b> 🎉

{' '.join(battle_log)}

✨ <b>Награды:</b>
• +{points_earned} очков Санты
• +40 опыта оленёнку
• Звание Защитника Рождества!

Гринч повержен, и Новый Год спасён! 🎄
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Сразиться снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(victory_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_defeat(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_log):
    user = update.effective_user
    points_lost = random.randint(30, 60)
    add_santa_points(user.id, -points_lost, context)
    
    defeat_text = f"""
💔 <b>ПОРАЖЕНИЕ...</b>

{' '.join(battle_log)}

😔 <b>Потеряно:</b> {points_lost} очков Санты

Не сдавайся! Гринч должен быть остановлен! 🎅
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Попробовать снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(defeat_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# -------------------------------------------------------------------
# 🎓 НОВОГОДНИЙ КВИЗ
# -------------------------------------------------------------------
NEW_YEAR_QUIZ = [
    {
        "question": "🎄 В какой стране начали наряжать ёлку на Новый год?",
        "options": ["🇩🇪 Германия", "🇷🇺 Россия", "🇺🇸 США", "🇫🇷 Франция"],
        "correct": 0,
        "fact": "Традиция наряжать ёлку зародилась в Германии в XVI веке!"
    },
    {
        "question": "⭐ Сколько лучей у снежинки?",
        "options": ["4", "6", "8", "10"],
        "correct": 1,
        "fact": "Правильно! У снежинки всегда 6 лучей из-за кристаллической структуры льда."
    },
    {
        "question": "🎅 Как зовут оленя с красным носом?",
        "options": ["Рудольф", "Дашер", "Дансер", "Комет"],
        "correct": 0,
        "fact": "Рудольф — самый известный олень Санты с красным светящимся носом!"
    },
    {
        "question": "🕛 Во сколько бьют куранты в новогоднюю ночь?",
        "options": ["23:55", "00:00", "00:05", "00:10"],
        "correct": 1,
        "fact": "Куранты бьют ровно в полночь, символизируя наступление Нового года!"
    },
    {
        "question": "🍪 Кто обычно оставляет подарки под ёлкой в России?",
        "options": ["Санта Клаус", "Дед Мороз", "Снегурочка", "Йоулупукки"],
        "correct": 1,
        "fact": "В России подарки под ёлкой оставляет Дед Мороз со своей внучкой Снегурочкой!"
    },
    {
        "question": "🌟 Какой цвет традиционно считается новогодним?",
        "options": ["Красный", "Зелёный", "Золотой", "Все варианты"],
        "correct": 3,
        "fact": "Все три цвета — красный, зелёный и золотой — считаются традиционными новогодними!"
    },
    {
        "question": "🎁 Что принято делать под бой курантов?",
        "options": ["Загадывать желание", "Обниматься", "Кричать 'Ура!'", "Все варианты"],
        "correct": 3,
        "fact": "Под бой курантов принято загадывать желание, обниматься и кричать 'Ура!'"
    },
    {
        "question": "🦌 Сколько оленей в упряжке Санта Клауса?",
        "options": ["8", "9", "10", "12"],
        "correct": 1,
        "fact": "У Санты 9 оленей: Дашер, Дэнсер, Прэнсер, Виксен, Комет, Кьюпид, Дондер, Блитцен и Рудольф!"
    },
    {
        "question": "❄️ Какой самый популярный новогодний фильм?",
        "options": ["Один дома", "Один дома 2", "Этажом выше", "Красотка"],
        "correct": 0,
        "fact": "'Один дома' — самый популярный новогодний фильм всех времён!"
    },
    {
        "question": "🍾 Что традиционно пьют в новогоднюю ночь?",
        "options": ["Шампанское", "Водку", "Сок", "Все варианты"],
        "correct": 3,
        "fact": "В разных странах и семьях традиции разные, но шампанское — самый популярный напиток!"
    }
]

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    context.user_data["quiz"] = {
        "score": 0,
        "current_question": 0,
        "questions": random.sample(NEW_YEAR_QUIZ, 5)  # 5 случайных вопросов
    }
    
    await ask_quiz_question(update, context)

async def ask_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz_data = context.user_data["quiz"]
    current_q = quiz_data["current_question"]
    
    if current_q >= len(quiz_data["questions"]):
        await finish_quiz(update, context)
        return
    
    question_data = quiz_data["questions"][current_q]
    
    keyboard = []
    for i, option in enumerate(question_data["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"quiz_answer_{i}")])
    
    progress = f"({current_q + 1}/{len(quiz_data['questions'])})"
    
    await update.callback_query.edit_message_text(
        f"🎓 <b>Новогодний Квиз {progress}</b>\n\n"
        f"❓ {question_data['question']}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user_answer = int(q.data.split("_")[2])
    quiz_data = context.user_data["quiz"]
    current_q = quiz_data["current_question"]
    question_data = quiz_data["questions"][current_q]
    
    is_correct = user_answer == question_data["correct"]
    
    if is_correct:
        quiz_data["score"] += 1
        result_text = "✅ <b>Правильно!</b>"
    else:
        correct_answer = question_data["options"][question_data["correct"]]
        result_text = f"❌ <b>Неправильно!</b> Правильный ответ: {correct_answer}"
    
    # Показываем факт
    result_text += f"\n\n💡 {question_data['fact']}"
    
    # Кнопка для продолжения
    keyboard = [[InlineKeyboardButton("➡️ Следующий вопрос", callback_data="quiz_next")]]
    
    await q.edit_message_text(
        result_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz_next_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    context.user_data["quiz"]["current_question"] += 1
    await ask_quiz_question(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz_data = context.user_data["quiz"]
    score = quiz_data["score"]
    total = len(quiz_data["questions"])
    
    user = update.effective_user
    init_user_data(user.id)
    
    # Начисление очков в зависимости от результата
    if score == total:  # Все правильно
        points = 150
        add_achievement(user.id, "quiz_master")
        result_message = "🎉 <b>ИДЕАЛЬНО! Ты настоящий новогодний эксперт!</b>"
    elif score >= total * 0.7:  # Больше 70%
        points = 100
        result_message = "🎊 <b>Отличный результат! Ты хорошо знаешь новогодние традиции!</b>"
    elif score >= total * 0.5:  # Больше 50%
        points = 60
        result_message = "👍 <b>Хороший результат! Есть что вспомнить о Новом годе!</b>"
    else:
        points = 30
        result_message = "📚 <b>Неплохо! Новогодние традиции — это интересно!</b>"
    
    add_santa_points(user.id, points, context)
    add_reindeer_exp(user.id, score * 10)
    user_data[str(user.id)]["games_won"] += 1
    user_data[str(user.id)]["quiz_wins"] = user_data[str(user.id)].get("quiz_wins", 0) + 1
    
    final_text = f"""
🎓 <b>Новогодний Квиз завершён!</b>

{result_message}

📊 <b>Твой результат:</b> {score}/{total}
✨ <b>Получено очков:</b> {points}
🦌 <b>Опыта оленёнку:</b> {score * 10}

Хочешь попробовать ещё раз?
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="game_quiz")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        final_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------------------------------------------------------------------
# 📊 РАЗДЕЛ: ПРОФИЛЬ И СТАТИСТИКА
# -------------------------------------------------------------------
async def enhanced_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    init_user_data(user.id)
    
    user_info = user_data[str(user.id)]
    
    # Информация об оленях
    reindeer_level = user_info["reindeer_level"]
    reindeer_exp = user_info["reindeer_exp"]
    current_skin = user_info["reindeer_skin"]
    
    REINDEER_STAGES = [
        "🦌 Новорождённый оленёнок (0 ур.)",
        "🦌💨 Оленёк-исследователь (1 ур.)", 
        "🦌✨ Сверкающий олень (2 ур.)",
        "🦌🌟 Звёздный олень (3 ур.)",
        "🦌🔥 Легендарный олень (4 ур.)",
        "🦌💫 Божественный олень (5 ур.)"
    ]
    
    reindeer_text = REINDEER_STAGES[reindeer_level] if reindeer_level < len(REINDEER_STAGES) else REINDEER_STAGES[-1]
    
    # Информация о скинах
    skin_display = {
        "default": "🦌 Обычный",
        "rainbow": "🌈 Радужный", 
        "ice_spirit": "❄️ Ледяной дух",
        "golden": "🌟 Золотой",
        "crystal": "💎 Хрустальный",
        "cosmic": "🌌 Космический",
        "phantom": "👻 Фантомный"
    }
    
    skin_text = skin_display.get(current_skin, "🦌 Обычный")
    
    profile_text = f"""
🎅 <b>Профиль игрока</b> @{user.username if user.username else user.first_name}

💫 <b>Очки Санты:</b> {user_info['santa_points']}
🦌 <b>Твой олень:</b> {reindeer_text}
🎨 <b>Вид:</b> {skin_text}
📊 <b>Опыт:</b> {reindeer_exp}/{(reindeer_level + 1) * 100}

🎖 <b>Достижения:</b> {len(user_info['achievements'])}
🎮 <b>Побед в играх:</b> {user_info['games_won']}
🏔 <b>Пройдено квестов:</b> {user_info['quests_finished']}
⚔️ <b>Побед над Гринчем:</b> {user_info['grinch_wins']}

💎 <b>Редких предметов:</b> {len(user_info['rare_items'])}
♟️ <b>Побед в шашках:</b> {user_info.get('checkers_wins', 0)}
🎓 <b>Побед в квизе:</b> {user_info.get('quiz_wins', 0)}
"""

    if update.callback_query:
        await update.callback_query.edit_message_text(
            profile_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            profile_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )

async def show_top_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Собираем статистику всех пользователей
    player_stats = []
    
    for user_id, data in user_data.items():
        score = data.get("total_points", 0)
        player_stats.append((user_id, score, data))
    
    # Сортируем по очкам
    player_stats.sort(key=lambda x: x[1], reverse=True)
    
    top_text = "🏆 <b>Топ игроков:</b> \n\n"
    
    if not player_stats:
        top_text += "Пока никто не играл... Будь первым! 🎄"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, score, data) in enumerate(player_stats[:10]):
            if i < 3:
                medal = medals[i]
            else:
                medal = f"{i+1}."
            
            user_name = data.get("name", f"Игрок {user_id}")
            top_text += f"{medal} {user_name} — {score} очков\n"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            top_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            top_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )

# -------------------------------------------------------------------
# 🎪 РАЗДЕЛ: КВЕСТЫ
# -------------------------------------------------------------------
async def enhanced_quest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    quests_info = """
🏔️ <b>Эпические новогодние квесты!</b>

✨ <b>Как проходить квесты:</b>
1. Выбери квест по сложности
2. Читай историю и выбирай действия
3. У каждого действия свой шанс успеха
4. Получай награды за успех!

🎁 <b>Награды за квесты:</b>
• Очки Санты 🎅
• Опыт оленёнка 🦌
• Редкие предметы ✨
• Достижения 🏆

Выбери квест для прохождения:
"""
    
    quests = [
        {"name": "❄️ Поиск замерзших рун", "id": "frozen_runes", "difficulty": "⚡⚡"},
        {"name": "🎁 Спасение подарков", "id": "gift_rescue", "difficulty": "⚡⚡⚡"},
        {"name": "🦌 Поиск пропавших оленей", "id": "lost_reindeer", "difficulty": "⚡⚡⚡⚡"},
        {"name": "🏰 Штурм замка Гринча", "id": "grinch_castle", "difficulty": "⚡⚡⚡⚡⚡"}
    ]
    
    keyboard = []
    for quest in quests:
        keyboard.append([InlineKeyboardButton(
            f"{quest['name']} {quest['difficulty']}", 
            callback_data=f"quest_start_{quest['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        quests_info,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quest_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quest_id = update.callback_query.data.replace("quest_start_", "")
    await update.callback_query.answer(f"Квест '{quest_id}' скоро будет добавлен!")
    # Здесь будет логика квестов
    admin = is_admin(update)
    await update.callback_query.edit_message_text(
        f"🏔️ Квест в разработке! Следи за обновлениями! 🎄",
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# 📢 РАЗДЕЛ: РАССЫЛКА ДЛЯ АДМИНА
# -------------------------------------------------------------------
async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    broadcast_info = """
📢 <b>Система рассылки сообщений</b>

✨ <b>Как работает:</b>
1. Выбери категорию получателей
2. Напиши сообщение для рассылки
3. Бот отправит его всем выбранным пользователям
4. Получи отчёт о доставке

👥 <b>Категории получателей:</b>
• <b>Всем пользователям</b> - кто-либо запускал бота
• <b>Участникам комнат</b> - только активные в комнатах

Выбери категорию получателей:
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Всем пользователям", callback_data="broadcast_all")],
        [InlineKeyboardButton("🎄 Участникам комнат", callback_data="broadcast_rooms")],
        [InlineKeyboardButton("📊 Статистика рассылки", callback_data="broadcast_stats")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]
    ])
    
    await update.callback_query.edit_message_text(
        broadcast_info,
        parse_mode='HTML',
        reply_markup=keyboard
    )

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Функция рассылки в разработке!")
    admin = is_admin(update)
    await update.callback_query.edit_message_text(
        "📢 Система рассылки скоро будет доступна!",
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# 🎄 ГЛАВНОЕ МЕНЮ
# -------------------------------------------------------------------
def enhanced_menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("🎁 Ввести пожелание", callback_data="wish"),
         InlineKeyboardButton("✨ Тост дня", callback_data="toast")],
        [InlineKeyboardButton("🎮 Мини-игры", callback_data="mini_games"),
         InlineKeyboardButton("❄️ Снегопад", callback_data="snowfall")],
        [InlineKeyboardButton("🎁 Идея подарка", callback_data="gift_idea"),
         InlineKeyboardButton("🏔️ Эпичные квесты", callback_data="quest_menu")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile"),
         InlineKeyboardButton("🏆 Топ игроков", callback_data="top_players")],
        [InlineKeyboardButton("♟️ Шашки", callback_data="game_checkers"),
         InlineKeyboardButton("📋 Участники комнаты", callback_data="room_members")],
    ]
    
    # Добавляем кнопку создания комнаты для админа
    if admin:
        base.append([InlineKeyboardButton("🏠 СОЗДАТЬ КОМНАТУ", callback_data="create_room_btn")])
        base.extend([
            [InlineKeyboardButton("🎄 Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("🚀 Админ: Запуск игры", callback_data="admin_start")],
            [InlineKeyboardButton("🗑️ Админ: Удалить комнату", callback_data="admin_delete")],
            [InlineKeyboardButton("📜 Админ: Пожелания", callback_data="admin_wishes")],
            [InlineKeyboardButton("🔀 Админ: Кому кто", callback_data="admin_map")],
            [InlineKeyboardButton("📢 Админ: Рассылка", callback_data="broadcast_menu")],
        ])
    
    base.append([InlineKeyboardButton("🎅 Присоединиться к комнате", callback_data="join_room_menu")])
    return InlineKeyboardMarkup(base)

# -------------------------------------------------------------------
# 🔄 ГЛАВНЫЙ ОБРАБОТЧИК CALLBACK'ОВ
# -------------------------------------------------------------------
async def enhanced_inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "wish":
        await wish_start(update, context)

    elif q.data == "toast":
        await q.edit_message_text(
            f"✨ <b>Тост дня:</b>\n{toast_of_day()}", 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )
        
    elif q.data == "gift_idea":
        idea = generate_gift_idea()
        await q.edit_message_text(
            f"🎁 <b>Идея подарка:</b>\n\n{idea}\n\n"
            f"💡 <b>Совет:</b> учитывай интересы получателя!",
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )

    elif q.data == "snowfall":
        await animated_snowfall_buttons(update, context)
        
    elif q.data == "admin_rooms":
        if not is_admin(update): 
            await q.edit_message_text("🚫 Доступ запрещён.")
            return
        data = load_data()
        txt = "📦 <b>Комнаты:</b>\n\n"
        for c, room in data["rooms"].items():
            status = "✅ Запущена" if room["game_started"] else "⏳ Ожидание"
            txt += f"{c} — {len(room['members'])} участников — {status}\n"
        await q.edit_message_text(
            txt, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard(True)
        )
        
    elif q.data == "admin_delete":
        await delete_room_menu(update, context)

    elif q.data == "admin_wishes":
        if not is_admin(update): 
            await q.edit_message_text("🚫 Доступ запрещён.")
            return
        data = load_data()
        txt = "🎁 <b>Все пожелания:</b>\n"
        for c, room in data["rooms"].items():
            txt += f"\n<b>Комната {c}:</b>\n"
            for uid, m in room["members"].items():
                wish = m['wish'] if m['wish'] else "❌ Не указано"
                txt += f"— {m['name']}: {wish}\n"
        await q.edit_message_text(
            txt, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard(True)
        )

    elif q.data == "admin_map":
        if not is_admin(update): 
            await q.edit_message_text("🚫 Доступ запрещён.")
            return
        data = load_data()
        txt = "🔀 <b>Распределение:</b>\n"
        for c, room in data["rooms"].items():
            if not room["game_started"]: continue
            txt += f"\n<b>Комната {c}:</b>\n"
            for g, r in room["assign"].items():
                mg = room["members"][g]
                mr = room["members"][r]
                txt += f"🎅 {mg['name']} → 🎁 {mr['name']}\n"
        await q.edit_message_text(
            txt, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard(True)
        )
        
    elif q.data == "admin_start":
        await start_game_admin(update, context)
        
    elif q.data.startswith("start_"):
        await start_specific_game(update, context)
        
    elif q.data.startswith("delete_"):
        await delete_specific_room(update, context)
        
    elif q.data == "profile":
        await enhanced_profile(update, context)
        
    elif q.data == "top_players":
        await show_top_players(update, context)
        
    elif q.data == "room_members":
        await show_room_members(update, context)
        
    elif q.data == "mini_games":
        await mini_game_menu(update, context)
        
    elif q.data == "quest_menu":
        await enhanced_quest_menu(update, context)
        
    elif q.data == "join_room_menu":
        await join_room_menu(update, context)
        
    elif q.data == "broadcast_menu":
        await broadcast_menu(update, context)
        
    elif q.data == "create_room_btn":
        if not is_admin(update):
            await q.answer("🚫 Только администратор может создавать комнаты!", show_alert=True)
            return
        await create_room(update, context)
        
    elif q.data == "back_menu":
        admin = is_admin(update)
        await q.edit_message_text(
            "🎄 Возвращаемся в главное меню...",
            reply_markup=enhanced_menu_keyboard(admin)
        )

# -------------------------------------------------------------------
# 🎯 ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
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
    
    admin = is_admin(update)
    await update.callback_query.edit_message_text(
        "❄️ Снегопад завершён! Волшебство продолжается...",
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def snowfall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Создаем начальное сообщение
    message = await update.message.reply_text("❄️ Запускаю волшебный снегопад...")
    
    frames = ["❄️", "✨", "❅", "☃️", "🎄", "🌟", "💫", "⭐"]
    snow_effects = [
        "❄️✨❄️✨❄️✨❄️✨",
        "✨❄️✨❄️✨❄️✨❄️", 
        "❅🌟❅🌟❅🌟❅🌟",
        "☃️💫☃️💫☃️💫☃️💫",
        "🎄⭐🎄⭐🎄⭐🎄⭐",
        "✨❄️❅☃️✨❄️❅☃️",
        "🌟💫⭐🌟💫⭐🌟💫"
    ]
    
    # Анимация снегопада
    for i in range(10):
        snow_frame = random.choice(snow_effects)
        text = f"❄️ <b>Волшебный снегопад</b> ❄️\n\n{snow_frame}\n\n"
        
        # Добавляем прогресс
        progress = "🔴" * i + "⚪" * (10 - i)
        text += f"Снегопад: {progress}"
        
        try:
            await message.edit_text(text, parse_mode='HTML')
            await asyncio.sleep(0.5)
        except:
            break
    
    # Финальное сообщение
    add_santa_points(user.id, 10, context)
    await message.edit_text(
        f"❄️ <b>Снегопад завершён!</b> ❄️\n\n"
        f"✨ Волшебство наполнило воздух!\n"
        f"🎁 +10 очков Санты за настроение!\n\n"
        f"Продолжаем праздник! 🎄",
        parse_mode='HTML'
    )
    
    admin = is_admin(update)
    await update.message.reply_text(
        "Выбери следующее действие:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 Твой ID: {user.id}")

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    init_user_data(user.id)
    points = user_data[str(user.id)]["santa_points"]
    await update.message.reply_text(f"🎅 У тебя {points} очков Санты!")

# -------------------------------------------------------------------
# 🚀 ОСНОВНОЙ ЗАПУСК
# -------------------------------------------------------------------
def main():
    # Инициализация данных
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            pass
        print("📁 Файл данных найден")
    except FileNotFoundError:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"rooms": {}, "users": {}}, f, indent=4, ensure_ascii=False)
        print("📁 Создан новый файл данных")
    
    load_data()
    
    app = Application.builder().token(TOKEN).build()

    # Основные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_room", create_room))
    app.add_handler(CommandHandler("join_room", join_room))
    app.add_handler(CommandHandler("start_game", start_game_admin))
    app.add_handler(CommandHandler("snowfall", snowfall))
    app.add_handler(CommandHandler("top", show_top_players))
    app.add_handler(CommandHandler("profile", enhanced_profile))
    app.add_handler(CommandHandler("myid", my_id))
    app.add_handler(CommandHandler("points", points))

    # Обработчики callback'ов - ВАЖНО: правильный порядок!
    app.add_handler(CallbackQueryHandler(game_handlers, pattern="^(game_|coin_|battle_start|quiz_start)"))
    app.add_handler(CallbackQueryHandler(guess_handler, pattern="^guess_"))
    app.add_handler(CallbackQueryHandler(quiz_answer_handler, pattern="^quiz_answer_"))
    app.add_handler(CallbackQueryHandler(quiz_next_handler, pattern="^quiz_next$"))
    app.add_handler(CallbackQueryHandler(battle_action_handler, pattern="^battle_"))
    app.add_handler(CallbackQueryHandler(battle_continue_handler, pattern="^battle_continue$"))
    app.add_handler(CallbackQueryHandler(quest_start_handler, pattern="^quest_start_"))
    app.add_handler(CallbackQueryHandler(broadcast_handler, pattern="^broadcast_"))
    app.add_handler(CallbackQueryHandler(enhanced_inline_handler))

    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, join_room))

    print("🎄 Бот v2.4 запускается на Replit...")
    print("✨ ВСЕ кнопки исправлены + улучшен снегопад + кнопка создания комнаты!")
    print("🔧 Оптимизировано для Replit")
    
    # Запуск бота с обработкой ошибок для Replit
    try:
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        # Для Replit - перезапуск при ошибке
        print("🔄 Перезапуск через 5 секунд...")
        import time
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()
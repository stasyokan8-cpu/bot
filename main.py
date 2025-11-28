# ???? SUPER-DELUXE SECRET SANTA BOT v3.1 ????
# ИСПРАВЛЕННАЯ ВЕРСИЯ: улучшенный баланс, работающие квесты, исправленные шашки

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

print(f"?? Запуск Secret Santa Bot v3.1 на Replit...")

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
        [InlineKeyboardButton("?? Назад в меню", callback_data="back_menu")]
    ])

def toast_of_day():
    TOASTS = [
        "?? Пусть в новом году твой холодильник всегда будет полен, а будильник — сломан!",
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
            "username": "",
            "answered_quiz_questions": [],
            "last_checkers_win": None
        }

def add_santa_points(user_id, points, context: ContextTypes.DEFAULT_TYPE = None):
    init_user_data(user_id)
    user_data[str(user_id)]["santa_points"] += points
    user_data[str(user_id)]["total_points"] += points
    
    if context and abs(points) >= 50:
        try:
            context.bot.send_message(
                user_id,
                f"?? {'Получено' if points > 0 else 'Потеряно'} {abs(points)} очков Санты!"
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
# ?? РАЗДЕЛ: ГЕНЕРАТОР ИДЕЙ ПОДАРКОВ (РАСШИРЕННЫЙ)
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# ?? РАЗДЕЛ: ОСНОВНЫЕ КОМАНДЫ И ИНТЕРФЕЙС
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    init_user_data(user.id)
    
    # Сохраняем данные пользователя
    user_data[str(user.id)]["name"] = user.full_name
    user_data[str(user.id)]["username"] = user.username or "без username"
    
    welcome_text = f"""
?? Добро пожаловать, {user.first_name}! ??

? <b>Правила Тайного Санты:</b>
1. Создай или присоединись к комнате
2. Напиши своё пожелание подарка
3. Дождись запуска игры организатором
4. Получи имя своего получателя и подари ему подарок!

?? <b>Что можно делать в боте:</b>
• Создавать комнаты и приглашать друзей
• Писать пожелания подарков
• Играть в новогодние мини-игры
• Проходить квесты и получать достижения
• Соревноваться с друзьями в рейтинге

Выбери действие ниже ??
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
?? <b>Написание пожелания</b>

? <b>Как это работает:</b>
1. Напиши своё пожелание подарка в одном сообщении
2. Будь конкретным, но оставляй пространство для фантазии
3. Учитывай бюджет участников
4. После запуска игры изменить пожелание будет нельзя!

?? <b>Примеры хороших пожеланий:</b>
• "Люблю читать, хотел бы интересную книгу"
• "Нужен тёплый плед для холодных вечеров"
• "Хочу сюрприз - угадайте мои интересы!"

?? <b>Напиши своё пожелание ниже:</b>
"""
    
    await update.callback_query.edit_message_text(
        wish_instructions,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user

    # Обработка рассылки для админа
    if is_admin(update) and "broadcast_mode" in context.user_data:
        await handle_broadcast_message(update, context)
        return

    if context.user_data.get("wish_mode"):
        # Найдём все комнаты, где этот участник есть
        for code, room in data["rooms"].items():
            if str(user.id) in room["members"]:
                if room.get("game_started"):
                    await update.message.reply_text("?? Игра уже запущена! Менять пожелание нельзя.")
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
        return

    # Обработка присоединения к комнате по коду
    if context.user_data.get("join_mode"):
        await join_room(update, context)
        return

    # Если просто текст и он похож на код комнаты
    if len(update.message.text.strip()) == 6 and update.message.text.strip().startswith('R'):
        context.user_data["join_mode"] = True
        await join_room(update, context)
        return

    # Если ничего не подошло - показываем меню
    admin = is_admin(update)
    await update.message.reply_text(
        "Выбери действие в меню:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# ?? РАЗДЕЛ: УПРАВЛЕНИЕ КОМНАТАМИ
# -------------------------------------------------------------------
async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка прав администратора
    if not is_admin(update):
        if update.callback_query:
            await update.callback_query.answer("?? Только @BeellyKid может создавать комнаты!", show_alert=True)
            return
        else:
            await update.message.reply_text("?? Только @BeellyKid может создавать комнаты.")
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
    
    # Уведомление об успешном создании
    success_text = (
        f"?? <b>Комната создана!</b>\n\n"
        f"<b>Код комнаты:</b> {code}\n"
        f"<b>Ссылка для приглашения:</b>\n"
        f"https://t.me/{(await context.bot.get_me()).username}?start=join_{code}\n\n"
        f"Приглашай друзей! Они могут присоединиться через меню бота."
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            success_text,
            parse_mode='HTML',
            reply_markup=enhanced_menu_keyboard(admin)
        )
    else:
        await update.message.reply_text(
            success_text,
            parse_mode='HTML',
            reply_markup=enhanced_menu_keyboard(admin)
        )

async def join_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    join_instructions = """
?? <b>Присоединение к комнате</b>

? <b>Как присоединиться:</b>
1. Попроси у организатора код комнаты (формат: RXXXXX)
2. Используй команду: /join_room RXXXXX
3. Или просто напиши код комнаты в чат

?? <b>Правила:</b>
• Можно быть только в одной комнате
• Присоединиться можно только до старта игры
• Минимум 2 участника для запуска
• Все участники должны написать пожелания

?? <b>Напиши код комнаты ниже:</b>
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
        await update.message.reply_text("?? Неверный формат кода! Код должен быть в формате RXXXXX")
        return
        
    if code not in data["rooms"]:
        await update.message.reply_text("?? Такой комнаты нет. Проверь код или создай новую комнату.")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("?? Игра уже началась — вход закрыт!")
        return

    u = update.effective_user
    if str(u.id) in room["members"]:
        await update.message.reply_text("?? Ты уже в этой комнате!")
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
    
    members_text = f"?? <b>Участники комнаты {room_code}:</b>\n\n"
    for i, (user_id, member) in enumerate(user_room["members"].items(), 1):
        wish_status = "?" if member["wish"] else "?"
        username = f"@{member['username']}" if member["username"] != "без username" else "без username"
        members_text += f"{i}. {member['name']} ({username}) {wish_status}\n"
    
    members_text += f"\n<b>Всего участников:</b> {len(user_room['members'])}"
    
    await update.callback_query.edit_message_text(
        members_text,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
    )

# -------------------------------------------------------------------
# ?? РАЗДЕЛ: АДМИН-ПАНЕЛЬ
# -------------------------------------------------------------------
async def start_game_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён.", show_alert=True)
        return

    data = load_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "?? Нет созданных комнат!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return

    # Показываем список комнат для запуска
    keyboard = []
    for code, room in data["rooms"].items():
        if not room["game_started"] and len(room["members"]) >= 2:
            keyboard.append([InlineKeyboardButton(f"?? {code} ({len(room['members'])} участ.)", callback_data=f"start_{code}")])
    
    if not keyboard:
        await update.callback_query.edit_message_text(
            "?? Нет комнат для запуска! Нужны комнаты с минимум 2 участниками.",
            reply_markup=back_to_menu_keyboard(True)
        )
        return
    
    keyboard.append([InlineKeyboardButton("?? Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "?? <b>Запуск игры Тайный Санта</b>\n\n"
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
        await q.edit_message_text("?? Комната не найдена!")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await q.edit_message_text("?? Игра уже запущена в этой комнате!")
        return

    members = list(room["members"].keys())
    if len(members) < 2:
        await q.edit_message_text("?? Нужно минимум 2 участника!")
        return
        
    # Проверяем, все ли написали пожелания
    members_without_wishes = []
    for uid, member in room["members"].items():
        if not member["wish"]:
            members_without_wishes.append(member["name"])
    
    if members_without_wishes:
        await q.edit_message_text(
            f"?? <b>Не все участники написали пожелания:</b>\n"
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
                f"?? <b>Тайный Санта запущен!</b> ??\n\n"
                f"<b>Твой получатель:</b> {m['name']} (@{m['username']})\n\n"
                f"? <b>Его пожелание:</b> {m['wish']}\n\n"
                f"Удачи в выборе подарка! ??",
                parse_mode='HTML'
            )
            successful_sends += 1
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {giver}: {e}")

    admin = is_admin(update)
    await q.edit_message_text(
        f"?? <b>Игра запущена в комнате {code}!</b> ?\n\n"
        f"<b>Участников:</b> {len(members)}\n"
        f"<b>Сообщений отправлено:</b> {successful_sends}/{len(members)}\n\n"
        f"Все участники получили своих получателей! ??",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def delete_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён.", show_alert=True)
        return

    data = load_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "?? Нет созданных комнат для удаления!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return

    keyboard = []
    for code, room in data["rooms"].items():
        status = "? Запущена" if room["game_started"] else "? Ожидание"
        keyboard.append([InlineKeyboardButton(
            f"??? {code} ({len(room['members'])} участ.) - {status}", 
            callback_data=f"delete_{code}"
        )])
    
    keyboard.append([InlineKeyboardButton("?? Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "??? <b>Удаление комнат</b>\n\n"
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
        await q.edit_message_text("?? Комната не найдена!")
        return

    # Удаляем комнату
    room_info = data["rooms"][code]
    del data["rooms"][code]
    save_data(data)
    
    admin = is_admin(update)
    await q.edit_message_text(
        f"??? <b>Комната {code} удалена!</b>\n\n"
        f"<b>Было участников:</b> {len(room_info['members'])}\n"
        f"<b>Статус игры:</b> {'Запущена' if room_info['game_started'] else 'Не запущена'}\n\n"
        f"Все данные комнаты безвозвратно удалены.",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# ?? РАЗДЕЛ: МИНИ-ИГРЫ (ИСПРАВЛЕННЫЕ)
# -------------------------------------------------------------------
async def mini_game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    games_info = """
?? <b>Новогодние мини-игры</b>

? <b>Доступные игры:</b>

?? <b>Угадай число</b> - Угадай число от 1 до 5
• Победа: 25-50 очков
• Поражение: -10-20 очков

?? <b>Монетка судьбы</b> - Орёл или решка?
• Орёл: +15-30 очков
• Решка: -5-15 очков
• Серия побед даёт достижение!

?? <b>Битва с Гринчем</b> - Эпичная RPG-битва
• Победа: 80-150 очков + опыт
• Поражение: -30-60 очков
• 3 победы - достижение!

?? <b>Новогодний квиз</b> - Проверь знания
• 5 случайных вопросов
• До 150 очков за идеальный результат
• Интересные факты!

?? <b>Шашки</b> - Игра с друзьми
• Интеграция с @goplaybot
• Победа: 80-120 очков
• Поражение: -20-40 очков

Выбери игру:
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Угадай число", callback_data="game_number")],
        [InlineKeyboardButton("?? Монетка судьбы", callback_data="game_coin")],
        [InlineKeyboardButton("?? Битва с Гринчем", callback_data="game_grinch")],
        [InlineKeyboardButton("?? Новогодний квиз", callback_data="game_quiz")],
        [InlineKeyboardButton("?? Шашки", callback_data="game_checkers")],
        [InlineKeyboardButton("?? Назад в меню", callback_data="back_menu")],
    ])
    await update.callback_query.edit_message_text(games_info, parse_mode='HTML', reply_markup=kb)

# ?? Игра: Угадай число
async def game_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    num = random.randint(1, 5)
    context.user_data["guess_num"] = num
    
    game_rules = """
?? <b>Угадай число</b>

? <b>Правила:</b>
• Я загадал число от 1 до 5
• У тебя одна попытка
• За правильный ответ: 25-50 очков
• За ошибку: -10-20 очков

Выбери число:
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1,6)],
        [InlineKeyboardButton("?? Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# ?? Игра: Монетка судьбы
async def game_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    game_rules = """
?? <b>Монетка судьбы</b>

? <b>Правила:</b>
• Подбрасываю монетку - Орёл или Решка?
• Орёл: +15-30 очков
• Решка: -5-15 очков
• 5 побед подряд - достижение "Монетка Удачи"!

Нажимай "Подбросить монетку" ??
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Подбросить монетку", callback_data="coin_flip")],
        [InlineKeyboardButton("?? Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# ?? Игра: Битва с Гринчем (УЛУЧШЕННАЯ)
async def game_grinch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    game_rules = """
?? <b>Битва с Гринчем</b>

? <b>Правила битвы:</b>
• У тебя 100 HP, у Гринча 120 HP
• 4 типа действий: атака, защита, магия, побег
• Магия лечит тебя и вредит Гринчу (3 заряда)
• Побег имеет 30% шанс успеха

?? <b>Награды:</b>
• Победа: 80-150 очков + 40 опыта
• Поражение: -30-60 очков
• 3 победы - достижение "Гроза Гринча"!

Готов сразиться? ??
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Начать битву!", callback_data="battle_start")],
        [InlineKeyboardButton("?? Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# ?? Игра: Новогодний квиз
async def game_quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    # Проверяем, есть ли неотвеченные вопросы
    answered_questions = user_data[str(user.id)].get("answered_quiz_questions", [])
    available_questions = [q for q in NEW_YEAR_QUIZ if q["id"] not in answered_questions]
    
    if len(available_questions) < 5:
        if len(answered_questions) >= len(NEW_YEAR_QUIZ):
            await q.edit_message_text(
                "?? <b>Ты ответил на все вопросы новогоднего квиза!</b>\n\n"
                "Ты настоящий эксперт в новогодних традициях! ??\n"
                "Возвращайся позже, когда добавим новые вопросы!",
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard()
            )
            return
        else:
            # Используем оставшиеся вопросы
            available_questions = [q for q in NEW_YEAR_QUIZ if q["id"] not in answered_questions]
    
    game_rules = f"""
?? <b>Новогодний квиз</b>

? <b>Правила:</b>
• 5 случайных вопросов о Новом годе
• За каждый правильный ответ +1 балл
• После вопроса - интересный факт!

?? <b>Статистика:</b>
• Отвечено вопросов: {len(answered_questions)}/{len(NEW_YEAR_QUIZ)}
• Доступно вопросов: {len(available_questions)}

?? <b>Награды:</b>
• 5/5: 150 очков + достижение
• 4/5: 100 очков
• 3/5: 60 очков
• 2/5 и меньше: 30 очков

Проверь свои знания! ??
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Начать квиз!", callback_data="quiz_start")],
        [InlineKeyboardButton("?? Назад в игры", callback_data="mini_games")]
    ])
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=kb)

# ?? Игра: Шашки (УЛУЧШЕННАЯ)
async def game_checkers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    game_rules = f"""
?? <b>Шашки с друзьями</b>

? <b>Твоя статистика:</b>
• Побед: {user_data[str(user.id)].get('checkers_wins', 0)}
• Поражений: {user_data[str(user.id)].get('checkers_losses', 0)}

?? <b>Как играть и подтверждать результат:</b>
1. Нажми "?? Начать игру" для игры с другом через @goplaybot
2. Сыграй партию в шашки
3. Вернись в этого бота и подтверди результат
4. Получи награды за победу или потери за поражение

?? <b>Внимание:</b>
• Подтверждай результат только после реальной игры
• Нельзя подтверждать победы чаще 1 раза в 30 минут
• За обман могут быть сняты очки

?? <b>Награды:</b>
• Победа: 80-120 очков + 25 опыта
• Поражение: -20-40 очков
• Серия побед: дополнительные бонусы!

?? <b>Начни игру сейчас:</b>
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Начать игру в шашки", url="https://t.me/goplaybot?start=checkers")],
        [InlineKeyboardButton("? Я ВЫИГРАЛ(А) - подтвердить победу", callback_data="checkers_confirm_win")],
        [InlineKeyboardButton("? Я ПРОИГРАЛ(А) - подтвердить поражение", callback_data="checkers_confirm_loss")],
        [InlineKeyboardButton("?? Моя статистика", callback_data="checkers_stats")],
        [InlineKeyboardButton("?? Как подтверждать результаты", callback_data="checkers_help")],
        [InlineKeyboardButton("?? Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(game_rules, parse_mode='HTML', reply_markup=keyboard)

# -------------------------------------------------------------------
# ?? ОБРАБОТЧИКИ МИНИ-ИГР
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
    
    side = random.choice(["Орёл ??", "Решка ??"])
    user = update.effective_user
    init_user_data(user.id)
    
    if "coin_wins" not in context.user_data:
        context.user_data["coin_wins"] = 0
        
    if side == "Орёл ??":
        context.user_data["coin_wins"] += 1
        points = random.randint(15, 30)
        add_santa_points(user.id, points, context)
        
        if context.user_data["coin_wins"] >= 5:
            add_achievement(user.id, "lucky_coin")
            result_text = f"?? Монетка: {side}! +{points} очков\n\n?? 5 побед подряд! Достижение 'Монетка Удачи'!"
            context.user_data["coin_wins"] = 0
        else:
            result_text = f"?? Монетка: {side}! +{points} очков\nСерия побед: {context.user_data['coin_wins']}"
    else:
        points_lost = random.randint(5, 15)
        add_santa_points(user.id, -points_lost, context)
        context.user_data["coin_wins"] = 0
        result_text = f"?? Монетка: {side}! Потеряно {points_lost} очков"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Ещё раз", callback_data="game_coin")],
        [InlineKeyboardButton("?? Назад в игры", callback_data="mini_games")]
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
        result_text = f"?? Верно! Было число {real}. Получено {points} очков Санты!"
    else:
        points_lost = random.randint(10, 20)
        add_santa_points(user.id, -points_lost, context)
        result_text = f"?? Не угадал! Было число {real}. Потеряно {points_lost} очков."
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Играть снова", callback_data="game_number")],
        [InlineKeyboardButton("?? Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(result_text, reply_markup=kb)

# -------------------------------------------------------------------
# ?? ЭПИЧНАЯ БИТВА С ГРИНЧЕМ (ИСПРАВЛЕННАЯ И УЛУЧШЕННАЯ)
# -------------------------------------------------------------------
async def epic_grinch_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    user_data[str(user.id)]["grinch_fights"] += 1
    
    # УЛУЧШЕННАЯ СИСТЕМА ХАРАКТЕРИСТИК
    player_stats = {
        "hp": 100,
        "max_hp": 100,
        "attack": random.randint(18, 28),
        "defense": random.randint(8, 15),
        "special_charges": 3
    }
    
    grinch_stats = {
        "hp": 120,
        "max_hp": 120,
        "attack": random.randint(22, 32),
        "defense": random.randint(10, 18),
        "special_used": False,
        "rage_mode": False,
        "consecutive_defends": 0
    }
    
    context.user_data["battle_state"] = {
        "player": player_stats,
        "grinch": grinch_stats,
        "round": 1,
        "battle_log": []
    }
    
    await show_battle_interface(update, context)

async def show_battle_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    battle_state = context.user_data["battle_state"]
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    # Создаем визуальные шкалы HP
    player_hp_bar = "??" * max(1, player["hp"] // 10) + "?" * max(0, (player["max_hp"] - player["hp"]) // 10)
    grinch_hp_bar = "??" * max(1, grinch["hp"] // 10) + "?" * max(0, (grinch["max_hp"] - grinch["hp"]) // 10)
    
    battle_text = f"""
?? <b>ЭПИЧНАЯ БИТВА С ГРИНЧЕМ - Раунд {battle_state['round']}</b>

?? <b>ТВОЙ САНТА:</b>
{player_hp_bar} {player['hp']}/{player['max_hp']} HP
? Атака: {player['attack']} ?? Защита: {player['defense']}
? Особые умения: {player['special_charges']} зарядов

?? <b>ГРИНЧ:</b>  
{grinch_hp_bar} {grinch['hp']}/{grinch['max_hp']} HP
? Атака: {grinch['attack']} ?? Защита: {grinch['defense']}

Выбери действие:
"""
    
    # Добавляем лог битвы если есть
    if battle_state["battle_log"]:
        battle_text += "\n?? <b>Последние события:</b>\n" + "\n".join(battle_state["battle_log"][-3:]) + "\n"
    
    keyboard = [
        [InlineKeyboardButton("?? Атаковать", callback_data="battle_attack")],
        [InlineKeyboardButton("?? Укрепить защиту", callback_data="battle_defend")],
        [InlineKeyboardButton("? Новогоднее волшебство", callback_data="battle_special")],
        [InlineKeyboardButton("?? Сбежать", callback_data="battle_flee")]
    ]
    
    await q.edit_message_text(battle_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    action = q.data.replace("battle_", "")
    battle_state = context.user_data["battle_state"]
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    battle_log = battle_state["battle_log"]
    
    # Ход игрока
    if action == "attack":
        damage = max(1, player["attack"] - grinch["defense"] // 3)
        grinch["hp"] -= damage
        battle_log.append(f"?? Ты атаковал и нанёс {damage} урона!")
        
    elif action == "defend":
        defense_bonus = random.randint(8, 15)
        player["defense"] += defense_bonus
        battle_log.append(f"?? Ты укрепил защиту! +{defense_bonus} к защите")
        
    elif action == "special" and player["special_charges"] > 0:
        player["special_charges"] -= 1
        heal = random.randint(25, 40)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        special_damage = random.randint(20, 30)
        grinch["hp"] -= special_damage
        battle_log.append(f"? Новогоднее волшебство! Исцеление +{heal}, Гринч получает {special_damage} урона!")
        
    elif action == "flee":
        flee_chance = random.random()
        if flee_chance > 0.7:  # 30% шанс сбежать
            await q.edit_message_text(
                "?? Ты успешно сбежал от Гринча!\n\n-20 очков Санты за трусость!",
                reply_markup=back_to_menu_keyboard()
            )
            add_santa_points(update.effective_user.id, -20, context)
            return
        else:
            battle_log.append("?? Попытка сбежать провалилась! Гринч блокирует escape!")
    
    # Проверка победы
    if grinch["hp"] <= 0:
        await battle_victory(update, context, battle_log)
        return
    
    # УЛУЧШЕННЫЙ ХОД ГРИНЧА
    grinch_actions = ["attack", "attack", "strong_attack", "special", "defend", "rage_attack"]
    grinch_action = random.choice(grinch_actions)

    if grinch_action == "attack":
        damage = max(1, grinch["attack"] - player["defense"] // 3)
        player["hp"] -= damage
        grinch["consecutive_defends"] = 0
        battle_log.append(f"?? Гринч атаковал и нанёс {damage} урона!")

    elif grinch_action == "strong_attack":
        if random.random() > 0.3:  # 70% шанс попадания
            damage = max(1, (grinch["attack"] + 8) - player["defense"] // 4)
            player["hp"] -= damage
            battle_log.append(f"?? Гринч использует сильную атаку! {damage} урона!")
        else:
            battle_log.append(f"?? Гринч промахнулся сильной атакой!")
        grinch["consecutive_defends"] = 0

    elif grinch_action == "rage_attack" and grinch["hp"] < 40:
        damage = max(1, (grinch["attack"] + 12) - player["defense"] // 5)
        player["hp"] -= damage
        grinch["rage_mode"] = True
        battle_log.append(f"?? ГРИНЧ В ЯРОСТИ! Мощная атака на {damage} урона!")
        grinch["consecutive_defends"] = 0

    elif grinch_action == "defend":
        # Ограничиваем последовательную защиту
        if grinch["consecutive_defends"] < 2:
            grinch_defense_bonus = random.randint(5, 10)
            grinch["defense"] += grinch_defense_bonus
            grinch["consecutive_defends"] += 1
            battle_log.append(f"?? Гринч укрепил защиту! +{grinch_defense_bonus} к защите")
        else:
            # После 2 защит подряд - вынужденная атака
            damage = max(1, grinch["attack"] - player["defense"] // 3)
            player["hp"] -= damage
            grinch["consecutive_defends"] = 0
            battle_log.append(f"?? Гринч вынужден атаковать! {damage} урона!")

    elif grinch_action == "special" and not grinch["special_used"]:
        grinch["special_used"] = True
        grinch_special_damage = random.randint(25, 35)
        player["hp"] -= grinch_special_damage
        # Спецприем также снижает защиту игрока
        player["defense"] = max(5, player["defense"] - 8)
        battle_log.append(f"?? Гринч использует 'Крадущийся праздник'! -{grinch_special_damage} HP, твоя защита снижена!")
        grinch["consecutive_defends"] = 0
    
    # Проверка поражения
    if player["hp"] <= 0:
        await battle_defeat(update, context, battle_log)
        return
    
    battle_state["round"] += 1
    battle_state["battle_log"] = battle_log[-5:]  # Сохраняем только последние 5 записей
    
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
?? <b>ПОБЕДА НАД ГРИНЧЕМ!</b> ??

? <b>Награды:</b>
• +{points_earned} очков Санты
• +40 опыта оленёнку
• Звание Защитника Рождества!

?? <b>Ход битвы:</b>
""" + "\n".join(battle_log[-5:]) + f"""

Гринч повержен, и Новый Год спасён! ??
"""
    
    keyboard = [
        [InlineKeyboardButton("?? Сразиться снова", callback_data="game_grinch")],
        [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(victory_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_defeat(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_log):
    user = update.effective_user
    points_lost = random.randint(30, 60)
    add_santa_points(user.id, -points_lost, context)
    
    defeat_text = f"""
?? <b>ПОРАЖЕНИЕ...</b>

?? <b>Потеряно:</b> {points_lost} очков Санты

?? <b>Ход битвы:</b>
""" + "\n".join(battle_log[-5:]) + f"""

Не сдавайся! Гринч должен быть остановлен! ??
"""
    
    keyboard = [
        [InlineKeyboardButton("?? Попробовать снова", callback_data="game_grinch")],
        [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(defeat_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# -------------------------------------------------------------------
# ?? НОВОГОДНИЙ КВИЗ (РАСШИРЕННЫЙ)
# -------------------------------------------------------------------
NEW_YEAR_QUIZ = [
    {"id": 1, "question": "?? В какой стране начали наряжать ёлку на Новый год?", "options": ["???? Германия", "???? Россия", "???? США", "???? Франция"], "correct": 0, "fact": "Традиция наряжать ёлку зародилась в Германии в XVI веке!"},
    {"id": 2, "question": "? Сколько лучей у снежинки?", "options": ["4", "6", "8", "10"], "correct": 1, "fact": "Правильно! У снежинки всегда 6 лучей из-за кристаллической структуры льда."},
    {"id": 3, "question": "?? Как зовут оленя с красным носом?", "options": ["Рудольф", "Дашер", "Дансер", "Комет"], "correct": 0, "fact": "Рудольф — самый известный олень Санты с красным светящимся носом!"},
    {"id": 4, "question": "?? Во сколько бьют куранты в новогоднюю ночь?", "options": ["23:55", "00:00", "00:05", "00:10"], "correct": 1, "fact": "Куранты бьют ровно в полночь, символизируя наступление Нового года!"},
    {"id": 5, "question": "?? Кто обычно оставляет подарки под ёлкой в России?", "options": ["Санта Клаус", "Дед Мороз", "Снегурочка", "Йоулупукки"], "correct": 1, "fact": "В России подарки под ёлкой оставляет Дед Мороз со своей внучкой Снегурочкой!"},
    {"id": 6, "question": "?? Какой цвет традиционно считается новогодним?", "options": ["Красный", "Зелёный", "Золотой", "Все варианты"], "correct": 3, "fact": "Все три цвета — красный, зелёный и золотой — считаются традиционными новогодними!"},
    {"id": 7, "question": "?? Что принято делать под бой курантов?", "options": ["Загадывать желание", "Обниматься", "Кричать 'Ура!'", "Все варианты"], "correct": 3, "fact": "Под бой курантов принято загадывать желание, обниматься и кричать 'Ура!'"},
    {"id": 8, "question": "?? Сколько оленей в упряжке Санта Клауса?", "options": ["8", "9", "10", "12"], "correct": 1, "fact": "У Санты 9 оленей: Дашер, Дэнсер, Прэнсер, Виксен, Комет, Кьюпид, Дондер, Блитцен и Рудольф!"},
    {"id": 9, "question": "?? Какой самый популярный новогодний фильм?", "options": ["Один дома", "Один дома 2", "Этажом выше", "Красотка"], "correct": 0, "fact": "'Один дома' — самый популярный новогодний фильм всех времён!"},
    {"id": 10, "question": "?? Что традиционно пьют в новогоднюю ночь?", "options": ["Шампанское", "Водку", "Сок", "Все варианты"], "correct": 3, "fact": "В разных странах и семьях традиции разные, но шампанское — самый популярный напиток!"},
]

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    # Получаем неотвеченные вопросы
    answered_questions = user_data[str(user.id)].get("answered_quiz_questions", [])
    available_questions = [q for q in NEW_YEAR_QUIZ if q["id"] not in answered_questions]
    
    if len(available_questions) < 5:
        # Если вопросов меньше 5, используем все оставшиеся
        questions_to_use = available_questions
    else:
        # Выбираем 5 случайных вопросов из доступных
        questions_to_use = random.sample(available_questions, 5)
    
    context.user_data["quiz"] = {
        "score": 0,
        "current_question": 0,
        "questions": questions_to_use
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
        f"?? <b>Новогодний Квиз {progress}</b>\n\n"
        f"? {question_data['question']}",
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
        result_text = "? <b>Правильно!</b>"
    else:
        correct_answer = question_data["options"][question_data["correct"]]
        result_text = f"? <b>Неправильно!</b> Правильный ответ: {correct_answer}"
    
    # Показываем факт
    result_text += f"\n\n?? {question_data['fact']}"
    
    # Кнопка для продолжения
    keyboard = [[InlineKeyboardButton("?? Следующий вопрос", callback_data="quiz_next")]]
    
    await q.edit_message_text(
        result_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz_next_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    quiz_data = context.user_data["quiz"]
    current_question_data = quiz_data["questions"][quiz_data["current_question"]]
    
    # Добавляем вопрос в список отвеченных
    user = update.effective_user
    init_user_data(user.id)
    if "answered_quiz_questions" not in user_data[str(user.id)]:
        user_data[str(user.id)]["answered_quiz_questions"] = []
    
    if current_question_data["id"] not in user_data[str(user.id)]["answered_quiz_questions"]:
        user_data[str(user.id)]["answered_quiz_questions"].append(current_question_data["id"])
    
    quiz_data["current_question"] += 1
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
        result_message = "?? <b>ИДЕАЛЬНО! Ты настоящий новогодний эксперт!</b>"
    elif score >= total * 0.7:  # Больше 70%
        points = 100
        result_message = "?? <b>Отличный результат! Ты хорошо знаешь новогодние традиции!</b>"
    elif score >= total * 0.5:  # Больше 50%
        points = 60
        result_message = "?? <b>Хороший результат! Есть что вспомнить о Новом годе!</b>"
    else:
        points = 30
        result_message = "?? <b>Неплохо! Новогодние традиции — это интересно!</b>"
    
    add_santa_points(user.id, points, context)
    add_reindeer_exp(user.id, score * 10)
    user_data[str(user.id)]["games_won"] += 1
    user_data[str(user.id)]["quiz_wins"] = user_data[str(user.id)].get("quiz_wins", 0) + 1
    
    # Показываем статистику по отвеченным вопросам
    answered_count = len(user_data[str(user.id)].get("answered_quiz_questions", []))
    total_questions = len(NEW_YEAR_QUIZ)
    
    final_text = f"""
?? <b>Новогодний Квиз завершён!</b>

{result_message}

?? <b>Твой результат:</b> {score}/{total}
? <b>Получено очков:</b> {points}
?? <b>Опыта оленёнку:</b> {score * 10}

?? <b>Общая статистика:</b>
Отвечено вопросов: {answered_count}/{total_questions}

Хочешь попробовать ещё раз?
"""
    
    keyboard = [
        [InlineKeyboardButton("?? Пройти ещё раз", callback_data="game_quiz")],
        [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        final_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------------------------------------------------------------------
# ?? РАЗДЕЛ: ПРОФИЛЬ И СТАТИСТИКА
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
        "?? Новорождённый оленёнок (0 ур.)",
        "???? Оленёк-исследователь (1 ур.)", 
        "??? Сверкающий олень (2 ур.)",
        "???? Звёздный олень (3 ур.)",
        "???? Легендарный олень (4 ур.)",
        "???? Божественный олень (5 ур.)"
    ]
    
    reindeer_text = REINDEER_STAGES[reindeer_level] if reindeer_level < len(REINDEER_STAGES) else REINDEER_STAGES[-1]
    
    # Информация о скинах
    skin_display = {
        "default": "?? Обычный",
        "rainbow": "?? Радужный", 
        "ice_spirit": "?? Ледяной дух",
        "golden": "?? Золотой",
        "crystal": "?? Хрустальный",
        "cosmic": "?? Космический",
        "phantom": "?? Фантомный"
    }
    
    skin_text = skin_display.get(current_skin, "?? Обычный")
    
    # Статистика квиза
    answered_questions = len(user_info.get("answered_quiz_questions", []))
    total_questions = len(NEW_YEAR_QUIZ)
    
    profile_text = f"""
?? <b>Профиль игрока</b> @{user.username if user.username else user.first_name}

?? <b>Очки Санты:</b> {user_info['santa_points']}
?? <b>Твой олень:</b> {reindeer_text}
?? <b>Вид:</b> {skin_text}
?? <b>Опыт:</b> {reindeer_exp}/{(reindeer_level + 1) * 100}

?? <b>Достижения:</b> {len(user_info['achievements'])}
?? <b>Побед в играх:</b> {user_info['games_won']}
?? <b>Пройдено квестов:</b> {user_info['quests_finished']}
?? <b>Побед над Гринчем:</b> {user_info['grinch_wins']}

?? <b>Редких предметов:</b> {len(user_info['rare_items'])}
?? <b>Побед в шашках:</b> {user_info.get('checkers_wins', 0)}
?? <b>Побед в квизе:</b> {user_info.get('quiz_wins', 0)}
?? <b>Отвечено вопросов:</b> {answered_questions}/{total_questions}
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
    
    top_text = "?? <b>Топ игроков:</b> \n\n"
    
    if not player_stats:
        top_text += "Пока никто не играл... Будь первым! ??"
    else:
        medals = ["??", "??", "??"]
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
# ?? РАЗДЕЛ: КВЕСТЫ (ПОЛНОСТЬЮ РЕАЛИЗОВАННЫЕ)
# -------------------------------------------------------------------
async def enhanced_quest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    quests_info = f"""
??? <b>Эпические новогодние квесты!</b>

? <b>Твои квесты:</b>
• Пройдено: {user_data[str(user.id)]['quests_finished']}
• Активные: {len(context.user_data.get('active_quests', {}))}

?? <b>Награды за квесты:</b>
• Очки Санты ?? (50-300 очков)
• Опыт оленёнка ?? (20-100 опыта)  
• Редкие предметы ?
• Уникальные достижения ??

?? <b>Доступные квесты:</b>
"""

    quests = [
        {
            "name": "?? Поиск замерзших рун", 
            "id": "frozen_runes", 
            "difficulty": "??", 
            "reward": "100 очков + 30 опыта",
            "description": "Найди 5 магических рун в Зачарованном лесу"
        },
        {
            "name": "?? Спасение подарков", 
            "id": "gift_rescue", 
            "difficulty": "???", 
            "reward": "150 очков + 50 опыта",
            "description": "Верни подарки, украденные Гринчем"
        },
        {
            "name": "?? Поиск пропавших оленей", 
            "id": "lost_reindeer", 
            "difficulty": "????", 
            "reward": "200 очков + 80 опыта",
            "description": "Найди 3 потерявшихся оленей Санты"
        },
        {
            "name": "?? Штурм замка Гринча", 
            "id": "grinch_castle", 
            "difficulty": "?????", 
            "reward": "300 очков + 120 опыта",
            "description": "Эпичная битва в логове Гринча!"
        }
    ]
    
    keyboard = []
    for quest in quests:
        # Проверяем, завершен ли уже квест
        quest_key = f"quest_{quest['id']}_completed"
        status = " ?" if quest_key in user_data[str(user.id)].get("achievements", []) else ""
        
        keyboard.append([InlineKeyboardButton(
            f"{quest['name']} {quest['difficulty']}{status}", 
            callback_data=f"quest_start_{quest['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("?? Мои достижения", callback_data="quest_achievements")])
    keyboard.append([InlineKeyboardButton("?? Назад в меню", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        quests_info,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quest_frozen_runes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    # Инициализация квеста
    if "frozen_runes" not in context.user_data:
        context.user_data["frozen_runes"] = {
            "step": 1,
            "found_runes": 0,
            "attempts": 0,
            "locations": ["Снежный храм", "Ледяная пещера", "Замерзшее озеро", "Волшебный лес", "Гора духов"]
        }
    
    quest_data = context.user_data["frozen_runes"]
    
    if quest_data["step"] == 1:
        story = """
?? <b>Поиск замерзших рун</b>

В Зачарованном лесу спрятаны 5 магических рун, содержащих новогоднюю магию. 
Без них праздник не будет по-настоящему волшебным!

Ты стоишь на развилке трёх тропинок:
"""
        keyboard = [
            [InlineKeyboardButton("?? Идти по заснеженной тропе", callback_data="quest_frozen_path")],
            [InlineKeyboardButton("?? Спуститься в ледяную пещеру", callback_data="quest_ice_cave")],
            [InlineKeyboardButton("?? Вернуться в лагерь", callback_data="quest_menu")]
        ]
        
    elif quest_data["step"] == 2:
        story = f"""
?? <b>Прогресс: {quest_data['found_runes']}/5 рун найдено</b>

Ты находишься в {quest_data['locations'][quest_data['found_runes']]}. 
Куда направишься дальше?
"""
        keyboard = [
            [InlineKeyboardButton("?? Обыскать местность", callback_data="quest_search_area")],
            [InlineKeyboardButton("?? Использовать магический компас", callback_data="quest_use_compass")],
            [InlineKeyboardButton("???>? Перейти в следующую локацию", callback_data="quest_next_location")],
            [InlineKeyboardButton("?? Завершить поиски", callback_data="quest_complete")]
        ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ?? Квест: Спасение подарков (многошаговый)
async def quest_gift_rescue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    if "gift_rescue" not in context.user_data:
        context.user_data["gift_rescue"] = {
            "step": 1,
            "gifts_rescued": 0,
            "stealth": 50,
            "position": "вход в пещеру"
        }
    
    quest_data = context.user_data["gift_rescue"]
    
    if quest_data["step"] == 1:
        story = """
?? <b>Спасение подарков</b>

Гринч украл все подарки из мастерской Санты! 
Тебе нужно проникнуть в его пещеру и вернуть как можно больше подарков.

Ты стоишь у входа в пещеру Гринча. Стражи бродят вокруг.
"""
        keyboard = [
            [InlineKeyboardButton("?? Замаскироваться под ёлку", callback_data="quest_disguise")],
            [InlineKeyboardButton("? Быстро пробежать мимо стражей", callback_data="quest_sneak")],
            [InlineKeyboardButton("?? Пойти в лобовую атаку", callback_data="quest_attack")],
            [InlineKeyboardButton("?? Отступить", callback_data="quest_menu")]
        ]
    
    elif quest_data["step"] == 2:
        story = f"""
?? <b>Прогресс: {quest_data['gifts_rescued']} подарков спасено</b>

Ты внутри пещеры Гринча. Уровень скрытности: {quest_data['stealth']}/100

Перед тобой несколько коридоров:
"""
        keyboard = [
            [InlineKeyboardButton("?? Левый коридор (рискованно)", callback_data="quest_left_hall")],
            [InlineKeyboardButton("?? Центральный зал (умеренно)", callback_data="quest_center_hall")],
            [InlineKeyboardButton("?? Правый тоннель (безопасно)", callback_data="quest_right_tunnel")],
            [InlineKeyboardButton("?? Попытаться сбежать с добычей", callback_data="quest_escape")]
        ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ?? Квест: Поиск пропавших оленей
async def quest_lost_reindeer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    story = """
?? <b>Поиск пропавших оленей</b>

Трое оленей Санты потерялись в снежной буре! 
Их имена: Искорка, Снежок и Комета.

Куда отправишься на поиски?
"""

    keyboard = [
        [InlineKeyboardButton("?? Обыскать Северный лес", callback_data="quest_north_forest")],
        [InlineKeyboardButton("??? Подняться на Заснеженные горы", callback_data="quest_snow_mountains")],
        [InlineKeyboardButton("?? Проверить Ледяную долину", callback_data="quest_ice_valley")],
        [InlineKeyboardButton("?? Осмотреть Восточные равнины", callback_data="quest_east_plains")],
        [InlineKeyboardButton("?? Вернуться", callback_data="quest_menu")]
    ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ?? Квест: Штурм замка Гринча
async def quest_grinch_castle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    story = """
?? <b>Штурм замка Гринча</b>

Финальная битва! Замок Гринча защищён ледяными стенами и сторожевыми башнями.

Выбери стратегию штурма:
"""

    keyboard = [
        [InlineKeyboardButton("?? Штурмовать главные ворота", callback_data="quest_storm_gates")],
        [InlineKeyboardButton("?? Найти тайный проход", callback_data="quest_secret_passage")],
        [InlineKeyboardButton("?? Использовать новогоднюю магию", callback_data="quest_use_magic")],
        [InlineKeyboardButton("????>? Проникнуть через подземелье", callback_data="quest_dungeon")],
        [InlineKeyboardButton("?? Отступить", callback_data="quest_menu")]
    ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён", show_alert=True)
        return
        
    q = update.callback_query
    await q.answer()
    
    # Получаем ID пользователя из контекста или запрашиваем
    if "admin_selected_user" in context.user_data:
        user_id = context.user_data["admin_selected_user"]
        user_info = user_data.get(str(user_id), {})
        
        stats_text = f"""
?? <b>Детальная статистика пользователя</b>

?? <b>Информация:</b>
• Имя: {user_info.get('name', 'Неизвестно')}
• Username: @{user_info.get('username', 'без username')}
• ID: {user_id}

?? <b>Статистика шашек:</b>
• Побед: {user_info.get('checkers_wins', 0)}
• Поражений: {user_info.get('checkers_losses', 0)}
• Всего игр: {user_info.get('checkers_wins', 0) + user_info.get('checkers_losses', 0)}
• Последняя победа: {user_info.get('last_checkers_win', 'Никогда')}

?? <b>Общая статистика:</b>
• Очки Санты: {user_info.get('santa_points', 0)}
• Уровень оленя: {user_info.get('reindeer_level', 0)}
• Побед в играх: {user_info.get('games_won', 0)}
• Побед над Гринчем: {user_info.get('grinch_wins', 0)}
• Пройдено квестов: {user_info.get('quests_finished', 0)}
"""

        await q.edit_message_text(
            stats_text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("?? Общая статистика шашек", callback_data="admin_checkers_stats")],
                [InlineKeyboardButton("?? В админ-меню", callback_data="back_menu")]
            ])
        )
    else:
        # Показать список пользователей для выбора
        await show_user_selection(update, context)

async def show_user_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    keyboard = []
    for user_id, data in user_data.items():
        if data.get("checkers_wins", 0) > 0 or data.get("checkers_losses", 0) > 0:
            btn_text = f"{data.get('name', 'User')} ({data.get('checkers_wins', 0)} побед)"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"admin_select_user_{user_id}")])
    
    keyboard.append([InlineKeyboardButton("?? Назад", callback_data="admin_checkers_stats")])
    
    await q.edit_message_text(
        "?? <b>Выберите пользователя для детальной статистики:</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработчик старта квестов
async def quest_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    quest_id = q.data.replace("quest_start_", "")
    
    if quest_id == "frozen_runes":
        await quest_frozen_runes(update, context)
    elif quest_id == "gift_rescue":
        await quest_gift_rescue(update, context)
    elif quest_id == "lost_reindeer":
        await quest_lost_reindeer(update, context)
    elif quest_id == "grinch_castle":
        await quest_grinch_castle(update, context)

# Обработчики действий в квестах
async def quest_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    action = q.data.replace("quest_", "")
    user = update.effective_user
    init_user_data(user.id)
    
    # Определяем текущий активный квест
    active_quest = None
    for quest in ["frozen_runes", "gift_rescue"]:
        if quest in context.user_data:
            active_quest = quest
            break
    
    result = ""
    points_earned = 0
    exp_earned = 0
    
    if active_quest == "frozen_runes":
        quest_data = context.user_data["frozen_runes"]
        
        if action == "frozen_path":
            success = random.random() > 0.3
            if success:
                points_earned = 30
                exp_earned = 15
                quest_data["found_runes"] += 1
                result = "? Ты нашёл первую руну! +30 очков Санты, +15 опыта"
            else:
                result = "? Тропа привела в тупик. Попробуй другой путь!"
            quest_data["step"] = 2
            
        elif action == "ice_cave":
            success = random.random() > 0.5
            if success:
                points_earned = 50
                exp_earned = 25
                quest_data["found_runes"] += 2
                result = "?? В пещере ты нашёл 2 руны! +50 очков Санты, +25 опыта"
            else:
                points_earned = -10
                result = "?? Ты попал в лавину! Потеряно 10 очков"
            quest_data["step"] = 2
            
        elif action == "search_area":
            success = random.random() > 0.4
            if success and quest_data["found_runes"] < 5:
                points_earned = 25
                exp_earned = 10
                quest_data["found_runes"] += 1
                result = f"?? Ты нашёл руну! Всего найдено: {quest_data['found_runes']}/5. +25 очков, +10 опыта"
            else:
                result = "?? В этой области нет рун. Попробуй в другом месте."
                
        elif action == "use_compass" and user_data[str(user.id)]["santa_points"] >= 20:
            points_earned = -20
            quest_data["found_runes"] = min(5, quest_data["found_runes"] + 1)
            result = f"?? Магический компас указал на руну! -20 очков за использование. Найдено: {quest_data['found_runes']}/5"
            
        elif action == "next_location":
            result = "???>? Ты перемещаешься в следующую локацию..."
            
        elif action == "complete":
            total_runes = quest_data["found_runes"]
            if total_runes >= 3:
                points_earned = total_runes * 20
                exp_earned = total_runes * 8
                achievement = "frozen_runes_completed"
                if achievement not in user_data[str(user.id)]["achievements"]:
                    user_data[str(user.id)]["achievements"].append(achievement)
                    user_data[str(user.id)]["quests_finished"] += 1
                
                result = f"""
?? <b>Квест завершён!</b>

?? Найдено рун: {total_runes}/5
? Получено: {points_earned} очков, {exp_earned} опыта
?? Достижение получено: "Искатель рун"

Отличная работа! Новогодняя магия спасена!"""
                del context.user_data["frozen_runes"]
            else:
                result = "?? Нужно найти хотя бы 3 руны для завершения квеста!"
                return
    
    elif active_quest == "gift_rescue":
        quest_data = context.user_data["gift_rescue"]
        
        if action == "disguise":
            success = random.random() > 0.4
            if success:
                points_earned = 40
                exp_earned = 20
                quest_data["gifts_rescued"] += 2
                quest_data["stealth"] += 10
                result = "?? Отличная маскировка! Ты прошёл незамеченным и нашёл 2 подарка. +40 очков, +20 опыта"
            else:
                quest_data["stealth"] -= 15
                result = "?? Стражи заметили тебя! Уровень скрытности понижен."
            quest_data["step"] = 2
            
        elif action == "sneak":
            success = random.random() > 0.6
            if success:
                points_earned = 60
                exp_earned = 30
                quest_data["gifts_rescued"] += 3
                result = "? Молниеносный бросок! Ты нашёл 3 подарка. +60 очков, +30 опыта"
            else:
                points_earned = -20
                quest_data["stealth"] -= 25
                result = "?? Ты споткнулся и поднял тревогу! -20 очков"
            quest_data["step"] = 2
            
        elif action == "attack":
            success = random.random() > 0.7
            if success:
                points_earned = 80
                exp_earned = 40
                quest_data["gifts_rescued"] += 5
                quest_data["stealth"] = 0
                result = "?? Мощная атака! Ты победил стражей и нашёл 5 подарков. +80 очков, +40 опыта"
            else:
                points_earned = -30
                quest_data["stealth"] = 0
                result = "?? Ты был overpowered стражами! -30 очков"
            quest_data["step"] = 2
            
        elif action == "escape":
            total_gifts = quest_data["gifts_rescued"]
            if total_gifts > 0:
                points_earned = total_gifts * 25
                exp_earned = total_gifts * 15
                achievement = "gift_rescue_completed"
                if achievement not in user_data[str(user.id)]["achievements"]:
                    user_data[str(user.id)]["achievements"].append(achievement)
                    user_data[str(user.id)]["quests_finished"] += 1
                
                result = f"""
?? <b>Миссия выполнена!</b>

?? Спасено подарков: {total_gifts}
? Получено: {points_earned} очков, {exp_earned} опыта  
?? Достижение получено: "Спасатель подарков"

Ты вернул радость детям!"""
                del context.user_data["gift_rescue"]
            else:
                result = "?? Нужно спасти хотя бы 1 подарок!"
                return
    
    # Обработка общих действий для всех квестов
    if "north_forest" in action or "snow_mountains" in action or "ice_valley" in action or "east_plains" in action:
        success = random.random() > 0.5
        if success:
            points_earned = random.randint(40, 70)
            exp_earned = random.randint(20, 35)
            result = f"?? Ты нашёл потерявшегося оленя! +{points_earned} очков, +{exp_earned} опыта"
            add_achievement(user.id, "reindeer_finder")
        else:
            result = "?? В этой местности никого нет. Попробуй поискать в другом месте."
            
    elif "storm_gates" in action or "secret_passage" in action or "use_magic" in action or "dungeon" in action:
        success = random.random() > 0.6
        if success:
            points_earned = random.randint(100, 150)
            exp_earned = random.randint(50, 80)
            result = f"?? Успешный штурм! Ты проник в замок Гринча. +{points_earned} очков, +{exp_earned} опыта"
            add_achievement(user.id, "grinch_castle_conqueror")
        else:
            points_earned = -random.randint(30, 60)
            result = f"?? Штурм провалился! Защитники замка отбили атаку. {points_earned} очков"
    
    # Начисление наград
    if points_earned != 0:
        add_santa_points(user.id, points_earned, context)
    if exp_earned != 0:
        add_reindeer_exp(user.id, exp_earned)
    
    # Показываем результат
    keyboard = []
    if active_quest and "complete" not in action and "escape" not in action:
        keyboard.append([InlineKeyboardButton("?? Продолжить квест", callback_data=f"quest_start_{active_quest}")])
    keyboard.append([InlineKeyboardButton("??? Выбрать другой квест", callback_data="quest_menu")])
    keyboard.append([InlineKeyboardButton("?? В меню", callback_data="back_menu")])
    
    await q.edit_message_text(
        f"??? <b>Результат:</b>\n\n{result}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_quest_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    achievements = user_data[str(user.id)].get("achievements", [])
    quest_achievements = [
        ("frozen_runes_completed", "?? Искатель рун", "Найди 3+ рун в Зачарованном лесу"),
        ("gift_rescue_completed", "?? Спасатель подарков", "Верни украденные подарки"),
        ("reindeer_finder", "?? Поисковик оленей", "Найди потерявшегося оленя"),
        ("grinch_castle_conqueror", "?? Покоритель замка", "Проникни в замок Гринча")
    ]
    
    achievements_text = "?? <b>Твои достижения в квестах:</b>\n\n"
    
    for achievement_id, name, description in quest_achievements:
        status = "?" if achievement_id in achievements else "?"
        achievements_text += f"{status} <b>{name}</b>\n{description}\n\n"
    
    await q.edit_message_text(
        achievements_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("??? К квестам", callback_data="quest_menu")],
            [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
        ])
    )

# -------------------------------------------------------------------
# ?? РАЗДЕЛ: РАССЫЛКА ДЛЯ АДМИНА
# -------------------------------------------------------------------
async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    broadcast_info = """
?? <b>Система рассылки сообщений</b>

? <b>Как работает:</b>
1. Выбери категорию получателей
2. Напиши сообщение для рассылки
3. Бот отправит его всем выбранным пользователям
4. Получи отчёт о доставке

?? <b>Категории получателей:</b>
• <b>Всем пользователям</b> - кто-либо запускал бота
• <b>Участникам комнат</b> - только активные в комнатах

Выбери категорию получателей:
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Всем пользователям", callback_data="broadcast_all")],
        [InlineKeyboardButton("?? Участникам комнат", callback_data="broadcast_rooms")],
        [InlineKeyboardButton("?? Назад", callback_data="back_menu")]
    ])
    
    await update.callback_query.edit_message_text(
        broadcast_info,
        parse_mode='HTML',
        reply_markup=keyboard
    )

async def broadcast_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    context.user_data["broadcast_mode"] = "all"
    
    await update.callback_query.edit_message_text(
        "?? <b>Рассылка всем пользователям</b>\n\n"
        "Пришли сообщение, которое нужно разослать ВСЕМ пользователям бота.\n\n"
        "?? <b>Поддерживается:</b> текст, фото, видео, документы\n"
        "?? <b>Отмена:</b> /cancel",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("? Отмена", callback_data="broadcast_cancel")]])
    )

async def broadcast_room_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    context.user_data["broadcast_mode"] = "rooms"
    
    await update.callback_query.edit_message_text(
        "?? <b>Рассылка участникам комнат</b>\n\n"
        "Пришли сообщение, которое нужно разослать всем УЧАСТНИКАМ АКТИВНЫХ КОМНАТ.\n\n"
        "?? <b>Поддерживается:</b> текст, фото, видео, документы\n"
        "?? <b>Отмена:</b> /cancel",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("? Отмена", callback_data="broadcast_cancel")]])
    )

async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "broadcast_mode" in context.user_data:
        del context.user_data["broadcast_mode"]
    
    admin = is_admin(update)
    await update.callback_query.edit_message_text(
        "? Рассылка отменена",
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update) or "broadcast_mode" not in context.user_data:
        return
    
    broadcast_mode = context.user_data["broadcast_mode"]
    del context.user_data["broadcast_mode"]
    
    # Получаем список пользователей для рассылки
    users_to_message = set()
    data = load_data()
    
    if broadcast_mode == "all":
        # Все пользователи, которые когда-либо начинали диалог с ботом
        users_to_message = set(user_data.keys())
    elif broadcast_mode == "rooms":
        # Только пользователи в активных комнатах
        for room_code, room in data["rooms"].items():
            for user_id in room["members"]:
                users_to_message.add(user_id)
    
    if not users_to_message:
        await update.message.reply_text(
            "? Нет пользователей для рассылки!",
            reply_markup=enhanced_menu_keyboard(True)
        )
        return
    
    # Отправляем сообщение
    sent_count = 0
    failed_count = 0
    total_users = len(users_to_message)
    
    progress_msg = await update.message.reply_text(
        f"?? Начинаю рассылку...\n0/{total_users} отправлено"
    )
    
    for user_id in users_to_message:
        try:
            # Пытаемся отправить такое же сообщение
            if update.message.text:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=update.message.text,
                    parse_mode='HTML'
                )
            elif update.message.photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption,
                    parse_mode='HTML'
                )
            elif update.message.video:
                await context.bot.send_video(
                    chat_id=user_id,
                    video=update.message.video.file_id,
                    caption=update.message.caption,
                    parse_mode='HTML'
                )
            elif update.message.document:
                await context.bot.send_document(
                    chat_id=user_id,
                    document=update.message.document.file_id,
                    caption=update.message.caption,
                    parse_mode='HTML'
                )
            
            sent_count += 1
            
            # Обновляем прогресс каждые 10 сообщений
            if sent_count % 10 == 0:
                try:
                    await progress_msg.edit_text(
                        f"?? Рассылка...\n{sent_count}/{total_users} отправлено"
                    )
                except:
                    pass
                    
            # Небольшая задержка чтобы не превысить лимиты Telegram
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"Ошибка отправки пользователю {user_id}: {e}")
            failed_count += 1
    
    # Финальный отчет
    report_text = (
        f"? <b>Рассылка завершена!</b>\n\n"
        f"?? <b>Статистика:</b>\n"
        f"• Всего получателей: {total_users}\n"
        f"• Успешно отправлено: {sent_count}\n"
        f"• Не удалось отправить: {failed_count}\n"
        f"• Процент доставки: {(sent_count/total_users)*100:.1f}%\n\n"
        f"Рассылка выполнена для: {'всех пользователей' if broadcast_mode == 'all' else 'участников комнат'}"
    )
    
    await progress_msg.delete()
    await update.message.reply_text(
        report_text,
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(True)
    )

# Команда отмены для рассылки
async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "broadcast_mode" in context.user_data:
        del context.user_data["broadcast_mode"]
    
    admin = is_admin(update)
    await update.message.reply_text(
        "? Рассылка отменена",
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# ?? РАЗДЕЛ: ШАШКИ (ИСПРАВЛЕННЫЕ И УЛУЧШЕННЫЕ)
# -------------------------------------------------------------------
async def checkers_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    help_text = """
?? <b>Как подтверждать результаты в шашках:</b>

1. <b>Начни игру:</b>
   • Нажми "?? Начать игру в шашки"
   • Играй с другом через @goplaybot
   • Закончи партию

2. <b>Подтверди результат:</b>
   • Если ВЫИГРАЛ - нажми "? Подтвердить победу"
   • Если ПРОИГРАЛ - нажми "? Подтвердить поражение"

3. <b>Получи награды/потери:</b>
   • Победа: +80-120 очков Санты
   • Поражение: -20-40 очков Санты

?? <b>Важные правила:</b>
• Подтверждай только реальные игры
• Между подтверждениями должен быть перерыв 30+ минут
• За попытку обмана могут быть сняты очки

?? <b>Советы:</b>
• Тренируйся с друзьями
• Играй честно
• Улучшай свою стратегию!
"""

    await q.edit_message_text(
        help_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("?? К шашкам", callback_data="game_checkers")],
            [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
        ])
    )

async def checkers_confirm_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    # ПРОВЕРКА ВРЕМЕНИ - нельзя чаще чем раз в 30 минут
    last_win = user_data[str(user.id)].get("last_checkers_win")
    if last_win:
        last_time = datetime.fromisoformat(last_win)
        time_diff = datetime.now(timezone.utc) - last_time
        if time_diff < timedelta(minutes=30):
            remaining = timedelta(minutes=30) - time_diff
            minutes_left = int(remaining.total_seconds() // 60)
            
            await q.edit_message_text(
                f"? <b>Слишком рано!</b>\n\n"
                f"Подожди еще {minutes_left} минут перед следующим подтверждением.\n\n"
                f"Это правило нужно чтобы все играли честно! ??",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("?? Моя статистика", callback_data="checkers_stats")],
                    [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
                ])
            )
            return
    
    # Награда за победу
    points_earned = random.randint(80, 120)
    add_santa_points(user.id, points_earned, context)
    add_reindeer_exp(user.id, 25)
    
    # Обновляем статистику
    user_data[str(user.id)]["checkers_wins"] = user_data[str(user.id)].get("checkers_wins", 0) + 1
    user_data[str(user.id)]["last_checkers_win"] = datetime.now(timezone.utc).isoformat()
    
    # Проверяем достижения
    wins = user_data[str(user.id)]["checkers_wins"]
    achievement_unlocked = False
    
    if wins == 1 and "first_checkers_win" not in user_data[str(user.id)]["achievements"]:
        add_achievement(user.id, "first_checkers_win")
        achievement_unlocked = "?? Первая победа в шашках!"
    elif wins == 5 and "checkers_master" not in user_data[str(user.id)]["achievements"]:
        add_achievement(user.id, "checkers_master")
        achievement_unlocked = "?? Мастер шашек (5 побед)!"
    elif wins == 10 and "checkers_grandmaster" not in user_data[str(user.id)]["achievements"]:
        add_achievement(user.id, "checkers_grandmaster")
        achievement_unlocked = "?? Гроссмейстер шашек (10 побед)!"
    
    achievement_text = f"\n\n?? {achievement_unlocked}" if achievement_unlocked else ""
    
    await q.edit_message_text(
        f"?? <b>Победа подтверждена!</b>\n\n"
        f"? +{points_earned} очков Санты\n"
        f"?? +25 опыта оленёнку\n"
        f"?? Всего побед: {wins}\n"
        f"? Следующее подтверждение через 30 минут{achievement_text}\n\n"
        f"Отличная игра! ??",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("?? Статистика", callback_data="checkers_stats")],
            [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
        ])
    )

async def checkers_confirm_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    points_lost = random.randint(20, 40)
    add_santa_points(user.id, -points_lost, context)
    
    user_data[str(user.id)]["checkers_losses"] = user_data[str(user.id)].get("checkers_losses", 0) + 1
    
    await q.edit_message_text(
        f"?? <b>Поражение подтверждено</b>\n\n"
        f"?? -{points_lost} очков Санты\n"
        f"?? Всего поражений: {user_data[str(user.id)]['checkers_losses']}\n\n"
        f"Не расстраивайся! Удачи в следующей игре! ??",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("?? Реванш!", callback_data="game_checkers")],
            [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
        ])
    )

async def checkers_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    wins = user_data[str(user.id)].get("checkers_wins", 0)
    losses = user_data[str(user.id)].get("checkers_losses", 0)
    total_games = wins + losses
    win_rate = (wins / total_games * 100) if total_games > 0 else 0
    
    stats_text = f"""
?? <b>Статистика шашек</b>

?? <b>Общая:</b>
• Игр сыграно: {total_games}
• Побед: {wins}
• Поражений: {losses}
• Процент побед: {win_rate:.1f}%

?? <b>Достижения:</b>
"""
    
    achievements = user_data[str(user.id)].get("achievements", [])
    checkers_achievements = [
        ("first_checkers_win", "Первая победа", "?" if "first_checkers_win" in achievements else "?"),
        ("checkers_master", "5 побед", "?" if "checkers_master" in achievements else "?"), 
        ("checkers_grandmaster", "10 побед", "?" if "checkers_grandmaster" in achievements else "?")
    ]
    
    for achievement_id, name, status in checkers_achievements:
        stats_text += f"• {name}: {status}\n"
    
    await q.edit_message_text(
        stats_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("?? К шашкам", callback_data="game_checkers")],
            [InlineKeyboardButton("?? В меню", callback_data="back_menu")]
        ])
    )

async def admin_checkers_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("?? Доступ запрещён", show_alert=True)
        return
        
    q = update.callback_query
    await q.answer()
    
    # Собираем статистику всех пользователей по шашкам
    stats_data = []
    total_wins = 0
    total_losses = 0
    total_games = 0
    
    for user_id, data in user_data.items():
        wins = data.get("checkers_wins", 0)
        losses = data.get("checkers_losses", 0)
        user_games = wins + losses
        
        if user_games > 0:  # Показываем только тех, кто играл
            win_rate = (wins / user_games * 100) if user_games > 0 else 0
            stats_data.append({
                "name": data.get("name", f"User {user_id}"),
                "username": data.get("username", "без username"),
                "wins": wins,
                "losses": losses,
                "total_games": user_games,
                "win_rate": win_rate,
                "last_win": data.get("last_checkers_win")
            })
            
            total_wins += wins
            total_losses += losses
            total_games += user_games
    
    # Сортируем по количеству побед
    stats_data.sort(key=lambda x: x["wins"], reverse=True)
    
    stats_text = f"""
?? <b>АДМИН СТАТИСТИКА: ШАШКИ</b>

?? <b>Общая статистика:</b>
• Всего игр: {total_games}
• Побед: {total_wins}
• Поражений: {total_losses}
• Процент побед: {(total_wins/total_games*100) if total_games > 0 else 0:.1f}%

?? <b>Статистика по игрокам:</b>
"""
    
    if not stats_data:
        stats_text += "\n? Пока никто не играл в шашки"
    else:
        medals = ["??", "??", "??"]
        for i, player in enumerate(stats_data[:15]):  # Показываем топ-15
            if i < 3:
                medal = medals[i]
            else:
                medal = f"{i+1}."
            
            last_win_info = ""
            if player["last_win"]:
                last_time = datetime.fromisoformat(player["last_win"])
                time_diff = datetime.now(timezone.utc) - last_time
                if time_diff < timedelta(hours=24):
                    last_win_info = f" (?? {int(time_diff.total_seconds() // 3600)}ч назад)"
            
            stats_text += f"\n{medal} <b>{player['name']}</b> (@{player['username']})"
            stats_text += f"\n   ?? {player['wins']}?/{player['losses']}?"
            stats_text += f" ({player['win_rate']:.1f}%){last_win_info}"
    
    # Добавляем информацию о возможных нарушениях
    suspicious_players = []
    for player in stats_data:
        if player["last_win"]:
            last_time = datetime.fromisoformat(player["last_win"])
            time_diff = datetime.now(timezone.utc) - last_time
            # Если много побед за короткое время - подозрительно
            if player["wins"] > 5 and time_diff < timedelta(hours=2):
                suspicious_players.append(player)
    
    if suspicious_players:
        stats_text += f"\n\n?? <b>Подозрительная активность:</b>"
        for player in suspicious_players[:5]:
            stats_text += f"\n• {player['name']} - {player['wins']} побед за короткое время"
    
    await q.edit_message_text(
        stats_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("?? Обновить", callback_data="admin_checkers_stats")],
            [InlineKeyboardButton("?? В админ-меню", callback_data="back_menu")]
        ])
    )

# -------------------------------------------------------------------
# ?? ГЛАВНОЕ МЕНЮ
# -------------------------------------------------------------------
def enhanced_menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("?? Ввести пожелание", callback_data="wish"),
         InlineKeyboardButton("? Тост дня", callback_data="toast")],
        [InlineKeyboardButton("?? Мини-игры", callback_data="mini_games"),
         InlineKeyboardButton("?? Снегопад", callback_data="snowfall")],
        [InlineKeyboardButton("?? Идея подарка", callback_data="gift_idea"),
         InlineKeyboardButton("??? Эпичные квесты", callback_data="quest_menu")],
        [InlineKeyboardButton("?? Профиль", callback_data="profile"),
         InlineKeyboardButton("?? Топ игроков", callback_data="top_players")],
        [InlineKeyboardButton("?? Шашки", callback_data="game_checkers"),
         InlineKeyboardButton("?? Участники комнаты", callback_data="room_members")],
    ]
    
    # Добавляем кнопку создания комнаты для админа
    if admin:
        base.append([InlineKeyboardButton("?? СОЗДАТЬ КОМНАТУ", callback_data="create_room_btn")])
        base.extend([
            [InlineKeyboardButton("?? Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("?? Админ: Запуск игры", callback_data="admin_start")],
            [InlineKeyboardButton("??? Админ: Удалить комнату", callback_data="admin_delete")],
            [InlineKeyboardButton("?? Админ: Пожелания", callback_data="admin_wishes")],
            [InlineKeyboardButton("?? Админ: Кому кто", callback_data="admin_map")],
            [InlineKeyboardButton("?? Админ: Статистика шашек", callback_data="admin_checkers_stats")],
            [InlineKeyboardButton("?? Админ: Рассылка", callback_data="broadcast_menu")],
        ])
    
    base.append([InlineKeyboardButton("?? Присоединиться к комнате", callback_data="join_room_menu")])
    return InlineKeyboardMarkup(base)

# -------------------------------------------------------------------
# ?? ГЛАВНЫЙ ОБРАБОТЧИК CALLBACK'ОВ
# -------------------------------------------------------------------
async def enhanced_inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    
    try:
        await q.answer()
    except Exception as e:
        print(f"Ошибка ответа на callback: {e}")
        return

    try:
        if q.data == "wish":
            await wish_start(update, context)

        elif q.data == "toast":
            await q.edit_message_text(
                f"? <b>Тост дня:</b>\n{toast_of_day()}", 
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard()
            )
            
        elif q.data == "gift_idea":
            idea = generate_gift_idea()
            await q.edit_message_text(
                f"?? <b>Идея подарка:</b>\n\n{idea}\n\n"
                f"?? <b>Совет:</b> учитывай интересы получателя!",
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard()
            )

        elif q.data == "snowfall":
            await animated_snowfall(update, context)
            
        elif q.data == "admin_rooms":
            if not is_admin(update): 
                await q.answer("?? Только администратор может просматривать комнаты", show_alert=True)
                return
            data = load_data()
            txt = "?? <b>Комнаты:</b>\n\n"
            for c, room in data["rooms"].items():
                status = "? Запущена" if room["game_started"] else "? Ожидание"
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
                await q.answer("?? Только администратор может просматривать пожелания", show_alert=True)
                return
            data = load_data()
            txt = "?? <b>Все пожелания:</b>\n"
            for c, room in data["rooms"].items():
                txt += f"\n<b>Комната {c}:</b>\n"
                for uid, m in room["members"].items():
                    wish = m['wish'] if m['wish'] else "? Не указано"
                    txt += f"— {m['name']}: {wish}\n"
            await q.edit_message_text(
                txt, 
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard(True)
            )
            
        elif q.data == "admin_checkers_stats":
            await admin_checkers_stats(update, context)
            
        elif q.data == "admin_map":
            if not is_admin(update): 
                await q.answer("?? Только администратор может просматривать распределение", show_alert=True)
                return
            data = load_data()
            txt = "?? <b>Распределение:</b>\n"
            for c, room in data["rooms"].items():
                if not room["game_started"]: continue
                txt += f"\n<b>Комната {c}:</b>\n"
                for g, r in room["assign"].items():
                    mg = room["members"][g]
                    mr = room["members"][r]
                    txt += f"?? {mg['name']} > ?? {mr['name']}\n"
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
            
        elif q.data.startswith("quest_start_"):
            await quest_start_handler(update, context)
            
        elif q.data.startswith("quest_"):
            await quest_action_handler(update, context)
            
        elif q.data == "quest_achievements":
            await show_quest_achievements(update, context)
            
        elif q.data == "join_room_menu":
            await join_room_menu(update, context)
            
        elif q.data == "broadcast_menu":
            await broadcast_menu(update, context)
            
        elif q.data.startswith("admin_select_user_"):
            user_id = q.data.replace("admin_select_user_", "")
            context.user_data["admin_selected_user"] = user_id
            await admin_user_stats(update, context)
            
        elif q.data == "broadcast_all":
            await broadcast_all_users(update, context)
            
        elif q.data == "broadcast_rooms":
            await broadcast_room_users(update, context)
            
        elif q.data == "broadcast_cancel":
            await broadcast_cancel(update, context)
            
        elif q.data == "create_room_btn":
            if not is_admin(update):
                await q.answer("?? Только администратор может создавать комнаты!", show_alert=True)
                return
            await create_room(update, context)
            
        elif q.data == "checkers_confirm_win":
            await checkers_confirm_win(update, context)
            
        elif q.data == "checkers_confirm_loss":
            await checkers_confirm_loss(update, context)
            
        elif q.data == "checkers_stats":
            await checkers_stats(update, context)
            
        elif q.data == "checkers_help":
            await checkers_help(update, context)
            
        elif q.data == "back_menu":
            admin = is_admin(update)
            await q.edit_message_text(
                "?? Возвращаемся в главное меню...",
                reply_markup=enhanced_menu_keyboard(admin)
            )
            
        else:
            await q.answer("?? Эта функция временно недоступна", show_alert=True)
            
    except Exception as e:
        print(f"Ошибка в обработчике callback: {e}")
        await q.answer("? Произошла ошибка. Попробуйте позже.", show_alert=True)

# -------------------------------------------------------------------
# ?? ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
# -------------------------------------------------------------------
async def animated_snowfall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    # Создаем красивую анимацию снегопада
    snow_frames = [
        """
??       ??
   ??     ??
??     ??
   ??     ??
        """,
        """
   ??     ??
??     ??
   ??     ??
??     ??
        """,
        """
??     ??
   ??     ??
??     ??
   ??     ??
        """,
        """
   ??     ??
??     ??
   ??     ??
??     ??
        """
    ]
    
    message = await update.callback_query.edit_message_text("?? Подготовка волшебного снегопада...")
    
    # Анимация
    for i in range(6):
        frame = snow_frames[i % len(snow_frames)]
        text = f"?? <b>Волшебный снегопад</b> ??\n\n{frame}\n"
        
        # Добавляем прогресс
        snowflakes = "??" * (i + 1) + "?" * (5 - i)
        text += f"Снежинки: {snowflakes}\n\nИдет снегопад..."
        
        try:
            await message.edit_text(text, parse_mode='HTML')
            await asyncio.sleep(0.8)
        except:
            break
    
    # Финальное сообщение
    user = update.effective_user
    add_santa_points(user.id, 15, context)
    
    await message.edit_text(
        f"?? <b>Снегопад завершён!</b> ??\n\n"
        f"? Волшебство наполнило воздух!\n"
        f"?? +15 очков Санты за новогоднее настроение!\n\n"
        f"Земля покрыта сверкающим снегом... ???",
        parse_mode='HTML'
    )
    
    admin = is_admin(update)
    await asyncio.sleep(2)
    await update.callback_query.edit_message_text(
        "Выбери следующее действие:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def snowfall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Создаем начальное сообщение
    message = await update.message.reply_text("?? Запускаю волшебный снегопад...")
    
    # Красивая анимация снегопада
    snow_patterns = [
        "?????????????",
        "??????????????",
        "?????????????",
        "??????????????",
        "?????????????",
        "??????????????"
    ]
    
    for i in range(8):
        pattern = snow_patterns[i % len(snow_patterns)]
        text = f"?? <b>Волшебный снегопад</b> ??\n\n{pattern}\n{pattern}\n{pattern}\n\n"
        
        # Прогресс-бар
        progress = "??" * (i + 1) + "?" * (8 - i)
        text += f"Прогресс: {progress}"
        
        try:
            await message.edit_text(text, parse_mode='HTML')
            await asyncio.sleep(0.7)
        except:
            break
    
    # Финальное сообщение с наградой
    add_santa_points(user.id, 20, context)
    add_reindeer_exp(user.id, 10)
    
    await message.edit_text(
        f"?? <b>Снегопад завершён!</b> ??\n\n"
        f"? Волшебство наполнило воздух!\n"
        f"?? +20 очков Санты\n"
        f"?? +10 опыта оленёнку\n\n"
        f"Новогоднее настроение усилено! ??",
        parse_mode='HTML'
    )
    
    admin = is_admin(update)
    await update.message.reply_text(
        "Выбери следующее действие:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"?? Твой ID: {user.id}")

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    init_user_data(user.id)
    points = user_data[str(user.id)]["santa_points"]
    await update.message.reply_text(f"?? У тебя {points} очков Санты!")

# -------------------------------------------------------------------
# ?? ОСНОВНОЙ ЗАПУСК
# -------------------------------------------------------------------
def main():
    # Инициализация данных
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            pass
        print("?? Файл данных найден")
    except FileNotFoundError:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"rooms": {}, "users": {}}, f, indent=4, ensure_ascii=False)
        print("?? Создан новый файл данных")
    
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
    app.add_handler(CommandHandler("cancel", cancel_broadcast))

    # Обработчики callback'ов - ВАЖНО: правильный порядок!
    app.add_handler(CallbackQueryHandler(game_handlers, pattern="^(game_|coin_|battle_start|quiz_start)"))
    app.add_handler(CallbackQueryHandler(guess_handler, pattern="^guess_"))
    app.add_handler(CallbackQueryHandler(quiz_answer_handler, pattern="^quiz_answer_"))
    app.add_handler(CallbackQueryHandler(quiz_next_handler, pattern="^quiz_next$"))
    app.add_handler(CallbackQueryHandler(battle_action_handler, pattern="^battle_"))
    app.add_handler(CallbackQueryHandler(quest_start_handler, pattern="^quest_start_"))
    app.add_handler(CallbackQueryHandler(quest_action_handler, pattern="^quest_"))
    app.add_handler(CallbackQueryHandler(show_quest_achievements, pattern="^quest_achievements$"))
    app.add_handler(CallbackQueryHandler(checkers_help, pattern="^checkers_help$"))
    app.add_handler(CallbackQueryHandler(enhanced_inline_handler))

    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_broadcast_message))
    app.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND, handle_broadcast_message))
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_broadcast_message))

    print("?? Бот v3.1 запускается на Replit...")
    print("? ВСЕ функции исправлены и улучшены!")
    print("?? Баланс мини-игр - ? Исправлен")
    print("?? Битва с Гринчем - ? Улучшена")
    print("??? Квесты - ? Полностью работают") 
    print("?? Шашки - ? Логичная система подтверждения")
    print("?? Оптимизировано для Replit")
    
    # Запуск бота с обработкой ошибок для Replit
    try:
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    except KeyboardInterrupt:
        print("\n?? Бот остановлен")
    except Exception as e:
        print(f"? Критическая ошибка: {e}")
        # Для Replit - перезапуск при ошибке
        print("?? Перезапуск через 5 секунд...")
        import time
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()
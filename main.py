# 🔥🎄 SUPER-DELUXE SECRET SANTA BOT v2.0 🎄🔥
# УЛУЧШЕННАЯ ВЕРСИЯ: эпичная битва с Гринчем, продвинутые квесты, система очков, шашки!

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

TOKEN = "8299215190:AAEqLfMOTjywx_jOeT-Kv1I5oKdgbdWzN9Y"
ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"

print(f"🎄 Запуск Secret Santa Bot v2.0...")

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
# УЛУЧШЕННАЯ СИСТЕМА ОЧКОВ И ОЛЕНЕЙ
# -------------------------------------------------------------------
def init_user_data(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "reindeer_level": 0,
            "reindeer_exp": 0,
            "santa_points": 100,  # Новая валюта
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
            "total_points": 0
        }

def add_santa_points(user_id, points, context: ContextTypes.DEFAULT_TYPE = None):
    init_user_data(user_id)
    user_data[str(user_id)]["santa_points"] += points
    user_data[str(user_id)]["total_points"] += points
    
    # Уведомление о крупных выигрышах/проигрышах
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
        
        # РАСШИРЕННАЯ СИСТЕМА ЭВОЛЮЦИИ ОЛЕНЕЙ
        new_skin = None
        evolution_chance = random.random()
        
        if current_level + 1 == 3:
            if evolution_chance < 0.1:  # 10% шанс
                new_skin = "rainbow"
            elif evolution_chance < 0.02:  # 2% шанс
                new_skin = "ice_spirit"
        elif current_level + 1 == 4:
            if evolution_chance < 0.08:  # 8% шанс
                new_skin = "golden"
            elif evolution_chance < 0.015:  # 1.5% шанс
                new_skin = "crystal"
        elif current_level + 1 == 5:
            if evolution_chance < 0.05:  # 5% шанс
                new_skin = "cosmic"
            elif evolution_chance < 0.01:  # 1% шанс
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
        # Награда за достижение
        add_santa_points(user_id, 50)

# -------------------------------------------------------------------
# УЛУЧШЕННЫЙ ГЕНЕРАТОР ИДЕЙ ПОДАРКОВ
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
# ЭПИЧНАЯ БИТВА С ГРИНЧЕМ v2.0
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
⚔️ ЭПИЧНАЯ БИТВА С ГРИНЧЕМ - Раунд {battle_state['round']}

❤️ Твоё HP: {player['hp']} ⚡ Атака: {player['attack']} 🛡 Защита: {player['defense']}
💚 HP Гринча: {grinch['hp']} ⚡ Атака: {grinch['attack']} 🛡 Защита: {grinch['defense']}

✨ Особые умения: {player['special_charges']} зарядов

Выбери действие:
"""
    
    keyboard = [
        [InlineKeyboardButton("⚔️ Атаковать", callback_data="battle_attack")],
        [InlineKeyboardButton("🛡 Укрепить защиту", callback_data="battle_defend")],
        [InlineKeyboardButton("✨ Новогоднее волшебство", callback_data="battle_special")],
        [InlineKeyboardButton("🏃 Сбежать", callback_data="battle_flee")]
    ]
    
    await update.callback_query.edit_message_text(battle_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        battle_log.append(f"✨ Новогоднее волшебство! Исцеление +{hele}, Гринч получает 15 урона!")
        
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
🎉 ПОБЕДА НАД ГРИНЧЕМ! 🎉

{' '.join(battle_log)}

✨ Награды:
• +{points_earned} очков Санты
• +40 опыта оленёнку
• Звание Защитника Рождества!

Гринч повержен, и Новый Год спасён! 🎄
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Сразиться снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(victory_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_defeat(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_log):
    user = update.effective_user
    points_lost = random.randint(30, 60)
    add_santa_points(user.id, -points_lost, context)
    
    defeat_text = f"""
💔 ПОРАЖЕНИЕ...

{' '.join(battle_log)}

😔 Потеряно: {points_lost} очков Санты

Не сдавайся! Гринч должен быть остановлен! 🎅
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Попробовать снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(defeat_text, reply_markup=InlineKeyboardMarkup(keyboard))

# -------------------------------------------------------------------
# УЛУЧШЕННЫЕ КВЕСТЫ С ВЕТВЛЕНИЕМ
# -------------------------------------------------------------------
async def enhanced_quest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
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
        "🏔️ Эпические новогодние квесты!\n\n"
        "Выбери квест для прохождения. За выполнение получишь:\n"
        "• Очки Санты 🎅\n• Опыт оленёнка 🦌\n• Редкие предметы ✨",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_enhanced_quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    quest_id = q.data.replace("quest_start_", "")
    context.user_data["current_quest"] = quest_id
    context.user_data["quest_progress"] = 0
    
    quest_stories = {
        "frozen_runes": {
            "start": "❄️ Ты находишь древний свиток с замерзшими рунами...",
            "options": [
                {"text": "🔍 Исследовать руны магии", "next": "magic"},
                {"text": "🔥 Растопить лёд огнём", "next": "fire"},
                {"text": "🎵 Способ магической песни", "next": "song"}
            ]
        },
        "gift_rescue": {
            "start": "🎁 Гринч украл все подарки! Нужно спасти их...",
            "options": [
                {"text": "🚀 Быстрая атака", "next": "attack"},
                {"text": "🕵️ Тихая инфильтрация", "next": "stealth"},
                {"text": "🎪 Отвлекающий манёвр", "next": "distract"}
            ]
        }
    }
    
    story = quest_stories.get(quest_id, quest_stories["frozen_runes"])
    
    keyboard = []
    for option in story["options"]:
        keyboard.append([InlineKeyboardButton(option["text"], callback_data=f"quest_choice_{option['next']}")])
    
    await q.edit_message_text(
        story["start"] + "\n\nВыбери свой подход:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def process_quest_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    choice = q.data.replace("quest_choice_", "")
    quest_id = context.user_data["current_quest"]
    
    # Логика квеста с разными исходами
    outcomes = {
        "magic": {"success": 0.8, "text": "✨ Магия сработала! Руны ожили и открыли секрет.", "points": 60},
        "fire": {"success": 0.5, "text": "🔥 Лёд растаял, но некоторые руны повредились.", "points": 40},
        "song": {"success": 0.9, "text": "🎵 Волшебная песня мягко разбудила магию рун!", "points": 70},
        "attack": {"success": 0.6, "text": "⚔️ Атака удалась! Гринч в замешательстве.", "points": 50},
        "stealth": {"success": 0.7, "text": "🕵️ Ты незаметно проник и забрал подарки!", "points": 80},
        "distract": {"success": 0.4, "text": "🎪 Манёвр отвлёк Гринча, но он всё ещё опасен.", "points": 30}
    }
    
    outcome = outcomes.get(choice, outcomes["magic"])
    success = random.random() < outcome["success"]
    
    user = update.effective_user
    init_user_data(user.id)
    
    if success:
        points = outcome["points"]
        add_santa_points(user.id, points, context)
        add_reindeer_exp(user.id, 35)
        user_data[str(user.id)]["quests_finished"] += 1
        
        # Шанс на редкий предмет
        if random.random() < 0.3:
            rare_items = ["❄️ Ледяной кристалл", "✨ Пыльца северного сияния", "🌟 Звёздный фрагмент"]
            rare_item = random.choice(rare_items)
            user_data[str(user.id)]["rare_items"].append(rare_item)
            item_text = f"\n\n🎁 Найден редкий предмет: {rare_item}!"
        else:
            item_text = ""
        
        await q.edit_message_text(
            f"🎉 УСПЕХ!\n\n{outcome['text']}\n\n"
            f"✨ Награды:\n"
            f"• +{points} очков Санты\n"
            f"• +35 опыта оленёнку\n"
            f"• Прогресс в приключениях!{item_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎪 Ещё квесты", callback_data="quest_menu")],
                [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
            ])
        )
    else:
        points_lost = random.randint(20, 40)
        add_santa_points(user.id, -points_lost, context)
        
        await q.edit_message_text(
            f"💔 НЕУДАЧА...\n\n{outcome['text']}\n\n"
            f"Потеряно: {points_lost} очков Санты\n\n"
            f"Не сдавайся! Попробуй другой подход!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"quest_start_{quest_id}")],
                [InlineKeyboardButton("🎪 Другие квесты", callback_data="quest_menu")]
            ])
        )

# -------------------------------------------------------------------
# СИСТЕМА ШАШЕК (базовая реализация)
# -------------------------------------------------------------------
async def checkers_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    await q.edit_message_text(
        "♟️ Вызов на шашки\n\n"
        "Чтобы сыграть в шашки с другим участником:\n\n"
        "1. Узнай его ID (он может получить его через /myid)\n"
        "2. Используй команду:\n"
        "   /challenge @username\n\n"
        "Или напиши мне ID пользователя:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🆔 Мой ID", callback_data="get_my_id")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="mini_games")]
        ])
    )

async def start_checkers_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Базовая реализация вызова
    if context.args:
        target = context.args[0]
        challenger = update.effective_user
        
        await update.message.reply_text(
            f"♟️ {challenger.first_name} вызывает на шашки пользователя {target}!\n\n"
            f"Игра будет реализована в следующем обновлении! 🎮"
        )

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.callback_query.edit_message_text(
        f"🆔 Твой ID: {user.id}\n\n"
        f"Дай этот ID другу, чтобы он мог вызвать тебя на шашки!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад к шашкам", callback_data="game_checkers")]
        ])
    )

# -------------------------------------------------------------------
# ОБНОВЛЁННЫЕ МЕНЮ И ОБРАБОТЧИКИ
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
    if admin:
        base.extend([
            [InlineKeyboardButton("🎄 Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("🚀 Админ: Запуск игры", callback_data="admin_start")],
            [InlineKeyboardButton("📜 Админ: Пожелания", callback_data="admin_wishes")],
            [InlineKeyboardButton("🔀 Админ: Кому кто", callback_data="admin_map")],
        ])
    base.append([InlineKeyboardButton("🎅 Присоединиться к комнате", callback_data="join_room_menu")])
    return InlineKeyboardMarkup(base)

async def enhanced_gift_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idea = generate_gift_idea()
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"🎁 Идея подарка:\n\n{idea}\n\n"
        f"💡 Совет: учитывай интересы получателя!",
        reply_markup=back_to_menu_keyboard()
    )

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
🎅 Профиль игрока @{user.username if user.username else user.first_name}

💫 Очки Санты: {user_info['santa_points']}
🦌 Твой олень: {reindeer_text}
🎨 Вид: {skin_text}
📊 Опыт: {reindeer_exp}/{(reindeer_level + 1) * 100}

🎖 Достижения: {len(user_info['achievements'])}
🎮 Побед в играх: {user_info['games_won']}
🏔 Пройдено квестов: {user_info['quests_finished']}
⚔️ Побед над Гринчем: {user_info['grinch_wins']}

💎 Редких предметов: {len(user_info['rare_items'])}
♟️ Побед в шашках: {user_info.get('checkers_wins', 0)}
"""

    if update.callback_query:
        await update.callback_query.edit_message_text(
            profile_text, 
            reply_markup=back_to_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            profile_text, 
            reply_markup=back_to_menu_keyboard()
        )

# -------------------------------------------------------------------
# ОБНОВЛЁННЫЕ ОБРАБОТЧИКИ ИГР
# -------------------------------------------------------------------
async def enhanced_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "game_number":
        num = random.randint(1, 5)
        context.user_data["guess_num"] = num
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1,6)],
            [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
        ])
        await q.edit_message_text("🎯 Я загадал число от 1 до 5. Угадай!", reply_markup=kb)

    elif q.data.startswith("guess_"):
        guess = int(q.data.split("_")[1])
        real = context.user_data.get("guess_num")
        user = update.effective_user
        init_user_data(user.id)
        
        if guess == real:
            points = random.randint(25, 50)
            add_santa_points(user.id, points, context)
            user_data[str(user.id)]["games_won"] += 1
            add_reindeer_exp(user.id, 15)
            await q.edit_message_text(
                f"🎉 Верно! Получено {points} очков Санты!",
                reply_markup=back_to_menu_keyboard()
            )
        else:
            points_lost = random.randint(10, 20)
            add_santa_points(user.id, -points_lost, context)
            await q.edit_message_text(
                f"❄️ Не угадал! Было число {real}. Потеряно {points_lost} очков.",
                reply_markup=back_to_menu_keyboard()
            )

    elif q.data == "game_coin":
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
                await q.edit_message_text(
                    f"🧊 Монетка: {side}! +{points} очков\n\n"
                    f"🎉 5 побед подряд! Достижение 'Монетка Удачи'!", 
                    reply_markup=back_to_menu_keyboard()
                )
                context.user_data["coin_wins"] = 0
            else:
                await q.edit_message_text(
                    f"🧊 Монетка: {side}! +{points} очков\n"
                    f"Серия побед: {context.user_data['coin_wins']}", 
                    reply_markup=back_to_menu_keyboard()
                )
        else:
            points_lost = random.randint(5, 15)
            add_santa_points(user.id, -points_lost, context)
            context.user_data["coin_wins"] = 0
            await q.edit_message_text(
                f"🧊 Монетка: {side}! Потеряно {points_lost} очков", 
                reply_markup=back_to_menu_keyboard()
            )

    elif q.data == "game_grinch":
        await epic_grinch_battle(update, context)
        
    elif q.data == "game_checkers":
        await checkers_challenge(update, context)
        
    elif q.data == "battle_attack":
        await battle_action(update, context)
        
    elif q.data == "battle_defend":
        await battle_action(update, context)
        
    elif q.data == "battle_special":
        await battle_action(update, context)
        
    elif q.data == "battle_flee":
        await battle_action(update, context)
        
    elif q.data == "battle_continue":
        await show_battle_interface(update, context)
        
    elif q.data == "get_my_id":
        await get_my_id(update, context)

# -------------------------------------------------------------------
# ОБНОВЛЁННЫЙ INLINE ОБРАБОТЧИК
# -------------------------------------------------------------------
async def enhanced_inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "wish":
        await wish_start(update, context)

    elif q.data == "toast":
        await q.edit_message_text(
            f"✨ Тост дня:\n{toast_of_day()}", 
            reply_markup=back_to_menu_keyboard()
        )

    elif q.data == "admin_rooms":
        if not is_admin(update): 
            await q.edit_message_text("🚫 Доступ запрещён.")
            return
        # ... остальной код админ-панели

    elif q.data == "quest_menu":
        await enhanced_quest_menu(update, context)
        
    elif q.data.startswith("quest_start_"):
        await start_enhanced_quest(update, context)
        
    elif q.data.startswith("quest_choice_"):
        await process_quest_choice(update, context)
        
    elif q.data == "gift_idea":
        await enhanced_gift_idea(update, context)
        
    elif q.data == "profile":
        await enhanced_profile(update, context)
        
    elif q.data == "mini_games":
        await mini_game_menu(update, context)
        
    elif q.data == "back_menu":
        admin = is_admin(update)
        await q.edit_message_text(
            "🎄 Возвращаемся в главное меню...",
            reply_markup=enhanced_menu_keyboard(admin)
        )

# -------------------------------------------------------------------
# ДОБАВЛЯЕМ НОВЫЕ КОМАНДЫ
# -------------------------------------------------------------------
async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 Твой ID: {user.id}")

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    init_user_data(user.id)
    points = user_data[str(user.id)]["santa_points"]
    await update.message.reply_text(f"🎅 У тебя {points} очков Санты!")

# -------------------------------------------------------------------
# ОСНОВНОЙ ЗАПУСК
# -------------------------------------------------------------------
def main():
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
    app.add_handler(CommandHandler("challenge", start_checkers_game))

    # Обработчики callback'ов
    app.add_handler(CallbackQueryHandler(enhanced_inline_handler, pattern="^(wish|toast|admin_rooms|admin_wishes|admin_map|admin_start|profile|mini_games|quest_menu|gift_idea|snowfall|back_menu|join_room_menu|top_players|room_members)$"))
    app.add_handler(CallbackQueryHandler(enhanced_game_handler, pattern="^game"))
    app.add_handler(CallbackQueryHandler(enhanced_game_handler, pattern="^battle"))
    app.add_handler(CallbackQueryHandler(enhanced_game_handler, pattern="^guess"))
    app.add_handler(CallbackQueryHandler(enhanced_game_handler, pattern="^get_my_id"))
    app.add_handler(CallbackQueryHandler(start_enhanced_quest, pattern="^quest_start"))
    app.add_handler(CallbackQueryHandler(process_quest_choice, pattern="^quest_choice"))
    app.add_handler(CallbackQueryHandler(start_specific_game, pattern="^start_"))

    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, join_room))

    print("🎄 Бот v2.0 запускается...")
    print("✨ Улучшенная битва с Гринчем, квесты, система очков!")
    
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

if __name__ == "__main__":
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            pass
        print("📁 Файл данных найден")
    except FileNotFoundError:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"rooms": {}, "users": {}}, f, indent=4, ensure_ascii=False)
        print("📁 Создан новый файл данных")
    
    main()
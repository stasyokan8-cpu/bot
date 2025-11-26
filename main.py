"""
Secret Santa — Full Replit-ready bot
Features:
- Uses TELEGRAM_BOT_TOKEN from Replit Secrets
- keep_alive using Flask for UptimeRobot
- Polling via Application.run_polling() (no asyncio.run)
- Rooms, wishes, invites
- Admin-only actions for @BeellyKid
- Personal reindeer per user + leveling
- Achievements
- Mini-games, quest, animated snowfall buttons
- Gift idea generator
- Simple reminder loop (background thread)

Drop this file as `main.py` on Replit, set TELEGRAM_BOT_TOKEN secret and press Run.
"""

import os
import json
import random
import string
import time
from threading import Thread
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# -------------------- CONFIG --------------------
ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"
KEEPALIVE_PORT = int(os.environ.get("PORT", 8080))

# -------------------- KEEP ALIVE --------------------
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app_flask.run(host='0.0.0.0', port=KEEPALIVE_PORT)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

# -------------------- DATA --------------------

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"rooms": {}, "users": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- HELPERS --------------------

def gen_room_code(n=5):
    return 'R' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

def is_admin(user):
    return getattr(user, 'username', '') == ADMIN_USERNAME

# Reindeer stages
REINDEER_STAGES = [
    "🦌 Маленький оленёк (0 ур.) — только вылупился!",
    "🦌💨 Оленёк-подросток (1 ур.) — резвится по снегу!",
    "🦌✨ Звёздный олень (2 ур.) — рога сияют!",
    "🦌🔥 Легендарный олень (3 ур.) — готов к приключениям!"
]

ACHIEVEMENTS = {
    "snow_hero": "🏆 Снежный Герой — прошёл главный квест!",
    "grinch_slayer": "🎄⚔️ Гроза Гринча — победил Гринча!",
    "reindeer_master": "🦌✨ Повелитель Оленей — оленёнок lvl 3!",
    "lucky_coin": "🍀 Монетка Удачи — везение бьёт ключом!"
}

# -------------------- BOT INIT --------------------
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print('❌ TELEGRAM_BOT_TOKEN not set. Add it to Replit Secrets.')
    raise SystemExit(1)

app = ApplicationBuilder().token(TOKEN).build()

data = load_data()
# ensure structures
if 'rooms' not in data:
    data['rooms'] = {}
if 'users' not in data:
    data['users'] = {}

# -------------------- COMMANDS --------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    # ensure user record
    if uid not in data['users']:
        data['users'][uid] = {
            'reindeer_level': 0,
            'reindeer_exp': 0,
            'achievements': [],
            'quests_finished': 0,
            'games_won': 0,
            'coin_streak': 0
        }
        save_data(data)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('🎁 Создать комнату', callback_data='create_room')],
        [InlineKeyboardButton('🔗 Присоединиться', callback_data='join_room')],
        [InlineKeyboardButton('🦌 Мой оленёнок', callback_data='my_reindeer')],
        [InlineKeyboardButton('🎮 Мини-игры', callback_data='mini_games')],
    ])
    await update.message.reply_text(
        f"🎄 Привет, {user.first_name}! Добро пожаловать в Тайного Санту — версия Replit.\nУправление через кнопки ниже.",
        reply_markup=kb
    )

app.add_handler(CommandHandler('start', cmd_start))

# Create room
async def cmd_create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    code = gen_room_code()
    data['rooms'][code] = {
        'name': f"Комната {code}",
        'owner_id': user.id,
        'participants': {},  # uid -> {username,name,wish}
        'started': False,
        'assignments': {},
        'deadline': (datetime.utcnow() + timedelta(days=2)).isoformat()
    }
    save_data(data)
    await update.effective_message.reply_text(f"🎉 Комната создана: {code}\nОтправь код друзьям или используй приглашение.")

app.add_handler(CommandHandler('create_room', cmd_create_room))

# Join room
async def cmd_join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Использование: /join_room RXXXXX')
        return
    code = args[0].upper()
    if code not in data['rooms']:
        await update.message.reply_text('❌ Комната не найдена')
        return
    room = data['rooms'][code]
    if room['started']:
        await update.message.reply_text('Игра уже началась — присоединиться нельзя')
        return
    uid = str(update.effective_user.id)
    room['participants'][uid] = {
        'username': update.effective_user.username or '',
        'name': update.effective_user.full_name,
        'wish': ''
    }
    save_data(data)
    await update.message.reply_text(f"✅ Вы присоединились к комнате {code}. Напишите /wish, чтобы сохранить пожелание.")

app.add_handler(CommandHandler('join_room', cmd_join_room))

# Invite
async def cmd_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Использование: /invite RXXXXX')
        return
    code = args[0].upper()
    if code not in data['rooms']:
        await update.message.reply_text('Комната не найдена')
        return
    await update.message.reply_text(f"🔗 Приглашение: Открой бота и введи код {code} или используйте /join_room {code}")

app.add_handler(CommandHandler('invite', cmd_invite))

# Wish
async def cmd_wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Напишите ваше пожелание. После старта игры изменить нельзя.')
    context.user_data['awaiting_wish'] = True

app.add_handler(CommandHandler('wish', cmd_wish_start))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if context.user_data.get('awaiting_wish'):
        # find latest room where user is participant and not started
        for code, room in data['rooms'].items():
            if uid in room['participants'] and not room['started']:
                room['participants'][uid]['wish'] = update.message.text
                save_data(data)
                context.user_data['awaiting_wish'] = False
                await update.message.reply_text('✅ Пожелание сохранено!')
                # add reindeer exp for activity
                add_reindeer_exp(uid, 5)
                return
        await update.message.reply_text('Вы не в комнате или игра уже началась.')
        context.user_data['awaiting_wish'] = False
        return

    await update.message.reply_text('Не понял. Попробуйте /start')

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# Mygiftee
async def cmd_mygiftee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    for code, room in data['rooms'].items():
        if uid in room['participants']:
            if not room['started']:
                await update.message.reply_text('Игра ещё не началась')
                return
            receiver = room['assignments'].get(uid)
            if not receiver:
                await update.message.reply_text('Назначение не найдено')
                return
            r = room['participants'][receiver]
            await update.message.reply_text(f"🎁 Ты даришь: {r['name']} (@{r.get('username','')})\nПожелание: {r.get('wish','(пусто)')}")
            return
    await update.message.reply_text('Вы не состоите ни в одной комнате')

app.add_handler(CommandHandler('mygiftee', cmd_mygiftee))

# Start game (admin)
async def cmd_start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        await update.message.reply_text('🚫 Только админ может запускать игру')
        return
    args = context.args
    if not args:
        await update.message.reply_text('Использование: /start_game RXXXXX')
        return
    code = args[0].upper()
    if code not in data['rooms']:
        await update.message.reply_text('Комната не найдена')
        return
    room = data['rooms'][code]
    if room['started']:
        await update.message.reply_text('Игра уже запущена')
        return
    participants = list(room['participants'].keys())
    if len(participants) < 2:
        await update.message.reply_text('Нужно минимум 2 участника')
        return
    random.shuffle(participants)
    assignments = {}
    for i, giver in enumerate(participants):
        receiver = participants[(i+1) % len(participants)]
        assignments[giver] = receiver
    room['assignments'] = assignments
    room['started'] = True
    save_data(data)
    # notify
    for giver, receiver in assignments.items():
        try:
            r = room['participants'][receiver]
            await app.bot.send_message(int(giver), f"🎁 Твой получатель: {r['name']} (@{r.get('username','')})\nПожелание: {r.get('wish','(пусто)')}")
        except Exception:
            pass
    await update.message.reply_text('✅ Игра запущена и игроки уведомлены')

app.add_handler(CommandHandler('start_game', cmd_start_game))

# Admin views
async def cmd_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        await update.message.reply_text('🚫 Только админ')
        return
    args = context.args
    if not args:
        await update.message.reply_text('Использование: /members RXXXXX')
        return
    code = args[0].upper()
    if code not in data['rooms']:
        await update.message.reply_text('Комната не найдена')
        return
    room = data['rooms'][code]
    text = f"Комната {code} — участники:\n"
    for uid, p in room['participants'].items():
        text += f"• {p.get('name')} @{p.get('username','')} (id {uid})\n"
    await update.message.reply_text(text)

app.add_handler(CommandHandler('members', cmd_members))

# Assignments (admin view)
async def cmd_assignments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        await update.message.reply_text('🚫 Только админ')
        return
    args = context.args
    if not args:
        await update.message.reply_text('Использование: /assignments RXXXXX')
        return
    code = args[0].upper()
    if code not in data['rooms']:
        await update.message.reply_text('Комната не найдена')
        return
    room = data['rooms'][code]
    if not room.get('started'):
        await update.message.reply_text('Игра ещё не началась')
        return
    text = f"Распределение в комнате {code}:\n"
    for g, r in room['assignments'].items():
        gv = room['participants'].get(g, {})
        rv = room['participants'].get(r, {})
        text += f"• {gv.get('name')} -> {rv.get('name')}\n"
    await update.message.reply_text(text)

app.add_handler(CommandHandler('assignments', cmd_assignments))

# -------------------- PROFILE & REINDEER --------------------

def add_reindeer_exp(uid, amount):
    # uid is string
    u = data['users'].setdefault(uid, {
        'reindeer_level': 0,
        'reindeer_exp': 0,
        'achievements': [],
        'quests_finished': 0,
        'games_won': 0,
        'coin_streak': 0
    })
    u['reindeer_exp'] = u.get('reindeer_exp', 0) + amount
    # simple thresholds
    thresholds = [0, 20, 60, 150]
    lvl = u.get('reindeer_level', 0)
    while lvl < len(thresholds)-1 and u['reindeer_exp'] >= thresholds[lvl+1]:
        lvl += 1
        u['reindeer_level'] = lvl
        # award achievement at max
        if lvl >= 3 and 'reindeer_master' not in u['achievements']:
            u['achievements'].append('reindeer_master')
    save_data(data)

async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    u = data['users'].get(uid, {})
    lvl = u.get('reindeer_level', 0)
    exp = u.get('reindeer_exp', 0)
    ach = u.get('achievements', [])
    msg = (
        f"🎅 *Профиль игрока* @{update.effective_user.username}\n\n"
        f"🦌 *Твой оленёнок:* {REINDEER_STAGES[min(lvl, len(REINDEER_STAGES)-1)]}\n\n"
        f"🎖 *Достижения:* {'; '.join([ACHIEVEMENTS.get(a,a) for a in ach]) if ach else 'Нет'}\n\n"
        f"🎮 Статистика:\n• Побед в мини-играх: {u.get('games_won',0)}\n"
        f"• Пройдено квестов: {u.get('quests_finished',0)}\n"
        f"• Опыт оленёнка: {exp} XP"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

app.add_handler(CommandHandler('profile', cmd_profile))

# -------------------- MINI-GAMES & QUESTS --------------------

async def callback_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data_cb = q.data

    # create room shortcut
    if data_cb == 'create_room':
        # emulate command
        class FakeMsg: pass
        fake = FakeMsg(); fake.effective_user = q.from_user; fake.message = q.message
        await cmd_create_room(q, context)
        return

    if data_cb == 'join_room':
        await q.edit_message_text('Отправьте /join_room RXXXXX или используйте /join_room <код>')
        return

    if data_cb == 'my_reindeer':
        await cmd_profile(q, context)
        return

    if data_cb == 'mini_games':
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton('🎯 Угадай число', callback_data='game_number')],
            [InlineKeyboardButton('🧊 Монетка', callback_data='game_coin')],
            [InlineKeyboardButton('🧭 Квест', callback_data='quest_menu')],
            [InlineKeyboardButton('❄️ Снегопад (аним)', callback_data='animated_snow')],
            [InlineKeyboardButton('🎁 Идея подарка', callback_data='gift_idea')]
        ])
        await q.edit_message_text('Выберите мини-игру:', reply_markup=kb)
        return

    # games
    if data_cb == 'game_number':
        n = random.randint(1,5)
        context.user_data['secret_number'] = n
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f'guess_{i}') for i in range(1,6)]])
        await q.edit_message_text('Я загадал число от 1 до 5 — угадай!', reply_markup=kb)
        return
    if data_cb.startswith('guess_'):
        guess = int(data_cb.split('_')[1])
        real = context.user_data.get('secret_number')
        if guess == real:
            # reward exp
            uid = str(q.from_user.id)
            add_reindeer_exp(uid, 10)
            data['users'].setdefault(uid, {}).setdefault('games_won', 0)
            data['users'][uid]['games_won'] = data['users'][uid].get('games_won',0) + 1
            save_data(data)
            await q.edit_message_text('🎉 Верно! Ты получил 10 XP для оленёнка')
        else:
            await q.edit_message_text(f'❌ Неправильно — было {real}')
        return

    if data_cb == 'game_coin':
        side = random.choice(['Орёл 🦅', 'Решка ❄️'])
        uid = str(q.from_user.id)
        # streak
        u = data['users'].setdefault(uid, {})
        if side.startswith('Орёл'):
            u['coin_streak'] = u.get('coin_streak',0) + 1
            if u['coin_streak'] >= 5 and 'lucky_coin' not in u.get('achievements',[]):
                u.setdefault('achievements',[]).append('lucky_coin')
        else:
            u['coin_streak'] = 0
        save_data(data)
        await q.edit_message_text(f'🧊 Выпало: {side}')
        return

    if data_cb == 'quest_menu':
        kb = InlineKeyboardMarkup([[InlineKeyboardButton('🎄 Начать квест', callback_data='quest_start')]])
        await q.edit_message_text('✨ Новогодний квест — пройди три этапа!', reply_markup=kb)
        return

    if data_cb == 'quest_start':
        # stage 1
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton('✨ Сияющая тропа', callback_data='quest_light')],
            [InlineKeyboardButton('🌑 Тёмная тропа', callback_data='quest_dark')]
        ])
        await q.edit_message_text('Глава 1: Перед тобой две тропы', reply_markup=kb)
        return

    if data_cb in ('quest_light', 'quest_dark'):
        uid = str(q.from_user.id)
        u = data['users'].setdefault(uid, {})
        # reward and proceed
        if data_cb == 'quest_light':
            u.setdefault('achievements',[]).append('snow_hero')
            await q.edit_message_text('✨ Ты выбрал свет — получил Медаль Снежного Героя!')
        else:
            u.setdefault('achievements',[]).append('grinch_slayer')
            await q.edit_message_text('🌑 Тёмная тропа — ты победил Гринча!')
        # finish quest
        u['quests_finished'] = u.get('quests_finished',0) + 1
        add_reindeer_exp(uid, 15)
        save_data(data)
        return

    if data_cb == 'animated_snow':
        frames = ['❄️','✨','❅','☃️']
        for i in range(8):
            fl = random.choice(frames)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f'{fl} Снежинка {i+1}', callback_data='noop')]])
            try:
                await q.edit_message_reply_markup(reply_markup=kb)
            except Exception:
                pass
            time.sleep(0.25)
        await q.edit_message_text('❄️ Снегопад окончен!')
        return

    if data_cb == 'gift_idea':
        ideas = [
            'Беспроводные наушники — для музыки под ёлкой',
            'Тёплый плед с оленями',
            'Настольная игра для весёлой компании',
            'Подарочная коробка шоколада и печенья',
            'Абонемент в курс по интересам'
        ]
        await q.edit_message_text(f'🎁 Идея подарка: {random.choice(ideas)}')
        return

    # noop
    await q.answer()

app.add_handler(CallbackQueryHandler(callback_inline))

# -------------------- REMINDER LOOP (background) --------------------

def reminder_loop():
    while True:
        try:
            now = datetime.utcnow()
            for code, room in data['rooms'].items():
                if room.get('started'):
                    continue
                deadline = datetime.fromisoformat(room.get('deadline'))
                # remind if within 1 hour
                if now + timedelta(hours=1) > deadline and now < deadline:
                    for uid in room['participants'].keys():
                        try:
                            app.bot.send_message(int(uid), f'⏰ Напоминание: до дедлайна комнаты {code} остался ~1 час')
                        except Exception:
                            pass
            time.sleep(3600)
        except Exception:
            time.sleep(60)

# run reminder thread
rem_thread = Thread(target=reminder_loop, daemon=True)
rem_thread.start()

# -------------------- RUN --------------------
if __name__ == '__main__':
    keep_alive()
    print('✅ Бот запускается — polling...')
    app.run_polling()

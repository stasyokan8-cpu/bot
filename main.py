"""
main.py — Secret Santa Replit-ready

Instructions:
1) Add secret TELEGRAM_BOT_TOKEN in Replit Secrets (Environment Variables).
2) Paste this file as main.py in Replit.
3) Press Run.
4) Add an UptimeRobot monitor to https://<your-repl>.repl.co/ every 5 minutes to keep the repl alive.
"""

import os
import json
import random
import string
import asyncio
from threading import Thread
from datetime import datetime, timedelta, timezone
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

# ---------------- CONFIG ----------------
ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"
KEEPALIVE_PORT = int(os.environ.get("PORT", 8080))
# ----------------------------------------

# -------------- KEEP ALIVE (Flask) --------------
app_flask = Flask(__name__)


@app_flask.route("/")
def home():
    return "Bot is alive!"


def run_web():
    app_flask.run(host="0.0.0.0", port=KEEPALIVE_PORT)


def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()


# -------------- DATA STORAGE --------------
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"rooms": {}, "users": {}}
    except Exception:
        return {"rooms": {}, "users": {}}


def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


data = load_data()
data.setdefault("rooms", {})
data.setdefault("users", {})


# -------------- HELPERS --------------
def gen_room_code(n=5):
    return "R" + "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


def is_admin(user):
    return getattr(user, "username", "") == ADMIN_USERNAME


REINDEER_STAGES = [
    "🦌 Маленький оленёк (0 ур.) — только вылупился!",
    "🦌💨 Оленёк-подросток (1 ур.) — резвится по снегу!",
    "🦌✨ Звёздный олень (2 ур.) — рога сияют!",
    "🦌🔥 Легендарный олень (3 ур.) — готов к приключениям!",
]

ACHIEVEMENTS = {
    "snow_hero": "🏆 Снежный Герой — прошёл главный квест!",
    "grinch_slayer": "🎄⚔️ Гроза Гринча — победил Гринча!",
    "reindeer_master": "🦌✨ Повелитель Оленей — оленёнок lvl 3!",
    "lucky_coin": "🍀 Монетка Удачи — везение бьёт ключом!",
}


def ensure_user_record(uid: str):
    u = data["users"].setdefault(uid, {})
    u.setdefault("reindeer_level", 0)
    u.setdefault("reindeer_exp", 0)
    u.setdefault("achievements", [])
    u.setdefault("quests_finished", 0)
    u.setdefault("games_won", 0)
    u.setdefault("coin_streak", 0)
    save_data(data)


def add_reindeer_exp(uid: str, amount: int):
    ensure_user_record(uid)
    u = data["users"][uid]
    u["reindeer_exp"] = u.get("reindeer_exp", 0) + amount
    thresholds = [0, 20, 60, 150]
    lvl = u.get("reindeer_level", 0)
    while lvl < len(thresholds) - 1 and u["reindeer_exp"] >= thresholds[lvl + 1]:
        lvl += 1
        u["reindeer_level"] = lvl
        if lvl >= 3 and "reindeer_master" not in u.get("achievements", []):
            u["achievements"].append("reindeer_master")
    save_data(data)


def create_room_for_user(user):
    code = gen_room_code()
    data["rooms"][code] = {
        "name": f"Комната {code}",
        "owner_id": user.id,
        "participants": {},
        "started": False,
        "assignments": {},
        "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
    }
    save_data(data)
    return code


# -------------- BOT INITIALIZATION --------------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not set. Add it to Replit Secrets.")
    raise SystemExit(1)

app = ApplicationBuilder().token(TOKEN).build()


# -------------- REMINDERS using JobQueue --------------
async def reminders_job(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(timezone.utc)
    for code, room in data["rooms"].items():
        if room.get("started"):
            continue
        try:
            deadline = datetime.fromisoformat(room.get("deadline"))
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if now + timedelta(hours=1) > deadline and now < deadline:
            for uid in room["participants"].keys():
                try:
                    await context.bot.send_message(int(uid), f"⏰ Напоминание: до дедлайна комнаты {code} остался ~1 час")
                except Exception:
                    pass


if app.job_queue:
    app.job_queue.run_repeating(reminders_job, interval=30 * 60, first=10)


# ---------------- COMMANDS ----------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    ensure_user_record(uid)
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎁 Создать комнату", callback_data="create_room")],
            [InlineKeyboardButton("🔗 Присоединиться", callback_data="join_room")],
            [InlineKeyboardButton("🦌 Мой оленёнок", callback_data="my_reindeer")],
            [InlineKeyboardButton("🎮 Мини-игры", callback_data="mini_games")],
        ]
    )
    await update.message.reply_text(
        f"🎄 Привет, {user.first_name}! Добро пожаловать в Тайного Санту — версия Replit.\nУправление через кнопки ниже.",
        reply_markup=kb,
    )


app.add_handler(CommandHandler("start", cmd_start))


# ---------------- ROOM COMMANDS ----------------
async def cmd_create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    code = create_room_for_user(user)
    await update.effective_message.reply_text(
        f"🎉 Комната создана: {code}\nОтправь код друзьям или используй приглашение."
    )


app.add_handler(CommandHandler("create_room", cmd_create_room))


async def cmd_join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /join_room RXXXXX")
        return
    code = args[0].upper()
    if code not in data["rooms"]:
        await update.message.reply_text("❌ Комната не найдена")
        return
    room = data["rooms"][code]
    if room["started"]:
        await update.message.reply_text("Игра уже началась — присоединиться нельзя")
        return
    uid = str(update.effective_user.id)
    room["participants"][uid] = {
        "username": update.effective_user.username or "",
        "name": update.effective_user.full_name,
        "wish": "",
    }
    save_data(data)
    ensure_user_record(uid)
    await update.message.reply_text(
        f"✅ Вы присоединились к комнате {code}. Напишите /wish, чтобы сохранить пожелание."
    )


app.add_handler(CommandHandler("join_room", cmd_join_room))


async def cmd_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /invite RXXXXX")
        return
    code = args[0].upper()
    if code not in data["rooms"]:
        await update.message.reply_text("Комната не найдена")
        return
    await update.message.reply_text(
        f"🔗 Приглашение: Открой бота и введи код {code} или используйте /join_room {code}"
    )


app.add_handler(CommandHandler("invite", cmd_invite))


async def cmd_wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напишите ваше пожелание. После старта игры изменить нельзя.")
    context.user_data["awaiting_wish"] = True


app.add_handler(CommandHandler("wish", cmd_wish_start))


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if context.user_data.get("awaiting_wish"):
        for code, room in data["rooms"].items():
            if uid in room["participants"] and not room["started"]:
                room["participants"][uid]["wish"] = update.message.text
                save_data(data)
                context.user_data["awaiting_wish"] = False
                await update.message.reply_text("✅ Пожелание сохранено!")
                add_reindeer_exp(uid, 5)
                return
        await update.message.reply_text("Вы не в комнате или игра уже началась.")
        context.user_data["awaiting_wish"] = False
        return
    await update.message.reply_text("Не понял. Попробуйте /start")


app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))


# ---------------- CALLBACK HANDLER ----------------
async def callback_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data_cb = q.data
    uid = str(q.from_user.id)

    # CREATE ROOM
    if data_cb == "create_room":
        code = create_room_for_user(q.from_user)
        await q.edit_message_text(f"🎉 Комната создана: {code}\nОтправь код друзьям.")
        return

    # JOIN ROOM
    if data_cb == "join_room":
        await q.edit_message_text("Отправьте /join_room RXXXXX или используйте /join_room <код>")
        return

    # PROFILE
    if data_cb == "my_reindeer":
        class TmpUpdate:
            def __init__(self, from_user, message):
                self.effective_user = from_user
                self.message = message
                self.callback_query = q
        tmp = TmpUpdate(q.from_user, q.message)
        await cmd_profile(tmp, context)
        return

    # MINI-GAMES MENU
    if data_cb == "mini_games":
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🎯 Угадай число", callback_data="game_number")],
                [InlineKeyboardButton("🧊 Монетка", callback_data="game_coin")],
                [InlineKeyboardButton("🧭 Квест", callback_data="quest_menu")],
                [InlineKeyboardButton("❄️ Снегопад (аним)", callback_data="animated_snow")],
                [InlineKeyboardButton("🎁 Идея подарка", callback_data="gift_idea")],
            ]
        )
        await q.edit_message_text("Выберите мини-игру:", reply_markup=kb)
        return

    # NUMBER GAME
    if data_cb == "game_number":
        n = random.randint(1, 5)
        context.user_data["secret_number"] = n
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1, 6)]])
        await q.edit_message_text("Я загадал число от 1 до 5 — угадай!", reply_markup=kb)
        return

    if data_cb.startswith("guess_"):
        guess = int(data_cb.split("_")[1])
        real = context.user_data.get("secret_number")
        if guess == real:
            add_reindeer_exp(uid, 10)
            u = data["users"].setdefault(uid, {})
            u["games_won"] = u.get("games_won", 0) + 1
            save_data(data)
            await q.edit_message_text("🎉 Верно! Ты получил 10 XP для оленёнка")
        else:
            await q.edit_message_text(f"❌ Неправильно — было {real}")
        return

    # COIN GAME
    if data_cb == "game_coin":
        side = random.choice(["Орёл 🦅", "Решка ❄️"])
        u = data["users"].setdefault(uid, {})
        if side.startswith("Орёл"):
            u["coin_streak"] = u.get("coin_streak", 0) + 1
            if u["coin_streak"] >= 5 and "lucky_coin" not in u.get("achievements", []):
                u.setdefault("achievements", []).append("lucky_coin")
        else:
            u["coin_streak"] = 0
        save_data(data)
        await q.edit_message_text(f"🧊 Выпало: {side}")
        return

    # QUEST MENU
    if data_cb == "quest_menu":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎄 Начать квест", callback_data="quest_start")]])
        await q.edit_message_text("✨ Новогодний квест — пройди три этапа!", reply_markup=kb)
        return

    if data_cb == "quest_start":
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✨ Сияющая тропа", callback_data="quest_light")],
                [InlineKeyboardButton("🌑 Тёмная тропа", callback_data="quest_dark")],
            ]
        )
        await q.edit_message_text("Глава 1: Перед тобой две тропы", reply_markup=kb)
        return

    if data_cb in ("quest_light", "quest_dark"):
        u = data["users"].setdefault(uid, {})
        if data_cb == "quest_light":
            if "snow_hero" not in u.get("achievements", []):
                u.setdefault("achievements", []).append("snow_hero")
            await q.edit_message_text("✨ Ты выбрал свет — получил Медаль Снежного Героя!")
        else:
            if "grinch_slayer" not in u.get("achievements", []):
                u.setdefault("achievements", []).append("grinch_slayer")
            await q.edit_message_text("🌑 Тёмная тропа — ты победил Гринча!")
        u["quests_finished"] = u.get("quests_finished", 0) + 1
        add_reindeer_exp(uid, 15)
        save_data(data)
        return

    # ANIMATED SNOW
    if data_cb == "animated_snow":
        frames = ["❄️", "✨", "❅", "☃️"]
        for i in range(8):
            fl = random.choice(frames)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{fl} Снежинка {i+1}", callback_data="noop")]])
            try:
                await q.edit_message_reply_markup(reply_markup=kb)
            except Exception:
                pass
            await asyncio.sleep(0.25)
        await q.edit_message_text("❄️ Снегопад окончен!")
        return

    # GIFT IDEAS
    if data_cb == "gift_idea":
        ideas = [
            "Беспроводные наушники — для музыки под ёлкой",
            "Тёплый плед с оленями",
            "Настольная игра для весёлой компании",
            "Подарочная коробка шоколада и печенья",
            "Абонемент в курс по интересам",
        ]
        await q.edit_message_text(f"🎁 Идея подарка: {random.choice(ideas)}")
        return

    # NOOP
    await q.answer()


app.add_handler(CallbackQueryHandler(callback_inline))


# ---------------- PROFILE ----------------
async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    ensure_user_record(uid)
    u = data["users"].get(uid, {})
    lvl = u.get("reindeer_level", 0)
    exp = u.get("reindeer_exp", 0)
    ach = u.get("achievements", [])
    achievements_text = "; ".join([ACHIEVEMENTS.get(a, a) for a in ach]) if ach else "Нет"
    msg = (
        f"🎅 *Профиль игрока* @{update.effective_user.username}\n\n"
        f"🦌 *Твой оленёнок:* {REINDEER_STAGES[min(lvl, len(REINDEER_STAGES) - 1)]}\n\n"
        f"🎖 *Достижения:* {achievements_text}\n\n"
        f"🎮 Статистика:\n• Побед в мини-играх: {u.get('games_won',0)}\n"
        f"• Пройдено квестов: {u.get('quests_finished',0)}\n"
        f"• Опыт оленёнка: {exp} XP"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


app.add_handler(CommandHandler("profile", cmd_profile))


# -------------- START --------------
if __name__ == "__main__":
    keep_alive()
    print("✅ Бот запускается — polling...")
    app.run_polling()

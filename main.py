# SUPER-DELUXE SECRET SANTA BOT — ПОЛНАЯ ВЕРСИЯ ДЛЯ REPLIT 2025
# Всё твоё волшебство + фиксы под Replit = 24/7 без ошибок

import json, random, string, asyncio, os, logging
import nest_asyncio
nest_asyncio.apply()
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from flask import Flask
from threading import Thread

# ====================== FLASK KEEP-ALIVE ======================
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Secret Santa жив!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

Thread(target=run_flask, daemon=True).start()

# ====================== КОНФИГ ======================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("Установите TELEGRAM_BOT_TOKEN в Secrets!")
    exit(1)

ADMIN_USERNAME = "BeellyKid"  # ←←← СМЕНИ НА СВОЙ НИК!!!
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

# ====================== УТИЛИТЫ ======================
def is_admin(update: Update):
    return update.effective_user.username == ADMIN_USERNAME

def gen_room_code():
    return "R" + "".join(random.choices(string.ascii_uppercase, k=5))

def menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("Ввести пожелание", callback_data="wish")],
        [InlineKeyboardButton("Тост дня", callback_data="toast")],
        [InlineKeyboardButton("Мини-игры", callback_data="mini_game_menu")],
        [InlineKeyboardButton("Новогодний Квест", callback_data="quest_start_menu")],
        [InlineKeyboardButton("Идея подарка", callback_data="gift_idea")],
        [InlineKeyboardButton("Снегопад", callback_data="animated_snowfall")]
    ]
    if admin:
        base.extend([
            [InlineKeyboardButton("Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("Админ: Пожелания", callback_data="admin_wishes")],
            [InlineKeyboardButton("Админ: Распределение", callback_data="admin_map")],
        ])
    return InlineKeyboardMarkup(base)

def toast_of_day():
    return random.choice([
        "Пусть в новом году твой холодильник всегда будет полон, а будильник — сломан!",
        "Желаю зарплаты как у Илон Маска, а забот — как у кота!",
        "Пусть удача прилипнет, как блёстки после корпоратива!",
        "Пусть счастье валит в дом, как снег в Сибири — неожиданно и много!"
    ])

# ====================== КОМАНДЫ ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    text = f"*Добро пожаловать, {user.first_name}!*\n\nЭтот бот — портал в волшебный мир Тайного Санты!\nСоздавай комнаты, приглашай друзей, пиши пожелания и дари магию!"
    kb = menu_keyboard(admin)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text(f"Только @{ADMIN_USERNAME} может создавать комнаты.")
        return
    data = load_data()
    code = gen_room_code()
    data["rooms"][code] = {
        "creator": update.effective_user.id,
        "members": {}, "game_started": False, "assign": {},
        "deadline": (datetime.utcnow() + timedelta(days=2)).isoformat()
    }
    save_data(data)
    await update.message.reply_text(f"*Комната создана!*\nКод: `{code}`\nПриглашай друзей!", parse_mode="Markdown")

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = " ".join(context.args).strip().upper()
    if not code:
        await update.message.reply_text("Напиши: /join_room RXXXXX")
        return
    data = load_data()
    if code not in data["rooms"]:
        await update.message.reply_text("Такой комнаты нет.")
        return
    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("Игра уже началась — вход закрыт!")
        return
    u = update.effective_user
    uid = str(u.id)
    if uid in room["members"]:
        await update.message.reply_text(f"Ты уже в комнате `{code}`!")
        return
    room["members"][uid] = {"name": u.full_name, "username": u.username, "wish": ""}
    save_data(data)
    await update.message.reply_text(f"Ты в комнате `{code}`!\nТеперь введи пожелание через кнопку", parse_mode="Markdown")

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("Только админ может запускать.")
        return
    code = " ".join(context.args).strip().upper()
    if not code:
        await update.message.reply_text("Формат: /start_game RXXXXX")
        return
    data = load_data()
    if code not in data["rooms"]:
        await update.message.reply_text("Комната не найдена.")
        return
    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("Игра уже запущена!")
        return
    if len(room["members"]) < 2:
        await update.message.reply_text("Нужно минимум 2 участника.")
        return

    for uid, m in room["members"].items():
        if not m["wish"]:
            await update.message.reply_text(f"{m['name']} не ввёл пожелание!")
            return

    members = list(room["members"].keys())
    random.shuffle(members)
    assign = {members[i]: members[(i + 1) % len(members)] for i in range(len(members))}
    room["assign"] = assign
    room["game_started"] = True
    save_data(data)

    for giver, receiver in assign.items():
        r = room["members"][receiver]
        try:
            await context.bot.send_message(int(giver),
                f"*Твой получатель в комнате {code}:*\n{r['name']} (@{r['username'] or 'без username'})\n\nПожелание:\n{r['wish']}",
                parse_mode="Markdown")
        except Exception as e:
            print(e)
    await update.message.reply_text(f"Игра в `{code}` запущена! Всем разослано!")

# ====================== ПОЖЕЛАНИЯ ======================
async def wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["wish_mode"] = True
    await update.callback_query.edit_message_text("Напиши своё новогоднее пожелание!\n\n*После запуска игры менять нельзя!*", parse_mode="Markdown")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("wish_mode"): return
    context.user_data["wish_mode"] = False
    data = load_data()
    user_id = str(update.effective_user.id)
    found = False
    for code, room in data["rooms"].items():
        if user_id in room["members"]:
            found = True
            if room["game_started"]:
                await update.message.reply_text("Игра уже запущена! Пожелание менять нельзя.")
            else:
                room["members"][user_id]["wish"] = update.message.text
                save_data(data)
                await update.message.reply_text("Пожелание сохранено! Магия началась")
            break
    if not found:
        await update.message.reply_text("Ты ещё не в комнате! Используй /join_room")

# ====================== АДМИНКА ======================
async def admin_rooms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    await update.callback_query.answer()
    data = load_data()
    txt = "*Комнаты:*\n"
    for c, r in data["rooms"].items():
        dl = datetime.fromisoformat(r["deadline"]).strftime("%d.%m %H:%M UTC")
        txt += f"`{c}` — {len(r['members'])} уч. | старт: {'ДА' if r['game_started'] else 'нет'} | дедлайн: {dl}\n"
    await update.callback_query.edit_message_text(txt or "Нет комнат", parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_menu")]]))

async def admin_wishes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    await update.callback_query.answer()
    data = load_data()
    txt = "*Все пожелания:*\n"
    for c, room in data["rooms"].items():
        txt += f"\nКомната `{c}`:\n"
        for uid, m in room["members"].items():
            txt += f"— {m['name']} (@{m['username'] or '—'}): {m['wish'] or '*пусто*'}\n"
    await update.callback_query.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_menu")]]))

async def admin_map_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    await update.callback_query.answer()
    data = load_data()
    txt = "*Распределение:*\n"
    for c, room in data["rooms"].items():
        txt += f"\nКомната `{c}`:\n"
        if not room["game_started"]:
            txt += "Игра не запущена\n"
            continue
        for g, r in room["assign"].items():
            txt += f"{room['members'][g]['name']} → {room['members'][r]['name']}\n"
    await update.callback_query.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_menu")]]))

# ====================== КВЕСТ ======================
async def quest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать квест", callback_data="quest_start")],
        [InlineKeyboardButton("Назад", callback_data="back_menu")]
    ])
    await update.callback_query.edit_message_text("*Новогодний квест!*\nПройди 3 уровня → стань Главным Снеговиком!", parse_mode="Markdown", reply_markup=kb)

async def quest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "quest_start":
        context.user_data["quest_level"] = 1
        await q.edit_message_text("Уровень 1: Найди подарок под ёлкой!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Открыть подарок", callback_data="quest_lvl1")]]))
    elif q.data == "quest_lvl1":
        context.user_data["quest_level"] = 2
        await q.edit_message_text("Подарок под снегом...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Сдуть снег", callback_data="quest_lvl2")]]))
    elif q.data == "quest_lvl2":
        context.user_data["quest_level"] = 3
        await q.edit_message_text("Снег сдут! Зови Санту!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Позвать Санту", callback_data="quest_lvl3")]]))
    elif q.data == "quest_lvl3":
        await q.edit_message_text("*Поздравляю!* Ты — Главный Снеговик 2026 года!",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Меню", callback_data="back_menu")]]))

# ====================== МИНИ-ИГРЫ ======================
async def mini_game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Угадай число", callback_data="game_number")],
        [InlineKeyboardButton("Монетка судьбы", callback_data="game_coin")],
        [InlineKeyboardButton("Назад", callback_data="back_menu")],
    ])
    await update.callback_query.edit_message_text("*Мини-игры!* Выбирай:", parse_mode="Markdown", reply_markup=kb)

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("guess_"):
        guess = int(q.data.split("_")[1])
        real = context.user_data.get("guess_num")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="mini_game_menu")]])
        await q.edit_message_text("Верно! Ты магистр предсказаний!" if guess == real else f"Не угадал! Было {real}.", reply_markup=kb)
    elif q.data == "game_number":
        num = random.randint(1, 5)
        context.user_data["guess_num"] = num
        await q.edit_message_text("Я загадал число от 1 до 5. Угадай!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1,6)]]))
    elif q.data == "game_coin":
        side = random.choice(["Орёл", "Решка"])
        await q.edit_message_text(f"Монетка упала: *{side}*!", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Снова", callback_data="game_coin")],
                [InlineKeyboardButton("Назад", callback_data="mini_game_menu")]
            ]))

# ====================== ПРОЧИЕ КНОПКИ ======================
async def gift_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ideas = [
        "Беспроводные наушники — чтобы слышать только хорошее!",
        "Тёплые носки с оленями — must have сезона!",
        "Огромная коробка шоколада для счастья на неделю.",
        "Аромасвеча 'Снежный вечер' — уют гарантирован!",
        "Книга с новогодней атмосферой — лучший зимний друг.",
        "Настольная игра — чтобы было чем заняться после оливье!"
    ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"*Идея подарка:*\n{random.choice(ideas)}", parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Ещё идею!", callback_data="gift_idea")],
            [InlineKeyboardButton("Назад", callback_data="back_menu")]
        ]))

async def toast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"*Тост дня:*\n{toast_of_day()}", parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Ещё тост!", callback_data="toast")],
            [InlineKeyboardButton("Назад", callback_data="back_menu")]
        ]))

async def animated_snowfall_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    frames = ["", "", "", ""]
    for i in range(10):
        flake = random.choice(frames)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{flake} Снежинка летит {flake}", callback_data="noop")]])
        try:
            await update.callback_query.edit_message_reply_markup(reply_markup=kb)
            await asyncio.sleep(0.35)
        except:
            break
    await start(update, context)

# ====================== ГЛАВНЫЙ INLINE ХЕНДЛЕР ======================
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "back_menu":
        await start(update, context)
    elif data == "wish":
        await wish_start(update, context)
    elif data == "toast":
        await toast_handler(update, context)
    elif data == "gift_idea":
        await gift_idea(update, context)
    elif data == "mini_game_menu":
        await mini_game_menu(update, context)
    elif data in ["game_number", "game_coin"] or data.startswith("guess_"):
        await game_handler(update, context)
    elif data == "quest_start_menu":
        await quest_menu(update, context)
    elif data in ["quest_start", "quest_lvl1", "quest_lvl2", "quest_lvl3"]:
        await quest_handler(update, context)
    elif data == "animated_snowfall":
        await animated_snowfall_buttons(update, context)
    elif data == "noop":
        pass
    elif data == "admin_rooms":
        await admin_rooms_handler(update, context)
    elif data == "admin_wishes":
        await admin_wishes_handler(update, context)
    elif data == "admin_map":
        await admin_map_handler(update, context)

# ====================== НАПОМИНАНИЯ ======================
async def reminder_loop(app: Application):
    while True:
        await asyncio.sleep(3600)
        data = load_data()
        now = datetime.utcnow()
        for code, room in data["rooms"].items():
            if room.get("game_started"): continue
            try:
                deadline = datetime.fromisoformat(room["deadline"])
                if timedelta(0) < (deadline - now) <= timedelta(hours=1):
                    for uid in room["members"]:
                        try:
                            await app.bot.send_message(int(uid),
                                f"*Напоминание!*\nДо дедлайна комнаты `{code}` остался ~1 час!\nВведи пожелание!",
                                parse_mode="Markdown")
                        except: pass
            except: pass


# ====================== ЗАПУСК ======================
def main():
    # Flask keep-alive (уже запущен выше)
    print("Бот запускается...")

    app = Application.builder().token(TOKEN).build()

    # Все хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_room", create_room))
    app.add_handler(CommandHandler("join_room", join_room))
    app.add_handler(CommandHandler("start_game", start_game))
    app.add_handler(CallbackQueryHandler(inline_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Запускаем напоминания
    app.create_task(reminder_loop(app))

    print("Бот полностью запущен! Снегопад, квест, игры, тосты — всё работает 24/7!")

    # ← ЭТО САМОЕ ГЛАВНОЕ: запускаем без asyncio.run()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()    # ← Обязательно!
    logging.basicConfig(level=logging.INFO)
    main()                  # ← Просто вызываем функцию
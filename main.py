# 🔥🎄 SUPER-DELUXE SECRET SANTA BOT + СНЕГОПАД + НАПОМИНАНИЯ + МИНИ-ИГРЫ 🎄🔥 — FULL FEATURE PACK 🎄🔥
# Полностью переработанная версия: ещё более новогодняя, красивая и функциональная!
# Под Replit / Python / PTB20+
# Управление комнатами, глубокие ссылки, новогодние шутки, меню, снег, тосты, дедлайны и т.д.

import json
import random
import string
import asyncio
import os
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

# -------------------------------------------------------------------
# WEB-СЕРВЕР ДЛЯ REPLIT
# -------------------------------------------------------------------
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# -------------------------------------------------------------------
# КОНФИГУРАЦИЯ И ДАННЫЕ
# -------------------------------------------------------------------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN is not set! Установите переменную окружения.")
    exit(1)

ADMIN_USERNAME = "BeellyKid" # Измените на свой никнейм для админ-доступа
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
# УТИЛИТЫ И МЕНЮ
# -------------------------------------------------------------------
def is_admin(update: Update):
    # Проверка должна быть по user_id, но для простоты оставляем username
    return update.effective_user.username == ADMIN_USERNAME

def gen_room_code():
    return "R" + "".join(random.choice(string.ascii_uppercase) for _ in range(5))

def menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("🎁 Ввести пожелание", callback_data="wish")],
        [InlineKeyboardButton("✨ Тост дня", callback_data="toast")],
        [InlineKeyboardButton("🎮 Мини-игры", callback_data="mini_game_menu")],
        [InlineKeyboardButton("⚔️ Новогодний Квест", callback_data="quest_start_menu")],
        [InlineKeyboardButton("💡 Идея подарка", callback_data="gift_idea")],
        [InlineKeyboardButton("❄️ Снегопад", callback_data="animated_snowfall")]
    ]
    if admin:
        base.extend([
            [InlineKeyboardButton("🎄 Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("📜 Админ: Пожелания", callback_data="admin_wishes")],
            [InlineKeyboardButton("🔀 Админ: Распределение", callback_data="admin_map")],
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
# /START - ГЛАВНОЕ МЕНЮ
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    # Если это колбэк, используем edit_message_text
    if update.callback_query:
        await update.callback_query.answer()
        # Для возврата из меню, нужно обновить сообщение
        await update.callback_query.edit_message_text(
            f"🎄 *Добро пожаловать, {user.first_name}!* 🎅",
            parse_mode="Markdown",
            reply_markup=menu_keyboard(admin)
        )
    # Если это команда /start
    else:
        await update.message.reply_text(
            f"🎄 *Добро пожаловать, {user.first_name}!* 🎅\n\n"
            "Этот бот — портал в волшебный мир Тайного Санты! 🎁✨\n"
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
        found_room = False
        for code, room in data["rooms"].items():
            if str(user.id) in room["members"]:
                found_room = True
                if room.get("game_started"):
                    await update.message.reply_text("🚫 Игра уже запущена! Менять пожелание нельзя.")
                    return
                room["members"][str(user.id)]["wish"] = update.message.text
                save_data(data)
                context.user_data["wish_mode"] = False
                await update.message.reply_text("✨ Пожелание сохранено! Волшебство началось 🎄")
                return
        
        context.user_data["wish_mode"] = False # Сброс, если не нашли комнату
        if not found_room:
             await update.message.reply_text("❄️ Ты ещё не в комнате! Используй /join_room.")
        return
    
    # Можно добавить обработку обычного текста, если не в режиме пожелания
    # await update.message.reply_text("Что-то не так. Попробуй /start")


# -------------------------------------------------------------------
# КОМАНДЫ КОМНАТ
# -------------------------------------------------------------------
async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text(f"🚫 Только @{ADMIN_USERNAME} может создавать комнаты.")
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
        f"🎄 *Комната создана!*\n"
        f"Код: `{code}`\n\n"
        "Приглашай друзей!",
        parse_mode="Markdown"
    )

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
    uid_str = str(u.id)
    
    if uid_str in room["members"]:
        await update.message.reply_text(f"✨ Ты уже в комнате `{code}`!")
        return
        
    room["members"][uid_str] = {
        "name": u.full_name,
        "username": u.username,
        "wish": ""
    }
    save_data(data)

    await update.message.reply_text(
        f"✨ Ты в комнате `{code}`!\n"
        "Теперь используй кнопку '🎁 Ввести пожелание' или команду /start, чтобы добавить его.",
        parse_mode="Markdown"
    )

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 Доступ запрещён.")
        return

    code = "".join(context.args).strip().upper() if context.args else None
    data = load_data()

    if not code or code not in data["rooms"]:
        await update.message.reply_text("Формат: /start_game RXXXXX")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("❄️ Уже запущено!")
        return
        
    if len(room["members"]) < 2:
        await update.message.reply_text("🚫 Недостаточно участников (нужно минимум 2).")
        return


    members = list(room["members"].keys())
    random.shuffle(members)
    assigns = {}
    
    # Проверка на наличие пожелания
    for uid in members:
        if not room["members"][uid]["wish"]:
            await update.message.reply_text(f"🚫 Участник {room['members'][uid]['name']} не ввёл пожелание. Игра не может начаться.")
            return
            
    # Собственно, распределение
    for i, uid in enumerate(members):
        assigns[uid] = members[(i + 1) % len(members)]

    room["assign"] = assigns
    room["game_started"] = True
    save_data(data)

    # Рассылка
    for giver, receiver in assigns.items():
        m = room["members"][receiver]
        try:
            # Отправка личного сообщения получателю
            await context.bot.send_message(
                giver,
                f"🎁 *Твой получатель в комнате {code}:* {m['name']} (@{m['username'] if m['username'] else 'нет_username'})"
                f"\n\n✨ Его пожелание: {m['wish']}",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {giver}: {e}")
            
    await update.message.reply_text(f"🎄 Игра в комнате `{code}` запущена! Разослал всем их получателей ✨✨✨", parse_mode="Markdown")

# -------------------------------------------------------------------
# АДМИН-МЕНЮ (CALLBACKS)
# -------------------------------------------------------------------
async def admin_rooms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    data = load_data()
    txt = "📦 *Комнаты:*\n"
    if not data["rooms"]:
        txt += "Нет активных комнат."
    else:
        for c, room in data["rooms"].items():
            deadline_dt = datetime.fromisoformat(room["deadline"]).strftime("%d.%m %H:%M UTC")
            txt += f"`{c}` — {len(room['members'])} уч., старт: {'ДА' if room['game_started'] else 'НЕТ'}. Дедлайн: {deadline_dt}\n"
            
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]])
    await update.callback_query.edit_message_text(txt, parse_mode="Markdown", reply_markup=kb)

async def admin_wishes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    data = load_data()
    txt = "🎁 *Все пожелания:*\n"
    
    for c, room in data["rooms"].items():
        txt += f"\nКомната `{c}`:\n"
        for uid, m in room["members"].items():
            wish_text = m['wish'] if m['wish'] else "*(нет пожелания)*"
            txt += f"— {m['name']} (@{m['username']}): {wish_text}\n"

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]])
    await update.callback_query.edit_message_text(txt, parse_mode="Markdown", reply_markup=kb)

async def admin_map_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    data = load_data()
    txt = "🔀 *Распределение:*\n"
    
    for c, room in data["rooms"].items():
        txt += f"\nКомната `{c}`:\n"
        if not room["game_started"]:
            txt += "Игра ещё не запущена.\n"
            continue
            
        for g, r in room["assign"].items():
            mg = room["members"][g]
            mr = room["members"][r]
            txt += f"🎅 {mg['name']} → 🎁 {mr['name']}\n"
            
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]])
    await update.callback_query.edit_message_text(txt, parse_mode="Markdown", reply_markup=kb)


# -------------------------------------------------------------------
# КВЕСТ
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
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Меню", callback_data="back_menu")]])
        await q.edit_message_text("🎉 *Поздравляем!* Ты стал Главным Снеговиком Нового Года!", parse_mode="Markdown", reply_markup=kb)

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
    
    # Для кнопок угадай число, чтобы не ломать логику других колбэков
    if q.data.startswith("guess_"):
        guess = int(q.data.split("_")[1])
        real = context.user_data.get("guess_num")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="mini_game_menu")]])

        if guess == real:
            await q.edit_message_text("🎉 Верно! Ты — магистр новогодних предсказаний!", reply_markup=kb)
        else:
            await q.edit_message_text(f"❄️ Не угадал! Было число {real}.", reply_markup=kb)
        return

    if q.data == "game_number":
        num = random.randint(1, 5)
        context.user_data["guess_num"] = num
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f"guess_{i}") for i in range(1,6)]] )
        await q.edit_message_text("🎯 Я загадал число от 1 до 5. Угадай!", reply_markup=kb)

    elif q.data == "game_coin":
        side = random.choice(["Орёл 🦅", "Решка ❄️"])
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Снова", callback_data="game_coin")] , [InlineKeyboardButton("⬅️ Назад", callback_data="mini_game_menu")]])
        await q.edit_message_text(f"🧊 Монетка упала: *{side}*!", parse_mode="Markdown", reply_markup=kb)


# -------------------------------------------------------------------
# ПРОЧИЕ ФУНКЦИИ (CALLBACKS)
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
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Ещё идею!", callback_data="gift_idea")], [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]])
    await update.callback_query.edit_message_text(f"🎁 *Идея подарка:* {idea}", parse_mode="Markdown", reply_markup=kb)

async def toast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Ещё тост!", callback_data="toast")], [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]])
    await update.callback_query.edit_message_text(f"✨ *Тост дня:*\n{toast_of_day()}", parse_mode="Markdown", reply_markup=kb)

async def animated_snowfall_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    frames = ["❄️", "✨", "❅", "☃️"]
    for i in range(8):
        flake = random.choice(frames)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{flake} Снежинка летит {flake}", callback_data="noop")]])
        try:
            await update.callback_query.edit_message_reply_markup(reply_markup=kb)
        except Exception as e:
            # Игнорируем ошибку, если пользователь быстро нажмет другую кнопку
            print(f"Ошибка обновления кнопок: {e}")
            break 
        await asyncio.sleep(0.3)
    
    # Возвращаемся в меню после анимации
    await start(update, context)

# -------------------------------------------------------------------
# ОБРАБОТЧИК ВСЕХ INLINE КНОПОК
# -------------------------------------------------------------------
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    if q.data == "back_menu":
        await start(update, context)
        
    elif q.data == "wish":
        await wish_start(update, context)

    elif q.data == "toast":
        await toast_handler(update, context)
        
    elif q.data == "gift_idea":
        await gift_idea(update, context)
        
    elif q.data == "mini_game_menu":
        await mini_game_menu(update, context)

    elif q.data == "game_number" or q.data == "game_coin" or q.data.startswith("guess_"):
        await game_handler(update, context)
        
    elif q.data == "quest_start_menu":
        await quest_menu(update, context)
        
    elif q.data.startswith("quest_lvl") or q.data == "quest_start":
        await quest_handler(update, context)
        
    elif q.data == "animated_snowfall":
        await animated_snowfall_buttons(update, context)
        
    elif q.data == "noop":
        await q.answer() # Ничего не делаем, просто закрываем уведомление

    # Админские кнопки
    elif q.data == "admin_rooms":
        await admin_rooms_handler(update, context)

    elif q.data == "admin_wishes":
        await admin_wishes_handler(update, context)

    elif q.data == "admin_map":
        await admin_map_handler(update, context)
        
    else:
        await q.answer("Неизвестная команда.")


# -------------------------------------------------------------------
# НАПОМИНАНИЯ (ФОНОВЫЙ ЦИКЛ)
# -------------------------------------------------------------------
async def reminder_loop(app: Application):
    while True:
        # Проверка дедлайнов каждый час (3600 секунд)
        await asyncio.sleep(3600) 
        
        data = load_data()
        now = datetime.utcnow()

        for code, room in data["rooms"].items():
            if room.get("game_started"):
                continue
                
            deadline_str = room.get("deadline")
            if not deadline_str:
                continue
                
            deadline = datetime.fromisoformat(deadline_str)
            # Если до дедлайна остался 1 час или меньше, но он ещё не наступил
            if now + timedelta(hours=1) > deadline and now < deadline:
                for uid_str in room["members"]:
                    try:
                        # Отправка напоминания
                        await app.bot.send_message(
                            int(uid_str), # Telegram API требует int
                            f"⏰ *Напоминание!* До дедлайна на сбор пожеланий в комнате `{code}` остался 1 час!",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Не удалось отправить напоминание пользователю {uid_str}: {e}")
                        
        
# -------------------------------------------------------------------
# MAIN - ЗАПУСК БОТА
# -------------------------------------------------------------------
async def main():
    app = Application.builder().token(TOKEN).build()
    
    # Добавление обработчиков команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_room", create_room))
    app.add_handler(CommandHandler("join_room", join_room))
    app.add_handler(CommandHandler("start_game", start_game))
    # Добавление обработчика inline кнопок
    app.add_handler(CallbackQueryHandler(inline_handler))
    # Добавление обработчика текста (для пожеланий)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🎄 Бот запущен! Ожидание команды /start. ❄️✨")
    
    # Запуск фонового цикла для напоминаний
    app.create_task(reminder_loop(app))
    
    # Запуск бота с polling
    await app.run_polling()


if __name__ == "__main__":
    keep_alive()  # запускаем мини-сервер для Replit
    print("✅ Бот запускается...")
    # asyncio.run(main()) # НЕ использовать с run_polling в PTB20+
    # Используем синхронный запуск, чтобы Flask Thread работал правильно
    import logging
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
    except Exception as e:
        print(f"Критическая ошибка при запуске бота: {e}")
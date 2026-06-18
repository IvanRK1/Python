import os
import sqlite3
import telebot
from telebot import types

# --- НАЛАШТУВАННЯ БОТА ---
TOKEN = "8720662793:AAG-qhJueQxueSTGHLdcXrAWe3Osjb_QH-0"
ADMIN_ID = 6834600971

bot = telebot.TeleBot(TOKEN)
DB_FILE = "poetry.db"

USER_CONTEXT = {}

# Глобальний фільтр кнопок меню
MENU_BUTTONS = [
    "📝 Новий вірш", "📚 Мої вірші", "📁 Мої збірки", "🌍 Спільнота",
    "📚 Збірки спільноти", "📝 Окремі вірші", "➕ Створити збірку",
    "⚙️ Керування збірками"
]


# --- ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        chat_id INTEGER PRIMARY KEY,
                        username TEXT,
                        password TEXT,
                        state TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS poems (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        title TEXT,
                        content TEXT,
                        collection_name TEXT DEFAULT 'Немає',
                        sort_order INTEGER DEFAULT 0,
                        is_public INTEGER DEFAULT 0,
                        views INTEGER DEFAULT 0,
                        likes INTEGER DEFAULT 0)''')

    cols = ["is_public", "views", "likes", "sort_order"]
    for col in cols:
        try:
            cursor.execute(f"ALTER TABLE poems ADD COLUMN {col} INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


init_db()


# --- ПОМІЧНИКИ БАЗИ ДАНИХ ---
def get_user_state(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT state FROM users WHERE chat_id = ?", (chat_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None


def set_user_state(chat_id, state):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET state = ? WHERE chat_id = ?", (state, chat_id))
    conn.commit()
    conn.close()


# --- КНОПКИ МЕНЮ (МАРКАПИ) ---
def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Новий вірш", "📚 Мої вірші")
    markup.row("📁 Мої збірки", "🌍 Спільнота")
    return markup


def my_collections_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Створити збірку", "⚙️ Керування збірками")
    markup.row("🔙 Назад у меню")
    return markup


def community_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📚 Збірки спільноти", "📝 Окремі вірші")
    markup.row("🔙 Назад у меню")
    return markup


def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔙 Назад у меню")
    return markup


def my_poem_preview_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📖 Просто читати", "⚙️ Керування віршем")
    markup.row("🔙 Назад у меню")
    return markup


def my_poem_actions_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("✏️ Редагувати текст", "📝 Перейменувати")
    markup.row("📁 Змінити збірку", "🔢 Змінити порядок")
    markup.row("🌍 Опублікувати/Сховати", "❌ Видалити вірш")
    markup.row("🔙 Назад у меню")
    return markup


def my_collection_actions_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📖 Читати збірку", "➕ Додати вірші")
    markup.row("🌍 Опублікувати/Сховати", "✏️ Перейменувати")
    markup.row("🔓 Розформувати", "❌ Видалити ПОВНІСТЮ")
    markup.row("🔙 Назад у меню")
    return markup


def community_poem_actions_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📖 Читати", "👍 Лайкнути", "📥 Завантажити собі")
    markup.row("🔙 Назад у меню")
    return markup


def community_collection_actions_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👀 Переглянути", "👍 Лайкнути всю", "📥 Завантажити ВСЮ")
    markup.row("🔙 Назад у меню")
    return markup


def admin_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📢 Зробити розсилку", "💣 Очистити базу даних")
    markup.row("🔙 Назад у меню")
    return markup


# --- СТАРТ ТА АВТОРИЗАЦІЯ ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = message.chat.id
    user_handle = message.from_user.username if message.from_user.username else message.from_user.first_name

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE chat_id = ?", (chat_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET state = 'LOGIN_PASSWORD' WHERE chat_id = ?", (chat_id,))
        bot.send_message(chat_id, f"Привіт, {message.from_user.first_name}! Введи свій пароль для входу:",
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        cursor.execute("INSERT INTO users (chat_id, username, password, state) VALUES (?, ?, '', 'REG_PASSWORD')",
                       (chat_id, user_handle))
        bot.send_message(chat_id, "Вітаю! Придумай та введи пароль для свого акаунта:",
                         reply_markup=types.ReplyKeyboardRemove())

    conn.commit()
    conn.close()


# --- ГОЛОВНИЙ ОБРОБНИК ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = get_user_state(chat_id)

    # --- СЕКРЕТНІ КОМАНДИ ---
    if text == "TYU156" and chat_id == ADMIN_ID:
        set_user_state(chat_id, "ADMIN_MENU")
        bot.send_message(chat_id, "👑 *Адмін-панель активована!*\nОбери дію на клавіатурі нижче:", parse_mode="Markdown",
                         reply_markup=admin_menu_markup())
        return
    elif text == "ToY155":
        set_user_state(chat_id, "RESET_PASSWORD")
        bot.send_message(chat_id, "🔄 Режим скидання пароля! Введи свій новий пароль:")
        return

    # Перевірка кнопки Назад
    if text == "🔙 Назад у меню":
        set_user_state(chat_id, "MAIN_MENU")
        bot.send_message(chat_id, "Головне меню.", reply_markup=main_menu_markup())
        return

        # ЛОГІКА ДОДАВАННЯ ВІРШІВ СПИСКОМ (БЕЗ ЛІМІТУ КНОПОК)
    if state == "COLLECTION_ACTIONS" and text == "➕ Додати вірші":
        col_name = USER_CONTEXT.get(chat_id, {}).get("my_col")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM poems WHERE chat_id = ? AND collection_name != ?", (chat_id, col_name))
        free_poems = cursor.fetchall()
        conn.close()

        if not free_poems:
            bot.send_message(chat_id, "Немає доступних віршів для додавання.", reply_markup=main_menu_markup())
        else:
            set_user_state(chat_id, "ADD_POEM_TO_COLLECTION")
            poem_list = "\n".join([f"🔹 `{p[0]}`" for p in free_poems])
            bot.send_message(chat_id,
                             f"📝 *Список доступних віршів:*\n\n{poem_list}\n\n👉 *Скопіюй назву вірша і надішли її сюди:*",
                             parse_mode="Markdown", reply_markup=back_markup())
        return

    if state == "ADD_POEM_TO_COLLECTION":
        col_name = USER_CONTEXT[chat_id]["my_col"]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM poems WHERE chat_id = ? AND title = ?", (chat_id, text))
        if cursor.fetchone():
            cursor.execute("UPDATE poems SET collection_name = ? WHERE chat_id = ? AND title = ?",
                           (col_name, chat_id, text))
            conn.commit()
            bot.send_message(chat_id, f"✅ Вірш '{text}' додано! Пиши назву наступного або натисни 'Назад'.")
        else:
            bot.send_message(chat_id, "⚠️ Вірш не знайдено. Введи назву точно зі списку.")
        conn.close()
        return

        # ЛОГІКА КОПІЮВАННЯ ПО ДОТИКУ (ЧИТАННЯ)
    if state == "MY_POEM_PREVIEW" and text == "📖 Просто читати":
        poem_title = USER_CONTEXT.get(chat_id, {}).get("poem_title")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM poems WHERE chat_id = ? AND title = ?", (chat_id, poem_title))
        content = cursor.fetchone()[0]
        conn.close()

        # Виводимо вірш чистим текстом - Telegram автоматично зробить його "копіювальним"
        bot.send_message(chat_id, content)
        bot.send_message(chat_id, "Текст виведено. Можеш скопіювати його натисканням.", reply_markup=main_menu_markup())
        set_user_state(chat_id, "MAIN_MENU")
        return

    # 🔥 ФІЛЬТР "ПЕРЕДУМАВ"
    if text in MENU_BUTTONS and state not in ["REG_PASSWORD", "LOGIN_PASSWORD", "MAIN_MENU", "COMMUNITY_MENU",
                                              "MY_COLLECTIONS_MENU", "ADMIN_MENU"]:
        state = "MAIN_MENU"
        set_user_state(chat_id, "MAIN_MENU")

    # --- СТАНІ АВТОРИЗАЦІЇ ---
    if state == "REG_PASSWORD":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ?, state = 'MAIN_MENU' WHERE chat_id = ?", (text, chat_id))
        conn.commit()
        conn.close()
        bot.send_message(chat_id, "Пароль збережено!", reply_markup=main_menu_markup())
        return

    elif state == "LOGIN_PASSWORD":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE chat_id = ?", (chat_id,))
        saved_pass = cursor.fetchone()[0]
        conn.close()
        if text == saved_pass:
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id, "Вхід успішний!", reply_markup=main_menu_markup())
        else:
            bot.send_message(chat_id, "Неправильний пароль. Спробуй ще раз:")
        return

    elif state == "RESET_PASSWORD":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ?, state = 'MAIN_MENU' WHERE chat_id = ?", (text, chat_id))
        conn.commit()
        conn.close()
        bot.send_message(chat_id, "Пароль оновлено!", reply_markup=main_menu_markup())
        return

    # --- АДМІНКА ---
    elif state == "ADMIN_MENU":
        if text == "📢 Зробити розсилку":
            set_user_state(chat_id, "ADMIN_BROADCAST")
            bot.send_message(chat_id, "Введи текст повідомлення, яке отримають усі користувачі:",
                             reply_markup=back_markup())
        elif text == "💣 Очистити базу даних":
            set_user_state(chat_id, "ADMIN_CONFIRM_DB_CLEAR")
            bot.send_message(chat_id,
                             "⚠️ *УВАГА!* Ця дія видалить УСІ вірші, збірки та користувачів (окрім тебе).\n\nНапиши слово `ТАК` для підтвердження або натисни Назад.",
                             parse_mode="Markdown", reply_markup=back_markup())
        return

    elif state == "ADMIN_BROADCAST":
        set_user_state(chat_id, "MAIN_MENU")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        all_users = cursor.fetchall()
        conn.close()
        count = sum(1 for u in all_users if bot.send_message(u[0], f"📢 Розсилка:\n\n{text}"))
        bot.send_message(chat_id, f"✅ Повідомлення надіслано {count} користувачам.", reply_markup=main_menu_markup())
        return

    elif state == "ADMIN_CONFIRM_DB_CLEAR":
        if text == "ТАК":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM poems")
            cursor.execute("DELETE FROM users WHERE chat_id != ?", (chat_id,))
            conn.commit()
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id,
                             "💥 *БАЗУ ДАНИХ ПОВНІСТЮ ОЧИЩЕНО!*\nУсі користувачі та вірші видалені. Твій акаунт збережено.",
                             parse_mode="Markdown", reply_markup=main_menu_markup())
        else:
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id, "Відміна. Повертаємось у меню.", reply_markup=main_menu_markup())
        return

    # --- СТВОРЕННЯ ВІРША ---
    elif state == "POEM_TITLE":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO poems (chat_id, title, content) VALUES (?, ?, '')", (chat_id, text))
        conn.commit()
        conn.close()
        set_user_state(chat_id, "POEM_CONTENT")
        bot.send_message(chat_id, "Назву прийнято. Тепер надішли текст вірша:", reply_markup=back_markup())
        return

    elif state == "POEM_CONTENT":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM poems WHERE chat_id = ? AND content = '' ORDER BY id DESC LIMIT 1", (chat_id,))
        poem = cursor.fetchone()
        if poem:
            cursor.execute("UPDATE poems SET content = ? WHERE id = ?", (text, poem[0]))
            conn.commit()
            bot.send_message(chat_id, "Вірш успішно збережено!", reply_markup=main_menu_markup())
        conn.close()
        set_user_state(chat_id, "MAIN_MENU")
        return

    # --- РОБОТА ЗІ ЗБІРКАМИ ---
    elif state == "MY_COLLECTIONS_MENU":
        if text == "➕ Створити збірку":
            set_user_state(chat_id, "CREATE_COLLECTION")
            bot.send_message(chat_id, "Введи назву для нової збірки:", reply_markup=back_markup())
            return
        elif text == "⚙️ Керування збірками":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT collection_name FROM poems WHERE chat_id = ? AND collection_name != 'Немає'",
                (chat_id,))
            cols = cursor.fetchall()
            conn.close()

            if not cols:
                bot.send_message(chat_id, "У тебе ще немає створених збірок.")
            else:
                msg = "📁 *Твої збірки (натисни для копіювання):*\n\n"
                for c in cols:
                    msg += f"🔹 `{c[0]}`\n"
                msg += "\n✍️ Надішли назву збірки, яку хочеш налаштувати:"
                set_user_state(chat_id, "SELECT_MY_COLLECTION")
                bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=back_markup())
            return

    elif state == "CREATE_COLLECTION":
        set_user_state(chat_id, "MAIN_MENU")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE poems SET collection_name = ? WHERE chat_id = ? AND collection_name = 'Немає'",
                       (text, chat_id))
        conn.commit()
        conn.close()
        bot.send_message(chat_id, f"Приватну збірку '{text}' успішно створено!", reply_markup=main_menu_markup())
        return

    elif state == "SELECT_MY_COLLECTION":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT is_public FROM poems WHERE chat_id = ? AND collection_name = ? LIMIT 1", (chat_id, text))
        res = cursor.fetchone()
        conn.close()

        status_word = "🔒 Конфіденційна"
        if res and res[0] == 1:
            status_word = "🌍 Публічна у Спільноті"

        USER_CONTEXT[chat_id] = {"my_col": text}
        set_user_state(chat_id, "COLLECTION_ACTIONS")
        msg = f"📁 *Меню збірки '{text}'*\n📊 Статус: *{status_word}*\n\nОбери дію на клавіатурі:"
        bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=my_collection_actions_markup())
        return

    elif state == "COLLECTION_ACTIONS":
        col_name = USER_CONTEXT.get(chat_id, {}).get("my_col")

        if text == "📖 Читати збірку":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT title, content FROM poems WHERE chat_id = ? AND collection_name = ? ORDER BY sort_order DESC, id ASC",
                (chat_id, col_name))
            res = cursor.fetchall()
            conn.close()
            if not res:
                bot.send_message(chat_id, "У цій збірці ще немає віршів.")
            else:
                bot.send_message(chat_id, f"📁 --- ЗБІРКА: {col_name} ---")
                for p in res:
                    bot.send_message(chat_id, f"📌 *{p[0]}*\n\n{p[1]}", parse_mode="Markdown")
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id, "Перегляд завершено.", reply_markup=main_menu_markup())

        elif text == "➕ Додати вірші":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM poems WHERE chat_id = ? AND collection_name != ?", (chat_id, col_name))
            free_poems = cursor.fetchall()
            conn.close()

            if not free_poems:
                bot.send_message(chat_id, "У тебе немає інших віршів для додавання.", reply_markup=main_menu_markup())
                set_user_state(chat_id, "MAIN_MENU")
            else:
                set_user_state(chat_id, "ADD_POEM_TO_COLLECTION")
                # Генеруємо клавіатуру з усіма віршами
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                row = []
                for p in free_poems:
                    row.append(p[0])
                    if len(row) == 2:
                        markup.row(*row)
                        row = []
                if row:
                    markup.row(*row)
                markup.row("🔙 Назад у меню")
                bot.send_message(chat_id, "Обери вірш, який хочеш додати до цієї збірки:", reply_markup=markup)

        elif text == "🌍 Опублікувати/Сховати":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT is_public FROM poems WHERE chat_id = ? AND collection_name = ? LIMIT 1",
                           (chat_id, col_name))
            res = cursor.fetchone()
            new_status = 0 if res and res[0] == 1 else 1
            cursor.execute("UPDATE poems SET is_public = ? WHERE chat_id = ? AND collection_name = ?",
                           (new_status, chat_id, col_name))
            conn.commit()
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
            word = "опубліковано у спільноту!" if new_status == 1 else "заховано в приватний архів."
            bot.send_message(chat_id, f"✅ Статус збірки змінено. Тепер її {word}", reply_markup=main_menu_markup())

        elif text == "✏️ Перейменувати":
            set_user_state(chat_id, "RENAME_COLLECTION")
            bot.send_message(chat_id, f"Введи нову назву для збірки '{col_name}':", reply_markup=back_markup())

        elif text == "🔓 Розформувати":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE poems SET collection_name = 'Немає' WHERE chat_id = ? AND collection_name = ?",
                           (chat_id, col_name))
            conn.commit()
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id, f"Збірку розформовано. Вірші збережені як окремі.",
                             reply_markup=main_menu_markup())

        elif text == "❌ Видалити ПОВНІСТЮ":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM poems WHERE chat_id = ? AND collection_name = ?", (chat_id, col_name))
            conn.commit()
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id, f"Збірку '{col_name}' ВИДАЛЕНО разом з усіма віршами!",
                             reply_markup=main_menu_markup())
        return

    elif state == "ADD_POEM_TO_COLLECTION":
        col_name = USER_CONTEXT[chat_id]["my_col"]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM poems WHERE chat_id = ? AND title = ?", (chat_id, text))
        if cursor.fetchone():
            cursor.execute("UPDATE poems SET collection_name = ? WHERE chat_id = ? AND title = ?",
                           (col_name, chat_id, text))
            conn.commit()
            bot.send_message(chat_id, f"✅ Вірш '{text}' успішно додано до збірки '{col_name}'!",
                             reply_markup=main_menu_markup())
        else:
            bot.send_message(chat_id, "Вірш не знайдено, або дію скасовано.", reply_markup=main_menu_markup())
        conn.close()
        set_user_state(chat_id, "MAIN_MENU")
        return

    elif state == "RENAME_COLLECTION":
        old_name = USER_CONTEXT[chat_id]["my_col"]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE poems SET collection_name = ? WHERE chat_id = ? AND collection_name = ?",
                       (text, chat_id, old_name))
        conn.commit()
        conn.close()
        set_user_state(chat_id, "MAIN_MENU")
        bot.send_message(chat_id, "Назву збірки успішно змінено!", reply_markup=main_menu_markup())
        return

    # --- ЛОГІКА: МОЇ ВІРШІ ---
    elif state == "MY_POEMS_LIST":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM poems WHERE chat_id = ? AND title = ?", (chat_id, text))
        poem = cursor.fetchone()
        conn.close()

        if poem:
            USER_CONTEXT[chat_id] = {"poem_title": text}
            set_user_state(chat_id, "MY_POEM_PREVIEW")
            bot.send_message(chat_id, f"📖 Обрано вірш: *{text}*\nОбери дію на клавіатурі нижче:", parse_mode="Markdown",
                             reply_markup=my_poem_preview_markup())
        else:
            bot.send_message(chat_id, "Вірш не знайдено. Скопіюй і надішли назву зі списку вище.")
        return

    elif state == "MY_POEM_PREVIEW":
        poem_title = USER_CONTEXT.get(chat_id, {}).get("poem_title")
        if text == "📖 Просто читати":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content, collection_name, sort_order, is_public, views, likes FROM poems WHERE chat_id = ? AND title = ?",
                (chat_id, poem_title))
            p = cursor.fetchone()
            conn.close()
            status = "🌍 Публічний" if p[3] == 1 else "🔒 Приватний"
            msg = f"📝 *{poem_title}*\n📁 Збірка: {p[1]} | Порядок: {p[2]}\n📊 Статус: {status} | 👀 Перегляди: {p[4]} | ❤️ Лайки: {p[5]}\n\n---\n\n{p[0]}"
            bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=main_menu_markup())
            set_user_state(chat_id, "MAIN_MENU")
        elif text == "⚙️ Керування віршем":
            set_user_state(chat_id, "MY_POEM_ACTIONS")
            bot.send_message(chat_id, f"⚙️ Керування віршем '{poem_title}':", reply_markup=my_poem_actions_markup())
        return

    elif state == "MY_POEM_ACTIONS":
        poem_title = USER_CONTEXT.get(chat_id, {}).get("poem_title")
        if text == "✏️ Редагувати текст":
            set_user_state(chat_id, "EDIT_POEM_TEXT")
            bot.send_message(chat_id, f"Введи новий текст для вірша '{poem_title}':", reply_markup=back_markup())
        elif text == "📝 Перейменувати":
            set_user_state(chat_id, "RENAME_POEM")
            bot.send_message(chat_id, f"Введи нову назву для вірша '{poem_title}':", reply_markup=back_markup())
        elif text == "📁 Змінити збірку":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT collection_name FROM poems WHERE chat_id = ? AND collection_name != 'Немає'",
                (chat_id,))
            cols = cursor.fetchall()
            conn.close()

            set_user_state(chat_id, "EDIT_POEM_COLLECTION")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("Немає")
            row = []
            for c in cols:
                row.append(c[0])
                if len(row) == 2:
                    markup.row(*row)
                    row = []
            if row:
                markup.row(*row)
            markup.row("🔙 Назад у меню")
            bot.send_message(chat_id, f"Обери існуючу збірку кнопкою або введи нову назву:", reply_markup=markup)

        elif text == "🔢 Змінити порядок":
            set_user_state(chat_id, "EDIT_POEM_ORDER")
            bot.send_message(chat_id, f"Введи число пріоритету (чим більше число, тим вище він у списках):",
                             reply_markup=back_markup())
        elif text == "🌍 Опублікувати/Сховати":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT is_public FROM poems WHERE chat_id = ? AND title = ?", (chat_id, poem_title))
            res = cursor.fetchone()
            new_status = 0 if res[0] == 1 else 1
            cursor.execute("UPDATE poems SET is_public = ? WHERE chat_id = ? AND title = ?",
                           (new_status, chat_id, poem_title))
            conn.commit()
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
            word = "відкрито для всіх!" if new_status == 1 else "заховано в приват."
            bot.send_message(chat_id, f"✅ Статус змінено. Вірш {word}", reply_markup=main_menu_markup())
        elif text == "❌ Видалити вірш":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM poems WHERE chat_id = ? AND title = ?", (chat_id, poem_title))
            conn.commit()
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id, "🗑 Вірш назавжди видалено!", reply_markup=main_menu_markup())
        return

    elif state == "RENAME_POEM":
        poem_title = USER_CONTEXT[chat_id]["poem_title"]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE poems SET title = ? WHERE chat_id = ? AND title = ?", (text, chat_id, poem_title))
        conn.commit()
        conn.close()
        set_user_state(chat_id, "MAIN_MENU")
        bot.send_message(chat_id, "Назву вірша змінено!", reply_markup=main_menu_markup())
        return

    elif state == "EDIT_POEM_TEXT":
        poem_title = USER_CONTEXT[chat_id]["poem_title"]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE poems SET content = ? WHERE chat_id = ? AND title = ?", (text, chat_id, poem_title))
        conn.commit()
        conn.close()
        set_user_state(chat_id, "MAIN_MENU")
        bot.send_message(chat_id, "Текст відредаговано!", reply_markup=main_menu_markup())
        return

    elif state == "EDIT_POEM_COLLECTION":
        poem_title = USER_CONTEXT[chat_id]["poem_title"]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE poems SET collection_name = ? WHERE chat_id = ? AND title = ?",
                       (text, chat_id, poem_title))
        conn.commit()
        conn.close()
        set_user_state(chat_id, "MAIN_MENU")
        bot.send_message(chat_id, f"Збірку змінено на '{text}'!", reply_markup=main_menu_markup())
        return

    elif state == "EDIT_POEM_ORDER":
        poem_title = USER_CONTEXT[chat_id]["poem_title"]
        if text.isdigit():
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE poems SET sort_order = ? WHERE chat_id = ? AND title = ?",
                           (int(text), chat_id, poem_title))
            conn.commit()
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
            bot.send_message(chat_id, "Порядок змінено!", reply_markup=main_menu_markup())
        else:
            bot.send_message(chat_id, "Введи коректне число.")
        return

    # --- ЛОГІКА: СПІЛЬНОТА ---
    elif state == "COMMUNITY_MENU":
        if text == "📚 Збірки спільноти":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT collection_name, username FROM poems JOIN users ON poems.chat_id = users.chat_id WHERE collection_name != 'Немає' AND is_public = 1")
            items = cursor.fetchall()
            conn.close()
            if not items:
                bot.send_message(chat_id, "Публічних збірок ще немає.")
            else:
                msg = "🌍 *Публічні збірки спільноти (натисни для копіювання):*\n\n"
                for col in items:
                    msg += f"📁 `{col[0]}` (Автор: @{col[1]})\n"
                msg += "\n\n✍️ Встав скопійовану назву збірки, яку хочеш відкрити:"
                set_user_state(chat_id, "SELECT_COMMUNITY_COLLECTION")
                bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=back_markup())
            return
        elif text == "📝 Окремі вірші":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT title, username, likes, views FROM poems JOIN users ON poems.chat_id = users.chat_id WHERE collection_name = 'Немає' AND is_public = 1")
            items = cursor.fetchall()
            conn.close()
            if not items:
                bot.send_message(chat_id, "Публічних віршів ще немає.")
            else:
                msg = "🌍 *Публічні вірші (натисни для копіювання):*\n\n"
                for p in items:
                    msg += f"📄 `{p[0]}` (Автор: @{p[1]} | ❤️ {p[2]} | 👀 {p[3]})\n"
                msg += "\n\n✍️ Встав скопійовану назву вірша для дій:"
                set_user_state(chat_id, "SELECT_COMMUNITY_POEM")
                bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=back_markup())
            return

    elif state == "SELECT_COMMUNITY_POEM":
        USER_CONTEXT[chat_id] = {"com_poem": text}
        set_user_state(chat_id, "COMMUNITY_POEM_ACTIONS")
        bot.send_message(chat_id, f"Обрано вірш '{text}'. Що зробити?", reply_markup=community_poem_actions_markup())
        return

    elif state == "COMMUNITY_POEM_ACTIONS":
        target = USER_CONTEXT.get(chat_id, {}).get("com_poem")
        if text == "📖 Читати":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE poems SET views = views + 1 WHERE title = ? AND is_public = 1", (target,))
            cursor.execute("SELECT content, likes, views FROM poems WHERE title = ? AND is_public = 1 LIMIT 1",
                           (target,))
            res = cursor.fetchone()
            conn.commit()
            conn.close()
            if res:
                bot.send_message(chat_id, f"📖 *{target}*:\n\n{res[0]}\n\n❤️ Лайків: {res[1]} | 👀 Переглядів: {res[2]}",
                                 parse_mode="Markdown", reply_markup=community_menu_markup())
            set_user_state(chat_id, "COMMUNITY_MENU")
        elif text == "👍 Лайкнути":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE poems SET likes = likes + 1 WHERE title = ? AND is_public = 1", (target,))
            conn.commit()
            conn.close()
            bot.send_message(chat_id, "❤️ Лайк зараховано!", reply_markup=community_menu_markup())
            set_user_state(chat_id, "COMMUNITY_MENU")
        elif text == "📥 Завантажити собі":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM poems WHERE title = ? AND is_public = 1 LIMIT 1", (target,))
            res = cursor.fetchone()
            if res:
                cursor.execute("INSERT INTO poems (chat_id, title, content, is_public) VALUES (?, ?, ?, 0)",
                               (chat_id, f"{target} (Копія)", res[0]))
                conn.commit()
                bot.send_message(chat_id, f"✅ Вірш завантажено як приватну копію!", reply_markup=main_menu_markup())
            conn.close()
            set_user_state(chat_id, "MAIN_MENU")
        return

    elif state == "SELECT_COMMUNITY_COLLECTION":
        USER_CONTEXT[chat_id] = {"com_col": text}
        set_user_state(chat_id, "COMMUNITY_COLLECTION_ACTIONS")
        bot.send_message(chat_id, f"Обрано збірку '{text}'. Що зробити?",
                         reply_markup=community_collection_actions_markup())
        return

    elif state == "COMMUNITY_COLLECTION_ACTIONS":
        target = USER_CONTEXT.get(chat_id, {}).get("com_col")
        if text == "👀 Переглянути":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE poems SET views = views + 1 WHERE collection_name = ? AND is_public = 1", (target,))
            cursor.execute("SELECT title, content FROM poems WHERE collection_name = ? AND is_public = 1", (target,))
            res = cursor.fetchall()
            conn.commit()
            conn.close()
            if res:
                bot.send_message(chat_id, f"📁 --- ЗБІРКА: {target} ---")
                for p in res:
                    bot.send_message(chat_id, f"📌 *{p[0]}*\n\n{p[1]}", parse_mode="Markdown")
            set_user_state(chat_id, "COMMUNITY_MENU")
            bot.send_message(chat_id, "Перегляд завершено.", reply_markup=community_menu_markup())
        elif text == "👍 Лайкнути всю":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE poems SET likes = likes + 1 WHERE collection_name = ? AND is_public = 1", (target,))
            conn.commit()
            conn.close()
            bot.send_message(chat_id, f"❤️ Усі вірші в збірці '{target}' отримали твій лайк!",
                             reply_markup=community_menu_markup())
            set_user_state(chat_id, "COMMUNITY_MENU")
        elif text == "📥 Завантажити ВСЮ":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT title, content FROM poems WHERE collection_name = ? AND is_public = 1", (target,))
            res = cursor.fetchall()
            for p in res:
                cursor.execute(
                    "INSERT INTO poems (chat_id, title, content, collection_name, is_public) VALUES (?, ?, ?, ?, 0)",
                    (chat_id, p[0], p[1], f"{target} (Копія)", 0))
            conn.commit()
            conn.close()
            bot.send_message(chat_id, f"✅ Збірку завантажено у твій профіль як приватну!",
                             reply_markup=main_menu_markup())
            set_user_state(chat_id, "MAIN_MENU")
        return

    # --- НАВІГАЦІЯ ГОЛОВНОГО МЕНЮ ---
    if state == "MAIN_MENU":
        if text == "📝 Новий вірш":
            set_user_state(chat_id, "POEM_TITLE")
            bot.send_message(chat_id, "Введи назву свого нового вірша:", reply_markup=back_markup())

        elif text == "📚 Мої вірші":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT title, collection_name, sort_order, is_public FROM poems WHERE chat_id = ? ORDER BY sort_order DESC, id ASC",
                (chat_id,))
            poems = cursor.fetchall()
            conn.close()

            if not poems:
                bot.send_message(chat_id, "У тебе ще немає збережених віршів.")
            else:
                set_user_state(chat_id, "MY_POEMS_LIST")
                msg = "📚 *Твоя творчість (натисни на назву, щоб скопіювати її):*\n\n"
                for p in poems:
                    lock = "🌍" if p[3] == 1 else "🔒"
                    msg += f"{lock} `{p[0]}`\n   ┗ 📁 Збірка: *{p[1]}* | Порядок: {p[2]}\n\n"
                msg += "✍️ Встав скопійовану *назву вірша*, щоб відкрити його:"
                bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=back_markup())

        elif text == "📁 Мої збірки":
            set_user_state(chat_id, "MY_COLLECTIONS_MENU")
            bot.send_message(chat_id, "📁 Меню керування збірками:", reply_markup=my_collections_markup())

        elif text == "🌍 Спільнота":
            set_user_state(chat_id, "COMMUNITY_MENU")
            bot.send_message(chat_id, "🌍 Категорії публічних творів:", reply_markup=community_menu_markup())


# --- ЗАПУСК БОТА ---
if __name__ == "__main__":
    print("UI Кнопки + Динамічні збірки + Читання збірок активовані!")
    bot.infinity_polling()
# FindJob Telegram Bot
# PyTelegramBotAPI + SQLite
# Один файл, готов к запуску

import telebot
from telebot import types
import sqlite3

TOKEN = "8177473838:AAFpmySFyIwc4LxS5-ujKnAx7Cj8MR6TeFA"
bot = telebot.TeleBot(TOKEN)

# --- DB ---
conn = sqlite3.connect('findjob.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT,
    name TEXT,
    company TEXT,
    contact TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    position TEXT,
    company TEXT,
    city TEXT,
    salary TEXT,
    description TEXT,
    contact TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS resumes (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    age TEXT,
    city TEXT,
    position TEXT,
    experience TEXT,
    skills TEXT,
    contact TEXT
)''')
conn.commit()

user_state = {}
temp_data = {}

# --- Keyboards ---
def start_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔍 Я ищу работу", "📢 Я ищу работника")
    return kb

def back_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⬅️ Назад")
    return kb

# --- Start ---
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id,
                     "Добро пожаловать в бот FindJob 👋",
                     reply_markup=start_kb())

# --- MAIN MENU ---
@bot.message_handler(func=lambda m: m.text == "🔍 Я ищу работу")
def seeker_menu(msg):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📄 Создать резюме", "🔎 Смотреть вакансии")
    kb.add("⬅️ Назад")
    bot.send_message(msg.chat.id, "Выберите действие:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "📢 Я ищу работника")
def employer_menu(msg):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (msg.from_user.id,))
    if not cursor.fetchone():
        user_state[msg.from_user.id] = 'reg_name'
        bot.send_message(msg.chat.id, "Введите ваше имя:")
    else:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("➕ Добавить вакансию", "📄 Смотреть резюме")
        kb.add("⬅️ Назад")
        bot.send_message(msg.chat.id, "Меню работодателя:", reply_markup=kb)

# --- REGISTRATION ---
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'reg_name')
def reg_name(msg):
    temp_data[msg.from_user.id] = {'name': msg.text}
    user_state[msg.from_user.id] = 'reg_company'
    bot.send_message(msg.chat.id, "Название компании:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'reg_company')
def reg_company(msg):
    temp_data[msg.from_user.id]['company'] = msg.text
    user_state[msg.from_user.id] = 'reg_contact'
    bot.send_message(msg.chat.id, "Контакт (телефон или @username):")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'reg_contact')
def reg_contact(msg):
    data = temp_data[msg.from_user.id]
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                   (msg.from_user.id, 'employer', data['name'], data['company'], msg.text))
    conn.commit()
    user_state.pop(msg.from_user.id)
    bot.send_message(msg.chat.id, "✅ Регистрация завершена", reply_markup=start_kb())

# --- RESUME ---
@bot.message_handler(func=lambda m: m.text == "📄 Создать резюме")
def resume_start(msg):
    user_state[msg.from_user.id] = 'r_name'
    temp_data[msg.from_user.id] = {}
    bot.send_message(msg.chat.id, "Ваше имя:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'r_name')
def r_name(msg):
    temp_data[msg.from_user.id]['name'] = msg.text
    user_state[msg.from_user.id] = 'r_age'
    bot.send_message(msg.chat.id, "Возраст:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'r_age')
def r_age(msg):
    temp_data[msg.from_user.id]['age'] = msg.text
    user_state[msg.from_user.id] = 'r_city'
    bot.send_message(msg.chat.id, "Город:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'r_city')
def r_city(msg):
    temp_data[msg.from_user.id]['city'] = msg.text
    user_state[msg.from_user.id] = 'r_position'
    bot.send_message(msg.chat.id, "Желаемая должность:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'r_position')
def r_position(msg):
    temp_data[msg.from_user.id]['position'] = msg.text
    user_state[msg.from_user.id] = 'r_exp'
    bot.send_message(msg.chat.id, "Опыт работы:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'r_exp')
def r_exp(msg):
    temp_data[msg.from_user.id]['experience'] = msg.text
    user_state[msg.from_user.id] = 'r_skills'
    bot.send_message(msg.chat.id, "Навыки:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'r_skills')
def r_skills(msg):
    temp_data[msg.from_user.id]['skills'] = msg.text
    user_state[msg.from_user.id] = 'r_contact'
    bot.send_message(msg.chat.id, "Контакт:")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'r_contact')
def r_contact(msg):
    d = temp_data[msg.from_user.id]
    cursor.execute("REPLACE INTO resumes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (msg.from_user.id, d['name'], d['age'], d['city'], d['position'],
                    d['experience'], d['skills'], msg.text))
    conn.commit()
    user_state.pop(msg.from_user.id)
    bot.send_message(msg.chat.id, "✅ Резюме сохранено", reply_markup=start_kb())

# --- EMPLOYER VIEW RESUMES ---
@bot.message_handler(func=lambda m: m.text == "📄 Смотреть резюме")
def view_resumes(msg):
    bot.send_message(msg.chat.id, "Введите должность для поиска резюме:")
    user_state[msg.from_user.id] = 'search_resume'

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == 'search_resume')
def search_resume(msg):
    cursor.execute("SELECT * FROM resumes WHERE position LIKE ?", ('%'+msg.text+'%',))
    rows = cursor.fetchall()
    if not rows:
        bot.send_message(msg.chat.id, "Резюме не найдены")
    for r in rows:
        bot.send_message(msg.chat.id,
                         f"👤 {r[1]}\nВозраст: {r[2]}\nГород: {r[3]}\n"
                         f"Должность: {r[4]}\nОпыт: {r[5]}\nНавыки: {r[6]}\n📞 {r[7]}")
    user_state.pop(msg.from_user.id)

# --- BACK ---
@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back(msg):
    bot.send_message(msg.chat.id, "Главное меню", reply_markup=start_kb())

bot.polling(none_stop=True)
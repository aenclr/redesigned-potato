import telebot
from openai import OpenAI
import os

# Читаем ключи из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Проверка наличия ключей
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN не найден!")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY не найден!")

# ========== СИСТЕМНЫЙ ПРОМПТ ДЛЯ БОТА ==========
SYSTEM_PROMPT = """Ты помогаешь, ты - добрый ассистент, пиши без форматирования текста, в официально деловом стиле кратко и по делу и вежливо, запрещены форматирования markdown в тексте."""

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Инициализация OpenRouter клиента
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Функция для отправки длинных сообщений
def send_long_message(chat_id, text):
    """Разбивает длинное сообщение на части до 4000 символов"""
    max_length = 4000
    
    if len(text) <= max_length:
        bot.send_message(chat_id, text)
    else:
        # Разбиваем на части
        for i in range(0, len(text), max_length):
            chunk = text[i:i + max_length]
            bot.send_message(chat_id, chunk)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """ ассистент"""
    
    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Показываем, что бот печатает
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Отправляем запрос в AI
        response = client.chat.completions.create(
            model="xiaomi/mimo-v2-flash:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_tokens=3000  # ← УВЕЛИЧИЛИ С 500 ДО 3000!
        )
        
        # Получаем ответ
        answer = response.choices[0].message.content
        
        # Проверяем, что ответ не пустой
        if not answer or answer.strip() == "":
            bot.reply_to(message, "❌ AI вернул пустой ответ. Попробуйте переформулировать вопрос.")
            print(f"ОШИБКА: Пустой ответ от AI для запроса: {message.text}")
            return
        
        # Отправляем ответ с разбивкой если длинный
        send_long_message(message.chat.id, answer)
        
        # Логируем для отладки
        print(f"✅ Запрос: {message.text}")
        print(f"✅ Ответ ({len(answer)} символов): {answer[:100]}...")
        
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        bot.reply_to(message, error_msg)
        print(f"ОШИБКА: {e}")
        print(f"Запрос был: {message.text}")

# Запуск бота
print("🤖 Бот-ассистент запущен!")
print(f"✅ TELEGRAM_TOKEN установлен: {bool(TELEGRAM_TOKEN)}")
print(f"✅ OPENROUTER_API_KEY установлен: {bool(OPENROUTER_API_KEY)}")
bot.polling(none_stop=True)


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
SYSTEM_PROMPT = """Кодируй диагнозы по МКБ-10. ОШИБКИ НЕДОПУСТИМЫ.

ВАЖНО:
- не путай диагнозы проверяй их дважды
- Латеральность учитывай
- Если есть ?, ставь ? в коде мкб
- Сокращения оставляй как есть

ФОРМАТ:
Строка 1: коды МКБ-10 через запятую
Строка 2: пустая
Строка 3: текст диагноза без кодов
Строка 4: текст диагноза без кодов но как написано в классификации мкб по правильному

ВСЕГДА отвечай в этом формате. НЕ возвращай пустой ответ."""



# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Инициализация OpenRouter клиента
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """👨‍⚕️ Бот для кодирования диагнозов по МКБ-10

Отправьте диагноз — получите коды МКБ-10 и текст без кодов.
"""
    
    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Показываем, что бот печатает
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Отправляем запрос в AI
        response = client.chat.completions.create(
        model="xiaomi/mimo-v2-flash",

            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        # Получаем ответ
        answer = response.choices[0].message.content
        
        # ВАЖНО: Проверяем, что ответ не пустой
        if not answer or answer.strip() == "":
            bot.reply_to(message, "❌ AI вернул пустой ответ. Попробуйте переформулировать диагноз.")
            print(f"ОШИБКА: Пустой ответ от AI для запроса: {message.text}")
            return
        
        # Отправляем ответ (обычным текстом, без Markdown для надежности)
        bot.reply_to(message, answer)
        
        # Логируем для отладки
        print(f"✅ Запрос: {message.text}")
        print(f"✅ Ответ: {answer}")
        
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        bot.reply_to(message, error_msg)
        print(f"ОШИБКА: {e}")
        print(f"Запрос был: {message.text}")

# Запуск бота
print("🤖 Бот МКБ-10 запущен!")
print(f"✅ TELEGRAM_TOKEN установлен: {bool(TELEGRAM_TOKEN)}")
print(f"✅ OPENROUTER_API_KEY установлен: {bool(OPENROUTER_API_KEY)}")
bot.polling(none_stop=True)













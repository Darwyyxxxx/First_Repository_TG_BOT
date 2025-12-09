import telebot

# ID или URL GIF-файла для "Неверно".
# Можно найти GIF на Giphy или загрузить свой и получить file_id через @get_id_bot
INVALID_INPUT_GIF_URL = 'https://media.giphy.com/media/l4pTsh45Dg7wnhw7S/giphy.gif' # Пример GIF "Nope"

def send_invalid_input_response(bot_instance: telebot.TeleBot, chat_id: int):
    """Отправляет сообщение "Неверно" и GIF."""
    try:
        bot_instance.send_animation(chat_id, INVALID_INPUT_GIF_URL, caption="Неверно! Пожалуйста, используйте кнопки или выберите игру.")
    except Exception as e:
        # Если GIF не отправился, отправляем просто текст
        bot_instance.send_message(chat_id, "Неверно! Пожалуйста, используйте кнопки или выберите игру.")
        print(f"Ошибка при отправке GIF: {e}")
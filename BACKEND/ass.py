import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot = telegram.Bot('6953394512:AAHKhZfUggTcOiAhhFtO21BqFP88w-HYOpo')

# Замените 'YOUR_CHANNEL_ID' на ID вашего канала
channel_id = '@thefoxxstuff_storage'

def get_last_message(update, context):
    # Получаем последнее сообщение из канала
    messages = bot.get_chat_history(chat_id=channel_id, limit=1)
    if messages:
        last_message = messages[0]
        update.message.reply_text(f'Последнее сообщение в канале: {last_message.text}')
    else:
        update.message.reply_text('Канал пуст или произошла ошибка.')

def main():
    updater = Updater('6953394512:AAHKhZfUggTcOiAhhFtO21BqFP88w-HYOpo', use_context=True)
    dp = updater.dispatcher

    # Обработчик команды /get_last_message
    dp.add_handler(CommandHandler('get_last_message', get_last_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

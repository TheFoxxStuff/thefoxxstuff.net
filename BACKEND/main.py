import telegram
import httpx
import asyncio

# Настройки Telegram
telegram_token = '6953394512:AAHKhZfUggTcOiAhhFtO21BqFP88w-HYOpo'
chat_id = '@thefoxxstuff_storage_bot'

# Настройки Supabase
supabase_url = 'https://zarsrubjubqpxsuasaln.supabase.co'
supabase_api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcnNydWJqdWJxcHhzdWFzYWxuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY2ODUwNzcyNywiZXhwIjoxOTg0MDgzNzI3fQ.twwpSs8Y_GUXu6OxbICbJbEyTJOaLBqNSHwaILS7bX8'
supabase_table = 'telega'

# Подключение к Telegram API
bot = telegram.Bot(token=telegram_token)

# Функция для отправки сообщения в Supabase
async def send_to_supabase(message):
    supabase_payload = {
        'message_text': message.text,
        'message_date': message.date,
    }

    headers = {
        'Content-Type': 'application/json',
        'apikey': supabase_api_key,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f'{supabase_url}/rest/v1/{supabase_table}', json=supabase_payload, headers=headers)

# Основной цикл программы
async def main():
    while True:
        updates = await bot.get_updates()
        for update in updates:
            if update.message:
                await send_to_supabase(update.message)
            # При необходимости, добавьте логику обработки сообщения и дополнительные условия

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


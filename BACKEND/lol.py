import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import supabase
from datetime import datetime

# Укажите свои данные Supabase
supabase_url = 'https://zarsrubjubqpxsuasaln.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcnNydWJqdWJxcHhzdWFzYWxuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY2ODUwNzcyNywiZXhwIjoxOTg0MDgzNzI3fQ.twwpSs8Y_GUXu6OxbICbJbEyTJOaLBqNSHwaILS7bX8'
supabase_table = 'telega'

# Инициализация Supabase
supabase_client = supabase.Client(supabase_url, supabase_key)

# URL целевой страницы для парсинга
url = 'https://thefoxxstuff.net'

# Отправляем GET-запрос и получаем HTML-код страницы
response = requests.get(url)

if response.status_code == 200:
    # Используем BeautifulSoup для анализа HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлекаем все ссылки (ссылки)
    links = soup.find_all('a')
    
    # Получаем текущую дату и время
    current_time = datetime.now().isoformat()

    # Перебираем найденные ссылки и извлекаем их адреса
    for link in links:
        href = link.get('href')
        if href:
            # Если ссылка относительная, преобразуем ее в абсолютный URL
            if not urlparse(href).netloc:
                href = url + href
            
            try:
                # Попытка вставки извлеченного адреса в Supabase
                response = supabase_client.table(supabase_table, schema="public").upsert([
                    {'url': href, 'created_at': current_time}
                ], returning='minimal')
                if response['status_code'] == 201:
                    print(f'Успешно добавлен URL: {href}')
                else:
                    print(f'Ошибка при добавлении URL: {href}')
            except Exception as e:
                print(f'Ошибка при добавлении URL: {href}')
                print(f'Ошибка: {str(e)}')

else:
    print('Ошибка при получении страницы:', response.status_code)







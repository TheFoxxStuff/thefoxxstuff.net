import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Укажите ваш URL и настройки Xata.io API
url = 'https://halleylabs.com'
xata_io_url = 'https://Aytal-Popov-s-workspace-ktdj1r.eu-central-1.xata.sh/db/thefoxxstuff'
xata_io_api_key = 'xau_3PsXvtzPtoJvJ3AMkBUZjSruG6C1wC7j1'

# Отправляем GET-запрос и получаем HTML-код страницы
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')

    for link in links:
        href = link.get('href')
        if href:
            if not urlparse(href).netloc:
                href = url + href

            # Теперь отправим данные в Xata.io в таблицу "Urls"
            xata_io_data = {
                'url': href
            }

            xata_io_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {xata_io_api_key}'
            }

            xata_io_response = requests.post(
                f'{xata_io_url}/your-endpoint',  # Замените 'your-endpoint' на фактический эндпоинт Xata.io для создания записей
                json=xata_io_data,
                headers=xata_io_headers
            )

            if xata_io_response.status_code == 201:
                print(f'Successfully added {href} to Xata.io')
            else:
                print(f'Failed to add {href} to Xata.io')

else:
    print('Error getting the page:', response.status_code)

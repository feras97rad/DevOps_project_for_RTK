'''
Создание БД
Создаем БД, состоящую из 3-х полей в формате string
'''

CREATE TABLE accounts (
    username String,
    ipv4 String,
    mac String
) ENGINE MergeTree ORDER BY (username);

'''
Заполнение таблицы сгенерированными данными
Создаем 3 функции для генерации данных в соответствующих форматах
username - буквенные обозначения
ipv4 - как и принято 4 октета с цифрами от 0 до 255
mac -  это двузначное шестнадцатеричное число (для простоты обошлись без букв)
Всего будет 10 000 записей
'''

import random
import string

def generate_username():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

def generate_ipv4():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def generate_mac():
    return ':'.join('%02x' % random.randint(0, 255) for _ in range(6))

# Устанавливаем количество записей
n = 10000

# Генерируем данные и записываем их в переменную data
data = [(generate_username(), generate_ipv4(), generate_mac()) for _ in range(n)]

# Грузим данные в таблицу
insert_query = "INSERT INTO accounts (username, ipv4, mac) VALUES"
with open('data.csv', 'w') as f:
    f.write(','.join(['username', 'ipv4', 'mac']))
    f.write('\n')
    for row in data:
        f.write(','.join(row))
        f.write('\n')

# Импортируем таблицу в ClickHouse
clickhouse-client --query="LOAD DATA INFILE 'data.csv' INTO TABLE accounts FORMAT CSV"





# 2) Реализация сервиса


import redis
from clickhouse_driver import Client
import requests
import json

# Подключение к Redis
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
except redis.ConnectionError as e:
    print(f"Ошибка подключения к Redis: {e}")
    exit(1)

# Подключение к ClickHouse
try:
    clickhouse_client = Client(host='localhost', port=8123)
except clickhouse_driver.errors.ClickHouseException as e:
    print(f"Ошибка подключения к ClickHouse: {e}")
    exit(1)

# Функция для поиска имени пользователя
def search_username(ipv4, mac):
  query = f"SELECT username FROM table_name WHERE ipv4 = '{ipv4}' AND mac = '{mac}'"
  result = clickhouse_client.execute(query)
  if result:
    return result[0][0] # Предполагается, что результатом будет одна запись
  else:
    return None

# Функция для отправки данных во внешний сервис
def send_to_external_service(data):
    try:
        response = requests.post('https://pastebin.com/api/api_post.php', data=data)
    except requests.exceptions.ConnectionError as e:
        print(f"Ошибка подключения к внешнему сервису: {e}")
        exit(1)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Функция для парсинга задачи
def process_task(task):
    task_id = task['id']
    ipv4 = task['ipv4']
    mac = task['mac']

    # Поиск username
    username = search_username(ipv4, mac)

    if username:
    # Формирование JSON с результатом поиска
    result = {'id': task_id, 'username': username}
    json_result = json.dumps(result)

    # Отправка результатов во внешний сервис
    response = send_to_external_service(json_result)
    if response:
      # Сохранение URL на рез-тат успешного поиска в файл
      with open('successful_searches.txt', 'a') as f:
        f.write(response + '\n')
    else:
      print("Не удалось отправить результаты во внешний сервис")
    else:
    print("Username не найден")

def main():
  while True:
        task_json, _ = redis_client.blpop('tasks', timeout=1)

        if task_json is None:
            print("Очередь задач пуста")
            continue

        # Парсинг JSON задачи
        task = json.loads(task_json)

        # Обработка задачи
        process_task(task)

if __name__ == "__main__":
  main()

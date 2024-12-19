import time
import sqlite3
from rcon import RCON

# Данные для подключения к серверу Rust через RCON
host = '127.0.0.1'  # IP адрес вашего сервера
port = 28016         # Порт RCON сервера
password = 'your_rcon_password'  # RCON пароль

# Создание или подключение к базе данных
conn = sqlite3.connect('example.db')

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()

# Создание таблицы (если она еще не существует)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        last_join TEXT NOT NULL
    )
''')

# Функция для добавления нового пользователя в базу данных
def add_user(name, status, last_join):
    # Вставляем данные в таблицу
    cursor.execute('''
        INSERT INTO users (name, status, last_join)
        VALUES (?, ?, ?)
    ''', (name, status, last_join))

    # Сохраняем изменения
    conn.commit()

# Подключение к серверу через RCON и получение информации о игроках
def get_players():
    with RCON(host, port, password) as rcon:
        # Выполнение команды для получения информации о текущих игроках
        response = rcon.command("status")
        return response

# Обработка информации о текущих игроках и добавление в базу данных
def process_players():
    players_info = get_players()

    # Примерный парсинг ответа команды 'status' (будет зависеть от формата ответа)
    if players_info:
        lines = players_info.split("\n")
        for line in lines:
            # Здесь нужно адаптировать парсинг в зависимости от формата вывода сервера
            # Пример строки: "Player1 10.0.0.1 id: 12345 time: 1642023432"
            parts = line.split()  # Пытаемся разделить строку на части

            if len(parts) > 2:
                name = parts[0]
                last_join_timestamp = int(parts[-1])  # Предполагаем, что время последнего входа в конце строки

                # Преобразуем timestamp в читаемый формат
                last_join = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_join_timestamp))

                # Статус: Если игрок в списке - "online", иначе "offline"
                status = "online" if name else "offline"

                # Добавляем пользователя в базу данных
                add_user(name, status, last_join)

# Основной цикл для обновления базы данных
if __name__ == "__main__":
    process_players()

    # Закрытие соединения с базой данных после обновления
    conn.close()

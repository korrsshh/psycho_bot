import aiosqlite
from datetime import datetime
from typing import List, Optional, Tuple
from config import Config

class Database:
    def __init__(self):
        self.db_path = Config.DB_PATH
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    test_result TEXT,
                    test_completed_at TIMESTAMP,
                    answers TEXT
                )
            ''')
            await db.commit()
    
    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        """Добавление нового пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO users (id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username or "", first_name or "", last_name or ""))
            await db.commit()
    
    async def update_test_result(self, user_id: int, result: str, answers: List[str]):
        """Обновление результата теста"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users
                SET test_result = ?, test_completed_at = CURRENT_TIMESTAMP, answers = ?
                WHERE id = ?
            ''', (result, ",".join(answers), user_id))
            await db.commit()
    
    async def get_all_users(self) -> List[int]:
        """Получение всех пользователей для рассылки"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT id FROM users') as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def get_new_users_today(self) -> List[Tuple]:
        """Получение новых пользователей за сегодня"""
        today = datetime.now().strftime('%Y-%m-%d')
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT id, username, first_name, last_name, test_result, test_completed_at, answers
                FROM users 
                WHERE DATE(registered_at) = ?
                ORDER BY registered_at DESC
            ''', (today,)) as cursor:
                return await cursor.fetchall()
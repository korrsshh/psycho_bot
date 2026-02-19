from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import asyncio

from states import TestStates
from database import Database
from texts.admin import (
    ADMIN_BROADCAST_START, 
    ADMIN_BROADCAST_COMPLETE,
    ADMIN_STATS
)
from config import Config

router = Router()
db = Database()

@router.message(Command("message"))
async def cmd_message(message: Message, state: FSMContext):
    if message.from_user.id != Config.ADMIN_ID:
        await message.answer("❌ У вас нет прав для использования этой команды")
        return
    
    await message.answer(ADMIN_BROADCAST_START)
    await state.set_state(TestStates.broadcast)

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("Операция отменена ✅")
    else:
        await message.answer("Нет активных операций для отмены")

@router.message(TestStates.broadcast)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != Config.ADMIN_ID:
        await state.clear()
        return
    
    users = await db.get_all_users()
    total = len(users)
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await message.send_copy(chat_id=user_id)
            success += 1
        except Exception as e:
            failed += 1
            print(f"Не удалось отправить {user_id}: {e}")
        await asyncio.sleep(0.05)
    
    await message.answer(
        ADMIN_BROADCAST_COMPLETE.format(
            total=total,
            success=success,
            failed=failed
        )
    )
    await state.clear()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != Config.ADMIN_ID:
        await message.answer("❌ У вас нет прав для использования этой команды")
        return
    
    users = await db.get_all_users()
    today_users = await db.get_new_users_today()
    
    stats_text = ADMIN_STATS.format(
        total=len(users),
        today=len(today_users)
    )
    
    if today_users:
        for user in today_users[:5]:
            name = f"{user[2]} {user[3] or ''}".strip() or "Без имени"
            username = f"@{user[1]}" if user[1] else "—"
            result = user[4] or "не завершил(а) тест"
            stats_text += f"\n• {name} ({username}) — {result}"
    else:
        stats_text += "\nСегодня новых пользователей нет"
    
    await message.answer(stats_text)
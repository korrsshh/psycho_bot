from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime

from states import TestStates
from database import Database
from keyboards.inline import (
    welcome_keyboard, about_keyboard, 
    question_keyboard, result_keyboard,
    subscribe_required_keyboard, subscribe_confirmed_keyboard
)
from texts.greetings import WELCOME_TEXT, ABOUT_TEXT
from texts.questions import QUESTIONS
from texts.results import RESULT_INTERPRETATIONS, FINAL_MESSAGE
from texts.subscription import (
    SUBSCRIBE_REQUIRED, SUBSCRIBE_CONFIRMED, 
    SUBSCRIBE_NOT_CONFIRMED, ALREADY_SUBSCRIBED
)
from utils import calculate_result, format_answers_for_admin, check_subscription
from config import Config

router = Router()
db = Database()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    
    user = message.from_user
    await db.add_user(
        user.id,
        user.username,
        user.first_name,
        user.last_name
    )
    
    # Проверяем подписку
    is_subscribed = await check_subscription(bot, user.id)
    
    if is_subscribed:
        await message.answer(ALREADY_SUBSCRIBED, reply_markup=subscribe_confirmed_keyboard())
    else:
        await message.answer(SUBSCRIBE_REQUIRED, reply_markup=subscribe_required_keyboard())

@router.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(ABOUT_TEXT, reply_markup=about_keyboard())

@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    is_subscribed = await check_subscription(bot, callback.from_user.id)
    
    if is_subscribed:
        await callback.message.edit_text(
            SUBSCRIBE_CONFIRMED,
            reply_markup=subscribe_confirmed_keyboard()
        )
    else:
        await callback.answer("❌ Вы не подписаны на канал", show_alert=True)
        await callback.message.edit_text(
            SUBSCRIBE_NOT_CONFIRMED,
            reply_markup=subscribe_required_keyboard()
        )

@router.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    # Финальная проверка подписки перед началом теста
    is_subscribed = await check_subscription(bot, callback.from_user.id)
    
    if not is_subscribed:
        await callback.message.edit_text(
            SUBSCRIBE_REQUIRED,
            reply_markup=subscribe_required_keyboard()
        )
        await callback.answer("🔐 Требуется подписка на канал", show_alert=True)
        return
    
    await state.set_state(TestStates.q1)
    await state.update_data(answers=[])
    
    await callback.message.edit_text(
        QUESTIONS[0],
        reply_markup=question_keyboard(0)
    )

@router.callback_query(F.data == "prev_question")
async def prev_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    current_state = await state.get_state()
    if not current_state:
        await callback.message.answer("Ошибка состояния. Начните тест заново /start")
        return
    
    state_name = current_state.split(":")[1]
    question_map = {
        "q2": 0, "q3": 1, "q4": 2, "q5": 3,
        "q6": 4, "q7": 5, "q8": 6
    }
    prev_q_index = question_map.get(state_name)
    
    if prev_q_index is None:
        await callback.message.answer("Невозможно вернуться назад")
        return
    
    data = await state.get_data()
    answers = data.get("answers", [])
    
    if answers:
        answers.pop()
        await state.update_data(answers=answers)
    
    prev_state = getattr(TestStates, f"q{prev_q_index + 1}")
    await state.set_state(prev_state)
    
    await callback.message.edit_text(
        QUESTIONS[prev_q_index],
        reply_markup=question_keyboard(prev_q_index)
    )

@router.callback_query(F.data.startswith("ans_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    current_state = await state.get_state()
    if not current_state:
        await callback.message.answer("Ошибка состояния. Начните тест заново /start")
        return
    
    state_name = current_state.split(":")[1]
    question_map = {
        "q1": 0, "q2": 1, "q3": 2, "q4": 3,
        "q5": 4, "q6": 5, "q7": 6, "q8": 7
    }
    q_index = question_map.get(state_name, -1)
    
    if q_index == -1:
        await callback.message.answer("Ошибка состояния. Начните тест заново /start")
        await state.clear()
        return
    
    answer = callback.data.split("_")[1]
    data = await state.get_data()
    answers = data.get("answers", [])
    answers.append(answer)
    await state.update_data(answers=answers)
    
    # Последний вопрос
    if q_index == 7:
        result = calculate_result(answers)
        await db.update_test_result(callback.from_user.id, result, answers)
        
        # Формируем сообщение с результатом (с красивым оформлением)
        result_header = {
            "A": "◽️ <b>Результат: «Тихий тупик»</b>",
            "B": "◾️ <b>Результат: «Перегруженная женщина»</b>",
            "C": "▪️ <b>Результат: «Подавленная близость»</b>"
        }
        
        result_text = (
            "✅ <b>Тест завершён</b>\n\n"
            f"{result_header[result]}\n\n"
            f"{RESULT_INTERPRETATIONS[result]}\n\n"
            f"{FINAL_MESSAGE}"
        )
        
        await callback.message.edit_text(
            result_text,
            reply_markup=result_keyboard(Config.PSYCHOLOGIST_USERNAME)
        )
        
        # Уведомляем админа
        await notify_admin_new_user(bot, callback.from_user, result, answers)
        
        await state.clear()
    else:
        next_state = getattr(TestStates, f"q{q_index + 2}")
        await state.set_state(next_state)
        
        await callback.message.edit_text(
            QUESTIONS[q_index + 1],
            reply_markup=question_keyboard(q_index + 1)
        )

async def notify_admin_new_user(bot: Bot, user, result: str, answers: list):
    """Отправка уведомления админу о новом пользователе"""
    from texts.admin import ADMIN_NEW_USER_NOTIFICATION
    
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "не указан"
    
    notification = ADMIN_NEW_USER_NOTIFICATION.format(
        date=datetime.now().strftime('%d.%m.%Y %H:%M'),
        user_id=user.id,
        full_name=full_name,
        username=username,
        result=result,
        answers=format_answers_for_admin(answers)
    )
    
    try:
        await bot.send_message(
            Config.ADMIN_ID,
            notification,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления админу: {e}")
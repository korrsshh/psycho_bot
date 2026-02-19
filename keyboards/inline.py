from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from texts.questions import OPTIONS
from config import Config

def welcome_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✨ Начать диагностику", callback_data="start_test")
    builder.button(text="ℹ️ Подробнее о тесте", callback_data="about")
    builder.adjust(1)
    return builder.as_markup()

def about_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✨ Начать диагностику", callback_data="start_test")
    builder.adjust(1)
    return builder.as_markup()

def subscribe_required_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Перейти в канал", url=Config.CHANNEL_INVITE_LINK or f"https://t.me/{Config.CHANNEL_ID.lstrip('@')}")
    builder.button(text="🔍 Проверить подписку", callback_data="check_subscription")
    builder.adjust(1)
    return builder.as_markup()

def subscribe_confirmed_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✨ Начать диагностику", callback_data="start_test")
    builder.adjust(1)
    return builder.as_markup()

def question_keyboard(q_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for text, callback_data in OPTIONS[q_index]:
        builder.button(text=text, callback_data=f"ans_{callback_data}")
    
    # Кнопка "Назад" для вопросов 2-8
    if q_index > 0:
        builder.button(text="🔙 Вернуться к предыдущему вопросу", callback_data="prev_question")
    
    builder.adjust(1)
    return builder.as_markup()

def result_keyboard(psychologist_username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📅 Записаться на консультацию", 
        url=f"https://t.me/{psychologist_username.lstrip('@')}"
    )
    builder.button(
        text="🔄 Пройти диагностику ещё раз", 
        callback_data="start_test"
    )
    builder.adjust(1)
    return builder.as_markup()
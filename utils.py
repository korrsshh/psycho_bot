from collections import Counter
from typing import List
from aiogram import Bot
from config import Config

def calculate_result(answers: List[str]) -> str:
    """
    Расчет результата теста на основе ответов.
    В случае ничьей выбираем первый вариант по приоритету A > B > C
    """
    counts = Counter(answers)
    max_count = max(counts.values())
    
    for option in ["A", "B", "C"]:
        if counts.get(option, 0) == max_count:
            return option
    
    return "B"  # Фолбэк

def format_answers_for_admin(answers: List[str]) -> str:
    """Форматирование ответов для админского уведомления с красивым оформлением"""
    questions = [
        "Когда вы думаете о своих отношениях, вы чаще чувствуете:",
        "Когда вам больно или обидно, вы обычно:",
        "В отношениях вы чаще ощущаете себя:",
        "Ощущение, что вас по-настоящему слышат:",
        "Если вы перестанете быть удобной, вам кажется, что:",
        "Какая мысль вам ближе:",
        "Если представить будущее через несколько лет, вам:",
        "Самая точная фраза про ваше состояние сейчас:"
    ]
    
    formatted = []
    for i, (q, ans) in enumerate(zip(questions, answers), 1):
        emoji = "◽️" if ans == "A" else "◾️" if ans == "B" else "▪️"
        formatted.append(f"{emoji} <b>{i}.</b> {q}\n   → Ответ: <b>{ans}</b>")
    
    return "\n\n".join(formatted)

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """
    Проверка подписки пользователя на канал.
    Возвращает True, если пользователь подписан.
    
    Важно: бот должен быть админом канала!
    """
    try:
        member = await bot.get_chat_member(Config.CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator", "owner"]
    except Exception as e:
        print(f"Ошибка проверки подписки для {user_id}: {e}")
        return False
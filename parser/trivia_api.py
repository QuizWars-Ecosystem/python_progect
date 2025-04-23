import asyncio
import aiohttp
import random
from aiohttp import ClientError

from db.fn import create_tables, add_db, remove_db

API_URL = "https://opentdb.com/api.php"

async def get_request(count: int = 50) -> list[dict]:
    try:
        while True:
            USER_AGENTS = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://opentdb.com/", }
            params = {"amount": count}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(API_URL, params=params) as responce:
                    if responce.status == 429:
                        print(f"Слишком много запросов (429)! Жду..........")
                        await asyncio.sleep(random.uniform(10.0, 16.0))

                    if responce.status != 200 and responce.status != 429:
                        print(f"Code responce: {responce.status}. Джу 4 сек.....")
                        await asyncio.sleep(4)
                        continue

                    questions = await responce.json()
                    if not questions or "results" not in questions:
                        print(f"Некорректный ответ API. Повтор через 4 сек....")
                        await asyncio.sleep(4)
                        continue

                    return questions['results']
    except ClientError as e:
        print(f"Ошибка сети: {str(e)}. Жду 4 сек.....")
        await asyncio.sleep(4)

async def main():
    await create_tables()
    while True:
        questions_list = await get_request()
        for question in questions_list:
            await add_db(
                que_text=question['question'],                      # Текст вопроса
                complexity=question.get('difficulty', 'easy'),      # Сложность (с fallback)
                category=question['category'],                      # Категория
                correct_answer=question['correct_answer'],          # Правильный ответ
                incorrect_answers=question['incorrect_answers'],    # Неправильные ответы
                verified=False,                                      # Пример дополнительного параметра
                lang="en")                                          # Язык
        print("Sleep................")
        await asyncio.sleep(random.uniform(4.0, 7.5))

if __name__ == "__main__":
    asyncio.run(main())

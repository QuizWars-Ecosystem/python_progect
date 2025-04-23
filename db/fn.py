import asyncio
import hashlib
from sqlalchemy import text
from bs4 import BeautifulSoup

from db.models import Questions, Options, Categories
from db.database import async_engine, async_session_factory, Base


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def add_db(que_text: str,
                 complexity: str,
                 category: str,
                 correct_answer: str,
                 incorrect_answers: list[str],
                 verified: bool = False,
                 lang: str = "en") -> bool:
    try:
        soup = BeautifulSoup(que_text, "html.parser")
        clean_text = soup.get_text().replace("\"", "\'")
        hash_text = hashlib.sha256(clean_text.strip().lower().encode()).hexdigest()
        async with async_engine.begin() as conn:
            res = await conn.execute(text("SELECT hash FROM hashs WHERE hash = :hash"), {"hash": hash_text})
            if res.fetchone():  # если хеш уже есть в бд
                return False

            # Хеш
            hash_id = await conn.execute(text("""INSERT INTO hashs (hash) 
            VALUES (:hash) RETURNING id"""), {"hash": hash_text})
            hash_id = hash_id.scalar()

            # Категория
            category_id = await conn.execute(text("""
                INSERT INTO categories (name)
                VALUES (:category)
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id"""), {"category": category})
            category_id = category_id.scalar()

            # Вопрос
            question_id = await conn.execute(text("""
                INSERT INTO questions (text, verified, complexity, lang, category_id)
                VALUES (:text, :verified, :complexity, :lang, :category_id)
                RETURNING id"""), {"text": clean_text, "verified": verified, "complexity": complexity, "lang": lang,"category_id": category_id})
            question_id = question_id.scalar()

            # Правильный ответ
            soup2 = BeautifulSoup(correct_answer, "html.parser")
            clean_cor_answ = soup2.get_text()
            await conn.execute(text("""INSERT INTO options (question_id, text, is_correct)
            VALUES (:question_id, :text, TRUE)"""), {"question_id":question_id, "text": clean_cor_answ})

            # Неправильные ответы
            for answer in incorrect_answers:
                soup3 = BeautifulSoup(answer, "html.parser")
                clean_answer = soup3.get_text()
                await conn.execute(text("""INSERT INTO options (question_id, text, is_correct)
                VALUES (:question_id, :text, FALSE)"""), {"question_id": question_id, "text": clean_answer})

    except Exception as e:
        print(f"Error: {e}")
        return False
    return True


async def remove_db(que_text: str) -> bool:
    try:
        async with async_engine.begin() as conn:
            soup = BeautifulSoup(que_text, "html.parser")
            clean_text = soup.get_text()
            res = await conn.execute(text("""SELECT id FROM questions
            WHERE text = :text"""), {"text": clean_text})

            question_row = res.fetchone()
            print(f"{question_row=}")
            if not question_row:
                print(f"Вопрос не найден: {que_text}")
                return False

            question_id = question_row[0]

            # Удаляем ответы
            await conn.execute(text("""DELETE FROM options 
            WHERE question_id = :question_id"""), {"question_id": question_id})

            # Сам вопрос
            await conn.execute(text("""DELETE FROM questions WHERE id = :question_id"""), {"question_id": question_id})
            print(f"Удалили вопрос: {que_text} с его id: {question_id} и его ответы")

            return True

    except Exception as e:
        print(f"Error: {e}")
        return False


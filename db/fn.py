import asyncio
import hashlib
from sqlalchemy import text

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
        hash_text = hashlib.sha256(que_text.strip().lower().encode()).hexdigest()
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
                INSERT INTO questions (text, verified, complexity, lang, hash_id, category_id)
                VALUES (:text, :verified, :complexity, :lang, :hash_id, :category_id)
                RETURNING id"""), {"text": que_text, "verified": verified,
                                   "complexity": complexity, "lang": lang,
                                   "hash_id": hash_id, "category_id": category_id})
            question_id = question_id.scalar()

            # Правильный ответ
            await conn.execute(text("""INSERT INTO options (question_id, text, is_correct)
            VALUES (:question_id, :text, TRUE)"""), {"question_id":question_id, "text": correct_answer})

            # Неправильные ответы
            for answer in incorrect_answers:
                await conn.execute(text("""INSERT INTO options (question_id, text, is_correct)
                VALUES (:question_id, :text, FALSE)"""), {"question_id": question_id, "text": answer})

    except Exception as e:
        print(f"Error: {e}")
        return False
    return True


async def remove_db(que_text: str) -> bool:
    try:
        async with async_engine.begin() as conn:
            hash_text = hashlib.sha256(que_text.strip().lower().encode()).hexdigest()
            res = await conn.execute(text("""SELECT hash FROM hashs WHERE hash = :hash"""), {"hash": hash_text})
            if not res.scalar():
                return False

            question_id = await conn.execute(text("""
            SELECT q.id FROM questions AS q
            JOIN hashs AS h
            ON q.hash_id = h.id
            WHERE h.hash = :hash"""), {"hash": hash_text})
            question_id = question_id.scalar()
            if question_id: # Если есть вопрос, удаляем ответы
                await conn.execute(text("""DELETE FROM options 
                WHERE question_id = :question_id"""), {"question_id": question_id})

                # Сам вопрос
                await conn.execute(text("""DELETE FROM questions WHERE id = :question_id"""), {"question_id": question_id})
                print(f"Удалили вопрос {question_id} и его ответы")
            else:
                print("У этого хэша нет связанного вопроса и ответов")

            return True

    except Exception as e:
        print(f"Error: {e}")

# async def main():
#     await create_tables()
#     await add_db(
#         que_text="Какой язык программирования самый популярный?",
#         complexity="easy",
#         category="Программирование",
#         correct_answer="Python",
#         incorrect_answers=["Java", "C++", "PHP"],
#         verified=True,
#         lang="ru")
#     await asyncio.sleep(10)
#     await remove_db("Какой язык программирования самый популярный?")
#
# asyncio.run(main())

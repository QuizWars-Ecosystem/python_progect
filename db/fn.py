import hashlib
from datetime import datetime
from sqlalchemy import text
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any

from db.models import Questions, Options, Categories, Scheduler
from db.database import async_engine, async_session_factory, Base


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_question_to_db(que_text: str,
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


async def remove_question_to_db(que_text: str) -> bool:
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


async def get_questions_pagination(count: int = 100, verified: bool = None,
                                   complexity: str = None, lang: str = "en",
                                   category: str = None) -> list[dict]:
    try:
        async with async_engine.connect() as conn:
            query = ("""
                SELECT
                    q.id,
                    q.text,
                    q.verified,
                    q.complexity,
                    q.lang,
                    c.name as category_name
                FROM questions AS q
                LEFT JOIN categories AS c ON q.category_id = c.id
                WHERE 1=1""")
            params = {}

            if verified is not None:
                query += " AND q.verified = :verified"
                params["verified"] = verified
            if complexity:
                query += " AND q.complexity = :complexity"
                params["complexity"] = complexity
            if lang:
                query += " AND q.lang = :lang"
                params["lang"] = lang
            if category:
                query += " AND c.name = :category"
                params["category"] = category.strip().capitalize()

            query += " ORDER BY q.id LIMIT :count"
            params["count"] = count

            res = await conn.execute(text(query), params)
            questions = res.fetchall()
            if not questions:
                return []

            question_ids_list = [q[0] for q in questions]
            options_query = """
                SELECT id, question_id, text, is_correct
                FROM options WHERE question_id = ANY(:question_ids_list)
                ORDER BY question_id, id"""
            options_res = await conn.execute(text(options_query), {"question_ids_list": question_ids_list})
            options = options_res.fetchall()

            questions_res = []
            for q in questions:
                question_data = {
                    "id": q[0],
                    "text": q[1],
                    "verified": q[2],
                    "complexity": q[3],
                    "lang": q[4],
                    "category": q[5],
                    "options":
                        [{
                            "id": opt[0],
                            "question_id": opt[1],
                            "text": opt[2],
                            "is_correct": opt[3]
                        }for opt in options if opt[1] == q[0]]
                }
                questions_res.append(question_data)
            return questions_res

    except Exception as e:
        print(f"Error: {e}")




# Scheduler
async def create_scheduler_job(id: int, name: str, url: str,
                               state:str, mode: str, schedule: str,
                               interval: int, next_run: datetime, last_run: datetime) -> bool:
    async with async_engine.connect() as conn:
        try:
            query = ("""INSERT INTO scheduler VALUES (
                    :name,
                    :url,
                    :state,
                    :mode,
                    :schedule,
                    :interval,
                    :next_run,
                    :last_run)""")
            await conn.execute(query, {"name": name, "url": url, "state": state, "mode": mode,
            "schedule": schedule, "interval": interval, "next_run": next_run, "last_run": last_run})
            await conn.commit()
            return True
        except Exception as e:
            print(f"Error adding task to database: {e}")
            return False


async def get_all_jobs() -> List[Dict[str, Any]]:
    """БД запрос на получение всех задач сервера."""
    async with async_engine.connect() as conn:
        try:
            query = ("""
                SELECT
                    s.id,
                    s.name,
                    s.url,
                    s.state,
                    s.mode,
                    s.schedule,
                    s.interval,
                    s.next_run,
                    s.last_run
                FROM scheduler AS s""")
            res = await conn.execute(text(query))
            jobs = res.mappings().all()  # Получаем результаты как словари
            if not jobs:
                return False
            return [dict(job) for job in jobs]
        except Exception as e:
            print(f"Database fetch error: {e}")
            return False


async def change_mode_by_id(id: int, mode: str,
                            schedule: Optional[str] = None,
                            interval: Optional[int] = None) -> bool:
    """БД запрос на изменение режима существующей задачи и присвоение ей новой конфигурации."""
    async with async_engine.connect() as conn:
        try:
            update_data = {
                "mode": mode,
                "state": "WORKING"}
            if mode == "CRON":
                update_data["schedule"] = schedule
                update_data["interval"] = None
            else:
                update_data["schedule"] = None
                update_data["interval"] = interval

            await conn.execute(text("""UPDATE scheduler
                                        SET mode = :mode,
                                            schedule = :schedule,
                                            interval = :interval,
                                            state = :state
                                        WHERE id = :id"""),
                                        {"id": id, **update_data})
            await conn.commit()
            return True
        except Exception as e:
            print(f"Error changing job mode: {e}")
            return False


async def change_parameters_by_id(id: int,
                                  schedule: Optional[str] = None,
                                  interval: Optional[int] = None) -> bool:
    """БД изменение параметров существующей задачи (CRON/TIMER)"""
    async with async_engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT mode FROM scheduler WHERE id = :id"), {"id": id})
            current_mode = res.scalar_one()

            if current_mode == "CRON" and schedule:
                await conn.execute(
                    text("""UPDATE scheduler 
                                SET schedule = :schedule 
                            WHERE id = :id"""),
                            {"id": id, "schedule": schedule})
                await conn.commit()
            elif current_mode == "TIMER" and interval:
                await conn.execute(
                    text("""UPDATE scheduler 
                                SET interval = :interval 
                            WHERE id = :id"""),
                            {"id": id, "interval": interval})
                await conn.commit()
            else:
                raise ValueError("Invalid parameters for current job mode")

            return True
        except Exception as e:
            print(f"Error changing job mode: {e}")
            return False


async def change_state_job_by_id(id: int, action: str,
                                 start_at: Optional[datetime] = None) -> bool:
    """БД управление состоянием задачи (старт/пауза/остановка)"""
    async with async_engine.connect() as conn:
        try:
            update_data = {"state": action.upper()}

            if action.upper() == "PAUSED" and start_at:
                update_data["next_run"] = start_at

            await conn.execute(
                text("""UPDATE scheduler 
                        SET state = :state, 
                            next_run = :next_run
                        WHERE id = :id"""),
                {"id": id, **update_data})
            await conn.commit()
            return True
        except Exception as e:
            print(f"Error changing job state: {e}")
            return False


async def update_job_timestamps(id: int,
                                last_run: datetime,
                                next_run: Optional[datetime] = None) -> bool:
    """Обновление временных меток задачи"""
    async with async_engine.connect() as conn:
        try:
            update_data = {"last_run": last_run}
            if next_run:
                update_data["next_run"] = next_run

            await conn.execute(
                text("""UPDATE scheduler 
                        SET last_run = :last_run, 
                            next_run = :next_run
                        WHERE id = :id"""),
                        {"id": id, **update_data})
            await conn.commit()
            return True
        except Exception as e:
            print(f"Error updating job timestamps: {e}")
            return False


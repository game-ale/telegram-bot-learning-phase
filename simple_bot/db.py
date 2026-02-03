import os
import asyncpg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return await asyncpg.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

async def init_db():
    """Initializes the database by creating the users table if it doesn't exist."""
    conn = await get_db_connection()
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                bio TEXT
            )
        ''')
        logger.info("Database initialized and table 'users' checked/created.")
    finally:
        await conn.close()

async def save_user(name, age, bio):
    """Saves a new user to the database."""
    conn = await get_db_connection()
    try:
        await conn.execute('''
            INSERT INTO users (name, age, bio) VALUES ($1, $2, $3)
        ''', name, int(age), bio)
        logger.info(f"User {name} saved to database.")
    finally:
        await conn.close()

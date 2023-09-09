import os

import asyncpg

DB_HOST = 'localhost'
DB_PORT = os.environ.get("DB_PORT", 5432)
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = os.environ.get("DB_PASS", "dbpass")

pool = None


async def init():
    global pool
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    await conn.execute('CREATE TABLE IF NOT EXISTS honkai_user(id char(20) UNIQUE, uid integer);')
    await conn.close()
    pool = await get_connection()


async def get_connection():
    return await asyncpg.create_pool('postgresql://{user}:{password}@{host}:{port}/{dbname}'
    .format(
        user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
    ))


async def getdatabase(userid, id, default=None, table="honkai_user"):
    global pool
    async with pool.acquire() as conn:
        rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
        if rows is None:
            if table == "honkai_user":
                await conn.execute(f'INSERT INTO {table} (id) VALUES ($1);', (str(userid)))
                rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
            elif table == "guild":
                await conn.execute(f'INSERT INTO {table} (id) VALUES ($1);', (str(userid)))
                rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
        if rows[0] is None:
            return default
        else:
            return rows[0]


async def setdatabase(userid, id, value, table="honkai_user"):
    global pool
    async with pool.acquire() as conn:
        rows = await conn.fetchrow(f'SELECT {id} from {table} where "id" = $1;', (str(userid)))
        if rows is None:
            await conn.execute('INSERT INTO honkai_user (id) VALUES ($1);', (str(userid)))
            rows = await conn.fetchrow('SELECT voiceid from honkai_user where id = $1;', (str(userid)))
        await conn.execute(f'UPDATE {table} SET {id} = $1 WHERE "id" = $2;', value, str(userid))
        return rows[0]

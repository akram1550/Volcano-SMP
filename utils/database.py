import aiosqlite
from config import DATABASE_PATH

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER, user_id INTEGER, moderator_id INTEGER,
            reason TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            log_channel_id INTEGER,
            ticket_category_id INTEGER,
            support_role_id INTEGER
        )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS ticket_blacklist (
            guild_id INTEGER, user_id INTEGER,
            PRIMARY KEY (guild_id, user_id)
        )''')
        await db.commit()

async def get_setting(guild_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT log_channel_id,ticket_category_id,support_role_id FROM settings WHERE guild_id=?", (guild_id,))
        return await cur.fetchone()

async def save_setting(guild_id, log_channel_id=None, ticket_category_id=None, support_role_id=None):
    old = await get_setting(guild_id) or (None, None, None)
    values = tuple(new if new is not None else old[i] for i, new in enumerate(
        (log_channel_id, ticket_category_id, support_role_id)
    ))
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''INSERT INTO settings(guild_id,log_channel_id,ticket_category_id,support_role_id)
        VALUES(?,?,?,?) ON CONFLICT(guild_id) DO UPDATE SET
        log_channel_id=excluded.log_channel_id,
        ticket_category_id=excluded.ticket_category_id,
        support_role_id=excluded.support_role_id''', (guild_id, *values))
        await db.commit()

async def add_warning(guild_id,user_id,moderator_id,reason):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT INTO warnings(guild_id,user_id,moderator_id,reason) VALUES(?,?,?,?)",
                         (guild_id,user_id,moderator_id,reason))
        await db.commit()

async def get_warnings(guild_id,user_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur=await db.execute("SELECT id,reason,moderator_id,created_at FROM warnings WHERE guild_id=? AND user_id=? ORDER BY id DESC",
                             (guild_id,user_id))
        return await cur.fetchall()

async def clear_warnings(guild_id,user_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM warnings WHERE guild_id=? AND user_id=?", (guild_id,user_id))
        await db.commit()

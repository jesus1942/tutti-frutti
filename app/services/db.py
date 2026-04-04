import motor.motor_asyncio, os
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client["tutti"]
async def init_db():
    await db.users.create_index("username", unique=True)
    await db.rooms.create_index("id", unique=True)

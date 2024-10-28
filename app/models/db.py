# db.py
from motor.motor_asyncio import AsyncIOMotorClient

# Replace this with your MongoDB URI
MONGODB_URI = "mongodb://localhost:27017"

# Create a MongoDB client
client = AsyncIOMotorClient(MONGODB_URI)
db = client['secure_chrome_extension']

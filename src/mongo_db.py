from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"
MONGO_DB_NAME = "s2604_doc"

client = MongoClient(MONGO_URL)
mongo_db = client[MONGO_DB_NAME]

vulnerability_documents = mongo_db["vulnerabilities_doc"]

messages_collection = mongo_db["messages"]
summaries_collection = mongo_db["summaries"]
episodes_collection = mongo_db["episodes"]


def ping_mongo():
    return client.admin.command("ping")

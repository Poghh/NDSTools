from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv("../.env")

DB_CONFIG = {
    "host": "localhost",
    "port": 53306,
    "user": "devuser",
    "password": "devuser",
    "database": "cb_db",
    "charset": "utf8mb4",
    "autocommit": True,
}

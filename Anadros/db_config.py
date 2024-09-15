import os
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE'),
    'port': int(os.getenv('DB_PORT', 3306)),
}

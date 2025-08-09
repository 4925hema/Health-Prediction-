import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'health_monitoring')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'health_monitoring_secret_key')
    
    # Database connection string
    @property
    def DATABASE_URL(self):
        return {
            'host': self.MYSQL_HOST,
            'user': self.MYSQL_USER,
            'password': self.MYSQL_PASSWORD,
            'database': self.MYSQL_DATABASE,
            'port': self.MYSQL_PORT,
            'charset': 'utf8mb4',
            'autocommit': True
        }

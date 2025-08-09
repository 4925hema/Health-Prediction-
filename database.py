import mysql.connector
from mysql.connector import Error
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config.DATABASE_URL)
            if self.connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create necessary database tables"""
        try:
            cursor = self.connection.cursor()
            
            # Create students table
            students_table = """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                admission_date DATE NOT NULL,
                symptoms JSON NOT NULL,
                disease VARCHAR(100),
                confidence DECIMAL(5,4),
                status VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Create training_data table
            training_table = """
            CREATE TABLE IF NOT EXISTS training_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symptoms JSON NOT NULL,
                disease VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(students_table)
            cursor.execute(training_table)
            
            self.connection.commit()
            logger.info("Database tables created successfully")
            return True
            
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def insert_student(self, student_data):
        """Insert a new student record"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO students (name, phone, admission_date, symptoms, disease, confidence, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                student_data['name'],
                student_data['phone'],
                student_data['admission_date'],
                student_data['symptoms'],
                student_data['disease'],
                student_data['confidence'],
                student_data['status']
            )
            
            cursor.execute(query, values)
            student_id = cursor.lastrowid
            
            self.connection.commit()
            logger.info(f"Student record inserted with ID: {student_id}")
            return student_id
            
        except Error as e:
            logger.error(f"Error inserting student: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_all_students(self):
        """Retrieve all student records"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT * FROM students ORDER BY timestamp DESC"
            cursor.execute(query)
            
            students = cursor.fetchall()
            
            # Convert JSON symptoms back to list
            for student in students:
                if isinstance(student['symptoms'], str):
                    import json
                    student['symptoms'] = json.loads(student['symptoms'])
            
            return students
            
        except Error as e:
            logger.error(f"Error retrieving students: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def delete_student(self, student_id):
        """Delete a student record"""
        try:
            cursor = self.connection.cursor()
            
            query = "DELETE FROM students WHERE id = %s"
            cursor.execute(query, (student_id,))
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            
            logger.info(f"Student record deleted. Affected rows: {affected_rows}")
            return affected_rows > 0
            
        except Error as e:
            logger.error(f"Error deleting student: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def insert_training_data(self, symptoms, disease):
        """Insert training data for ML model"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO training_data (symptoms, disease)
            VALUES (%s, %s)
            """
            
            values = (symptoms, disease)
            cursor.execute(query, values)
            
            self.connection.commit()
            logger.info(f"Training data inserted: {symptoms} -> {disease}")
            return True
            
        except Error as e:
            logger.error(f"Error inserting training data: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def get_training_data(self):
        """Retrieve all training data"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT * FROM training_data ORDER BY created_at DESC"
            cursor.execute(query)
            
            training_data = cursor.fetchall()
            
            # Convert JSON symptoms back to list
            for item in training_data:
                if isinstance(item['symptoms'], str):
                    import json
                    item['symptoms'] = json.loads(item['symptoms'])
            
            return training_data
            
        except Error as e:
            logger.error(f"Error retrieving training data: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def clear_training_data(self):
        """Clear all training data"""
        try:
            cursor = self.connection.cursor()
            
            query = "DELETE FROM training_data"
            cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            
            logger.info(f"Training data cleared. Affected rows: {affected_rows}")
            return True
            
        except Error as e:
            logger.error(f"Error clearing training data: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Count students
            cursor.execute("SELECT COUNT(*) FROM students")
            student_count = cursor.fetchone()[0]
            
            # Count training data
            cursor.execute("SELECT COUNT(*) FROM training_data")
            training_count = cursor.fetchone()[0]
            
            return {
                'students': student_count,
                'training_data': training_count
            }
            
        except Error as e:
            logger.error(f"Error getting database stats: {e}")
            return {'students': 0, 'training_data': 0}
        finally:
            if cursor:
                cursor.close()

# Global database manager instance
db_manager = DatabaseManager()

import os, sqlite3

from config import SQL_DB_DIR
from utils.logger import setup_logger

logger = setup_logger(__name__)

STUDENT_REPOSITORY = {
        'student_email': None,
        'student_name': None,
        'student_code': None,
        'section': None,
        'department_name': None,
        'batch_code': None,
        'semester': None
    }

def get_student_repository():
    try:
        conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "aspas.db"))
        cursor = conn.cursor()

        cursor.execute("select * from student_profile;")
        users = cursor.fetchall()

        for user in users:
            user_id, user_email, user_name, user_student_code, user_section, user_department, user_batch_code, user_semester = user

            STUDENT_REPOSITORY['student_email'] = user_email
            STUDENT_REPOSITORY['student_name']= user_name
            STUDENT_REPOSITORY['student_code']= user_student_code
            STUDENT_REPOSITORY['section']= user_section
            STUDENT_REPOSITORY['department_name']= user_department
            STUDENT_REPOSITORY['batch_code']= user_batch_code
            STUDENT_REPOSITORY['semester']= user_semester
    except Exception as e:
        logger.error(str(e))

get_student_repository()
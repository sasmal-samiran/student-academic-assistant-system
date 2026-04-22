import os, sqlite3, re
from datetime import datetime, timedelta

from services import groq_api
from utils.functions import execute_sql, extract_entities

from config import SQL_DB_DIR
from ai_engine.student_repository import STUDENT_REPOSITORY
from utils.logger import setup_logger

logger = setup_logger(__name__)

current_attendace = []

def query_attendance(user_query):
    PROMPT = f"""You are an expert SQL generator for a university attendance system.

            Your task is to convert a student's natural language query into a correct SQLite SQL query.

            DATABASE SCHEMA (ATTENDANCE RELATED):

            Table: students
            (student_code PRIMARY KEY, student_name, section, semester, year)

            Table: subjects
            (subject_code PRIMARY KEY, subject_name, subject_type [core, lab, elective, skills, value added course], semester, credits)

            Table: student_subjects
            (student_code, subject_code, semester)

            Table: subject_total_classes (
                    subject_code,
                    total_classes)

            Table: attendance
            (attendance_id PRIMARY KEY, student_code, subject_code, date, period_id, status ['present','absent'])

            Table: attendance_summary
            (student_code, subject_code, classes_taken, attended_classes, attendance_percentage, last_updated DATETIME DEFAULT CURRENT_TIMESTAMP)

            Table: daily_attendance_summary
            (date, subject_code, section, total_students, present_count, absent_count)

             ==================================================
            SUBJECTS AVAILABLE
            ==================================================

            machine learning and its applications  
            data mining and data warehousing  
            big data and analytics  
            data handling and visualization  
            web technology  
            machine learning and its applications lab  
            data mining and data warehousing lab  
            big data and analytics lab  
            data handling and visualization lab  
            web technology lab  
            intelligent database system  
            data modelling and simulation  
            information extraction and retrieval  
            software project management  
            information security analysis and audit  
            operational research  
            aptitude  
            internet of things (iot) and applications  
            basic ai tools & applications 

            ==================================================
            IMPORTANT DATA RULES
            ==================================================
            - student_code, batch_code, and subject_code are stored in uppercase. all others are in lowercase.
            - always correct the spelling of faculty name by adding the prefix (dr. , mr.) and departments available in database before filtering.
            - date format: YYYY-MM-DD
            - all subjects have 45 total classes but only aptitude and basic ai tools have 30 classes

            MANDATORY JOIN FLOW (if student-specific):
            students → student_subjects → attendance

            MANDATORY CONDITIONS:
            - attendance.student_code = students.student_code
            - attendance.subject_code = student_subjects.subject_code

            IMPORTANT QUERY RULE:
            - if user asks for only attendance then fetch relevant data from attendance_summary table
            - do not return direct select * from attendance table.

            ==================================================
            FILTER RULES
            ==================================================

            - If query contains "my", "mine", "I", "me" and no specific student mentioned:
                → ALWAYS filter using the necessary user details from below:
                    user student details: {STUDENT_REPOSITORY}

            - If subject mentioned:
                → filter attendance.subject_code OR use subject_name via JOIN if needed

            - If date mentioned:
                → filter attendance.date = 'YYYY-MM-DD'

            - If "today", "yesterday":
                → use date functions accordingly

            - If asking for attendance percentage:
                → use attendance_summary table

            - If asking for low attendance:
                → use attendance_summary
                → filter attendance_percentage < 75

            - If asking for attendance history:
                → use attendance table
                → ORDER BY date

            - If asking for daily class summary (section-wise):
                → use daily_attendance_summary
                → filter by section and/or date
            
            - If user asks:
            "current class" / "next class"
                → use current time: {datetime.now().strftime("%H:%M %A")}
            if tommorow : use {(datetime.now() + timedelta(days=1)).strftime("%H:%M %A")}
            if previous : use {(datetime.now() - timedelta(days=1)).strftime("%H:%M %A")}
            if no year mentioned use 2026

            ==================================================
            QUERY TYPES HANDLING
            ==================================================

            1. Attendance status:
                → SELECT date, subject_code, status FROM attendance

            2. Attendance percentage:
                → SELECT subject_code, attendance_percentage FROM attendance_summary

            3. Low attendance:
                → WHERE attendance_percentage < 75

            4. Attendance history:
                → ORDER BY date

            5. Daily summary:
                → SELECT present_count, absent_count FROM daily_attendance_summary

            ==================================================
            OUTPUT REQUIREMENTS
            ==================================================
            - ONLY SQL query
            - No explanation
            - Use ORDER BY where relevant (date or subject)

            User Question:
            {user_query}
            """
    fetched_data = execute_sql(PROMPT)
    try:
        prompt = f"""
            Role: You are ASPAS (Automated Student Personal Assistant System).

            Task:
            Generate a clean HTML response using the attendance SQL result.

            OUTPUT FORMAT:
            - Return ONLY valid HTML inside <section>...</section>
            - At bottom add a p tag mentioning that a subject wise attendance barchart is given
            - Do NOT include SQL or explanations

            STYLE RULES:

            If data contains attendance records:
            - Show in structured format (table or list)
            - Include:
                • Date
                • Subject
                • Status (Present / Absent)

            If data contains attendance percentage:
            - Show clearly:
                • Subject
                • Attendance %
                • Highlight if below 75% (⚠️ Low Attendance)

            If data contains summary:
            - Show:
                • Total classes
                • Attended classes
                • Absent classes

            - if ask for needed classes always ceil ⌈number of needed classes⌉

            If data contains daily summary:
            - Show:
                • Date
                • Subject
                • Total students
                • Present count
                • Absent count

            Formatting:
            - Use headings (<h3>, <h4>) for sections
            - Use tables (<table>) for structured data
            - Highlight important values (like low attendance)

            If no data:
            → "No attendance records found"

            User Question:
            {user_query}

            SQL Result:
            {fetched_data}
            """
        
        conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "university.db"))
        cursor = conn.cursor()

        # --- Load students ---
        cursor.execute("SELECT student_code, student_name FROM students;")
        data = cursor.fetchall()

        students = {name: code for code, name in data}
        student_codes_list = [code for code, _ in data]

        # --- Extract entities ---
        entities = extract_entities(user_query, students.keys(), student_codes_list)

        if entities["codes"]:
            student_code = entities["codes"][0]
        elif entities["names"]:
            student_code = students[entities["names"][0]]
        else:
            student_code = student_codes_list[0]

        cursor.execute("""SELECT a.subject_code, a.attendance_percentage, s.subject_name 
               FROM attendance_summary a JOIN subjects s ON a.subject_code = s.subject_code 
               WHERE student_code = ?;""", (student_code,))
        attendance_data = cursor.fetchall()
    
        attendance_record = {'subject_code':[], 'attendance':[], 'subject_name': []}
        for subject in attendance_data:
            attendance_record['subject_code'].append(subject[0])
            attendance_record['attendance'].append(round(subject[1], 0))
            attendance_record['subject_name'].append(subject[2])

        conn.close()
        
        response = groq_api.call_groq(prompt)
        
        if response:
            start = response.find("<section>")
            end = response.find("</section>")
            
            return (response[start: end+10], attendance_record)
        else:
            return ("It's taking too longer. May be a slow network connection.", attendance_record)


    except Exception as e:
        logger.error(str(e))
        return ("Try again", attendance_record)
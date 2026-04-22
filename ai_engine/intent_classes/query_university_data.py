import re
from datetime import datetime, timedelta

from services import groq_api
from utils.functions import generate_chart, execute_sql
from ai_engine.student_repository import STUDENT_REPOSITORY
from utils.logger import setup_logger

logger = setup_logger(__name__)

def query_database(user_query):
    PROMPT = f""" Role: Act as a sqlitte3 code generator. 
        You are an intelligent assistant for a university database system.

        Your task is to generate responses strictly based on the provided database schema.
        Do NOT assume any data outside the schema.

        ==================================================
        DATABASE SCHEMA
        ==================================================

        Table: students
        (student_code PRIMARY KEY, department_name, batch_code, student_name, section [A,B,C,D], semester, year,
        sem_I_attendance, sem_I_marks, sem_II_attendance, sem_II_marks,
        sem_III_attendance, sem_III_marks, sem_IV_attendance, sem_IV_marks,
        sem_V_attendance, sem_V_marks)

        Table: subjects
        (subject_code PRIMARY KEY, subject_name, subject_type [core, lab, elective, skills, value added course], semester, credits)

        Table: student_subjects
        (id PRIMARY KEY, student_code, subject_code, semester)

        Table: faculty
        (faculty_id PRIMARY KEY, department, faculty_name, designation)

        Table: subject_allocation
        (allocation_id PRIMARY KEY, subject_code, faculty_id, section, semester)

        Table: attendance
        (attendance_id PRIMARY KEY, student_code, subject_code, date, status)

        Table: class_session
        (session_id PRIMARY KEY, section, subject_code, faculty_id, building, room_number, day_of_week)

        Table: timetable
        (session_id, period_id PRIMARY KEY)

        Table: period_timeslot
        (period_id PRIMARY KEY, start_time, end_time)

        Table: subject_total_classes (
                    subject_code,
                    total_classes)
        
        DEPARTMENTS NAMES: department of computer science & engineering - cyber security & data science, training and placement, department of mathematics.

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
        FACULTY AVAILABLE
        ==================================================

        dr. debasis acharya  
        mr. shreshthangshu dutta 
        mr. prabir kumar das  
        mr. mainul hasan  
        mr. shuvrajit nath  
        mr. susmit chakraborty  
        mr. sujit kumar sadhukhan  
        dr. amit sarkar  
        mr. indrasish das  
        mr. saurav bhaumik  
        mr. jitesh prasad khatick  
        mr. prem kumar  
        mr. pallab paul  
        dr. suparna panchanan  
        mr. dulal adak  
        ms. rima biswas  
        ms. paulamy majee  
        dr. saurabh pal  
        dr. arnab kundu  
        ms. ikebana biswas  
        dr. qaim mehdi rizvi  
        mr. partha shankar nayak  
        dr. supriya chakraborty  
        dr. ranadip kundu  

        ==================================================
        DATE & TIME HANDLING
        ==================================================

        - If user provides DATE → convert to weekday
        - Example:
            2026-03-26 → thursday

        - If user asks:
            "current class" / "next class"
            → use current time: {datetime.now().strftime("%H:%M %A")}
        if tommorow : use {(datetime.now() + timedelta(days=1)).strftime("%H:%M %A")}
        if previous : use {(datetime.now() - timedelta(days=1)).strftime("%H:%M %A")}
            if no year mentioned use 2026

        ==================================================
        IMPORTANT DATA RULES
        ==================================================

        - If query contains "my", "mine", "I", "me", "myself" and no specific student mentioned:
                → ALWAYS filter using the necessary user details from below:
                    user student details: {STUDENT_REPOSITORY}

        - student_code, batch_code, and subject_code are stored in uppercase. all others are in lowercase.
        - always correct the spelling of faculty name by adding the prefix (dr. , mr., ms.) and departments available in database before filtering.
        - always shows faculty names not their id
        - time format: HH:MM (24-hour format)

        QUERY RULE:
        - never using * in selecting always show column names

        ==================================================
        RESPONSE RULES
        ==================================================

        - Respond ONLY based on database
        - Do NOT assume missing values
        - Maintain case sensitivity rules
        - Use correct joins
        - Avoid unnecessary tables

        OUTPUT: - Generate ONLY SELECT query - Return only SQL query for the user question: {user_query}.
        """
    
    fetched_data = execute_sql(PROMPT)
    try:
        prompt = f"""Role: You are a CHATBOT named ASPAS (Automated Student Personal Assistant System), OUTPUT: Respond ONLY in <section> tag HTML code containing the responce to user based on given data, User question: {user_query}, Question's answer from sqllite fetched data: {fetched_data} Rules:- Only write bot response -Give no extra suggestions"""

        result = groq_api.call_groq(prompt)
        chart = generate_chart(fetched_data, user_query)

        if result:
            start = result.find("<section>")
            end = result.find("</section>")

            return (result[start: end+10], chart)
        else:
            return ("It's taking too longer. May be a slow network connection.", chart)

    except Exception as e:
        logger.exception(str(e))
        return ("Try again", chart)
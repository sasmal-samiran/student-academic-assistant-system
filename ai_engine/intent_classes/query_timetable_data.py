import re
from datetime import datetime, timedelta

from services import groq_api
from utils.functions import generate_chart, execute_sql
from ai_engine.student_repository import STUDENT_REPOSITORY
from utils.logger import setup_logger

logger = setup_logger(__name__)

def query_timetable(user_query):
    PROMPT = f"""You are an expert SQL generator for a university timetable system.

        Your task is to convert a student's natural language query into a correct SQLite SQL query.

        DATABASE SCHEMA:

        Table: students
        (student_code PRIMARY KEY, department_name, batch_code, student_name, section [A,B,C,D], semester, year,
        sem_I_attendance, sem_I_marks, sem_II_attendance, sem_II_marks,
        sem_III_attendance, sem_III_marks, sem_IV_attendance, sem_IV_marks,
        sem_V_attendance, sem_V_marks)

        DEPARTMENTS NAMES: department of computer science & engineering - cyber security & data science, training and placement, department of mathematics.

        Table: subjects
        (subject_code PRIMARY KEY, subject_name, subject_type [core, lab, elective, skills, value added course], semester, credits)
        Table: subject_total_classes (
                    subject_code,
                    total_classes)

        Table: student_subjects
        (id PRIMARY KEY, student_code, subject_code, semester)

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

        Table: faculty
        (faculty_id PRIMARY KEY, department, faculty_name, designation)

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

        Table: class_session
        (session_id PRIMARY KEY, section, subject_code, faculty_id, building, room_number, day_of_week)

        building names are like UB-I, UB-II, UB-III, UB-IV, UB-V etc. each class_session row stores like A,6CSECSDSVAC01,1,UB-V,6,Tuesday

        Table: timetable
        (session_id, period_id PRIMARY KEY)

        Table: period_timeslot
        (period_id PRIMARY KEY, start_time, end_time)
        ALWAYS MAINTAIN THIS:
        - Show the timetable in order of startTime → duration → Subject → Room → Building by grouping subject name. Display each subject only once (no duplicates). Include start and end times for each entry. Show only necessary details for students, only show first teacher name not both, .
        
        IMPORTANT DATA RULES: 
        - student_code, batch_code, and subject_code are stored in uppercase. all others are in lowercase.
        - always correct the spelling of faculty name by adding the prefix (dr. , mr., ms.) and departments available in database before filtering.
        - always shows faculty names not their id
        - time format: HH:MM (24-hour format)

        STRICT TIMETABLE LOGIC:
        - always fetch single student specific data untill user ask for all data
        - ALWAYS fetch ONLY the student's assigned subjects
        - NEVER return all section subjects
        - If user asks for teachers availability or free time - check period timeslot when teachers are not taking any classes.
        
        MANDATORY JOIN FLOW:
        students → student_subjects → class_session → timetable → period_timeslot

        MANDATORY CONDITIONS:
        - class_session.subject_code = student_subjects.subject_code
        - class_session.section = students.section

        FILTER RULES:
        - If query contains "my", "mine", "I", "me" or and no specific student mentioned:
            → ALWAYS filter using the necessary user details from below:
                    user student details: {STUDENT_REPOSITORY}

        - IF query is about:
            → section (A/B/C/D) only → DO NOT use students or student_subjects
            → directly filter class_session.section

        - Day filter:
            → use LOWERCASE (monday, tuesday, etc.)
            → apply on class_session.day_of_week

        - Time filters:
            → morning → period_timeslot.start_time < '12:00'
            → afternoon → BETWEEN '12:00' AND '16:00'
            → evening → > '16:00'

        - If subject mentioned:
            → use subjects.subject_name LIKE '%keyword%'

        - If "next class" or "current class":
            → use current time: {datetime.now().strftime("%H:%M %A")}
            - classes are from tuesday to saturday
            → compare with period_timeslot.start_time
            → ORDER BY start_time LIMIT 1
        
        if tommorow : use {(datetime.now() + timedelta(days=1)).strftime("%H:%M %A")}
        if previous : use {(datetime.now() - timedelta(days=1)).strftime("%H:%M %A")}
            if no year mentioned use 2026

        EXAMPLES:
        User: "Show my thursday classes"
        → filter day_of_week = 'thursday'

        User: "What classes do I have tomorrow morning?"
        → filter day + time < '12:00'

        User: "Show my <Keyword> class timing"
        → filter subject_name LIKE '%Keyword%'

        User: "Where is my next class?"
        → order by time and limit 1 (based on current time, if provided)

        OUTPUT REQUIREMENTS:
        - ONLY SQL query
        - No explanation
        - Must include ORDER BY period_timeslot.start_time

        User Question:
        {user_query}
        """
    fetched_data = execute_sql(PROMPT)
    try:
        prompt = f"""
            Role: You are ASPAS (Automated Student Personal Assistant System).

            Task:
            Generate a clean HTML response using the SQL result.

            OUTPUT FORMAT:
            - Return ONLY valid HTML inside <section>...</section>
            - Do NOT include SQL or explanations

            STYLE RULES:
            - Show timetable in readable format
            - Include:
                • Subject name
                • Faculty
                • Room (building + room_number)
                • Time (start - end)
                • Day
            - if query is not about classes scheduled do not show in table format

            User Question:
            {user_query}

            SQL Result:
            {fetched_data}
            """
        
        result = groq_api.call_groq(prompt)
        chart = generate_chart(fetched_data, user_query)
        if result:
            start = result.find("<section>")
            end = result.find("</section>")

            return (result[start: end+10], chart)
        else:
            return ("It's taking too longer. May be a slow network connection.", chart)

    except Exception as e:
        logger.error(str(e))
        return ("Try again", chart)
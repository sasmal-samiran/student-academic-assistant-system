from services import groq_api

INTENTS = ["attendance",
           "timetable",
           "query_university_data",
           "prediction",
           "semantic_search",
           "greeting",
           "help",
           "other"]


def classify(user_query):
    prompt = f"""You are an intent classifier for a university assistant system who solve all academic related issues.

        =====================
        INTENTS
        =====================

        1. attendance →
        Use this intent for ANY query related to student attendance data, including:
        - Attendance status (present/absent)
        - Attendance percentage (overall or subject-wise)
        - Attendance history (daily, date-wise, subject-wise)
        - Low attendance / shortage (<75%)
        - Total classes attended / missed
        - Subject-wise attendance performance
        - Daily attendance summary (present/absent count per class/section)
        - Trends or comparisons in attendance
        - Queries like:
            "my attendance"
            "attendance in DBMS"
            "was I present yesterday"
            "attendance percentage"
            "which subjects have low attendance"
            "attendance on specific date"
            "attendance summary"
            "how many classes did I attend"

        IMPORTANT:
        If the query involves ANY form of attendance data (present/absent, percentage, records, summary), ALWAYS choose "attendance".

        --------------------------------------------------


        2. timetable →
        Use this intent for ANY query related to a student's classes, including:
        - Class schedule (today, tomorrow, specific day like Monday, Thursday, etc.)
        - Subject-wise class timing (e.g., "When is my DBMS class?")
        - Period timing, start/end time
        - Faculty handling a class
        - if user asks for faculty, teacher,s availability or free time to meet them when they are not taking any classes
        - Classroom / building / room number
        - Next / current / upcoming class
        - Filters like:
            • day (Monday–Saturday)
            • time (morning, afternoon, evening)
            • subject name
            • semester / year
            • section
        - Any question that asks:
            "what class", "when class", "where class", "which class", "next class"

        IMPORTANT:
        If the query is about **ANY class-related information**, ALWAYS choose "timetable".
        If the query is about attendance (present/ absent), do not choose "timetable".

        --------------------------------------------------

        3. query_university_data →
        Use this ONLY for non-timetable database queries such as:
        - Student details (name, department, semester, marks, attendance)
        - Subject details (credits, type, semester)
        - Faculty details (designation, department)
        - Subject allocation (which faculty teaches which subject)

        IMPORTANT:
        If the query involves class timing/schedule → DO NOT use this intent.

        --------------------------------------------------

        4. prediction →
        - Any analysis, forecasting, any type of trend, behaviour, or ML-related query related to only attendace.
        - Example: attendance prediction, attendance trend, attendance behavior

        IMPORTANT:
        - if query related to prediction but not about attendance then choose others

        --------------------------------------------------

        5. semantic_search →
        Use this intent when the query is related to academic or student-support information that is NOT stored in structured database tables.

        This includes:
        - Assignment & Deadline tracking (pending tasks, submission reminders)
        - Event management (academic events, extracurricular activities, schedules, reminders)
        - General academic guidance (study tips, planning, productivity)
        - Any unstructured academic information not present in DB schema

        Examples:
        - "When my exam will start"
        - "What assignments are pending?"
        - "Remind me of upcoming deadlines"
        - "Any events this week?"

        IMPORTANT:
        - If the query CANNOT be answered using structured tables (students, subjects, faculty, attendance, timetable) → choose "semantic_search"
        - If the query requires explanation, reminders, planning, or general academic info → choose "semantic_search"
        - If the query is about the followings, strictly always choose 'semantic_search' intent
            1. Theory and Practical Examination schedules
            2. Elective subjects for 7 semester data
        - If user asks anything deeply about this chatbot system without help and casuall greetings

        --------------------------------------------------

        6. greeting →
        - hi, hello, hey, good morning, etc.
        - if user asks casually to chatbot witout any help.

        --------------------------------------------------

        7. help →
        - user asking how to use system or what they can ask
        - about chatbot(aspas) what it can do and how to use it

        --------------------------------------------------

        8. other →
        - anything unrelated to the system

        Intents are ordered with higher to lower priority

        =====================
        STRICT RULES
        =====================
        - if query related to any type of analysis, finding trends, behavior, or prediction always choose prediction over any other intents
        - "timetable" has HIGH PRIORITY over "query_university_data"
        - If there is ANY confusion → choose "timetable" for class-related queries
        - Output ONLY the intent name (no explanation, no extra text)

        =====================
        USER QUERY
        =====================

        {user_query}
        """

    response = groq_api.call_groq(prompt)
    
    fetched_intent = next((i for i in INTENTS if i in response.lower()), "other")

    return fetched_intent
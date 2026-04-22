import os, sqlite3

from config import SQL_DB_DIR

conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "university.db"))
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_code TEXT PRIMARY KEY,
    department_name TEXT NOT NULL,
    batch_code TEXT NOT NULL,
    student_name TEXT NOT NULL,
    section TEXT,
    semester INTEGER,
    year INTEGER,
    sem_I_attendance REAL,
    sem_I_marks REAL,
    sem_II_attendance REAL,
    sem_II_marks REAL,
    sem_III_attendance REAL,
    sem_III_marks REAL,
    sem_IV_attendance REAL,
    sem_IV_marks REAL,
    sem_V_attendance REAL,
    sem_V_marks REAL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    subject_code TEXT PRIMARY KEY,
    subject_name TEXT NOT NULL,
    subject_type TEXT,
    semester INTEGER,
    credits INTEGER
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT,
    subject_code TEXT,
    semester INTEGER,
    FOREIGN KEY (student_code) REFERENCES students(student_code),
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code),
    UNIQUE(student_code, subject_code)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department TEXT,
    faculty_name TEXT NOT NULL,
    designation TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subject_allocation (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT,
    faculty_id INTEGER,
    section TEXT,
    semester INTEGER,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS period_timeslot (
    period_id INTEGER PRIMARY KEY,
    start_time TEXT,
    end_time TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS class_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT,
    subject_code TEXT,
    faculty_id INTEGER,
    building TEXT,
    room_number TEXT,
    day_of_week TEXT
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS timetable (
    session_id INTEGER,
    period_id INTEGER,
    PRIMARY KEY (session_id, period_id),
    FOREIGN KEY (session_id) REFERENCES class_session(session_id),
    FOREIGN KEY (period_id) REFERENCES period_timeslot(period_id)
);
""")

cursor.execute("""CREATE TABLE subject_total_classes (
    subject_code TEXT PRIMARY KEY,
    total_classes INTEGER
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT NOT NULL,
    subject_code TEXT NOT NULL,
    date TEXT NOT NULL,
    period_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('present','absent')),

    FOREIGN KEY (student_code) REFERENCES students(student_code),
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code),
    FOREIGN KEY (period_id) REFERENCES period_timeslot(period_id),

    UNIQUE(student_code, subject_code, date, period_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_summary (
    student_code TEXT,
    subject_code TEXT,
    total_classes INTEGER,
    classes_taken INTEGER,
    attended_classes INTEGER,
    attendance_percentage REAL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_code, subject_code),
    FOREIGN KEY (student_code) REFERENCES students(student_code),
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_attendance_summary (
    date TEXT,
    subject_code TEXT,
    section TEXT,
    total_students INTEGER,
    present_count INTEGER,
    absent_count INTEGER,
    PRIMARY KEY (date, subject_code, section),
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code)
);
""")

#### prediction related tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_profiles (
               student_code TEXT PRIMARY KEY,
               profile TEXT)
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS subject_difficulty (
               subject_code TEXT PRIMARY KEY,
               difficulty_level TEXT)
               """)

conn.commit()
conn.close()
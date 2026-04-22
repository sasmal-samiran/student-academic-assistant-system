import os, sqlite3

from config import SQL_DB_DIR
from database.tables import student_details, student_subjects, time_table, attendance

conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "university.db"))
cursor = conn.cursor()

student_details.student_details(cursor)
student_subjects.student_subjects(cursor)
time_table.time_table(cursor)

# must run at last
attendance.attendance(cursor)

conn.commit()
conn.close()

print("Data inserted successfully into subjects and student_subjects tables.")
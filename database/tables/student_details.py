## Inserting data into------
# students table

import pandas as pd

def student_details(cursor):
    df = pd.read_csv("datasets/student_details.csv")
    for i in range(df.shape[0]):
        student_code = str((df.loc[i, 'student_code']))
        department_name = str((df.loc[i, 'department_name'])).lower()
        batch_code = str(df.loc[i, 'batch_code'])
        student_name = str(df.loc[i, 'student_name']).lower()
        section = str(df.loc[i, 'section'])
        semester = int(df.loc[i, 'semester'])
        year = int(df.loc[i, 'year'])
        sem_I_attendance = float(df.loc[i, 'sem_I_attendance'])
        sem_I_marks = float(df.loc[i, 'sem_I_marks'])
        sem_II_attendance = float(df.loc[i, 'sem_II_attendance'])
        sem_II_marks = float(df.loc[i, 'sem_II_marks'])
        sem_III_attendance = float(df.loc[i, 'sem_III_attendance'])
        sem_III_marks = float(df.loc[i, 'sem_III_marks'])
        sem_IV_attendance = float(df.loc[i, 'sem_IV_attendance'])
        sem_IV_marks = float(df.loc[i, 'sem_IV_marks'])
        sem_V_attendance = float(df.loc[i, 'sem_V_attendance'])
        sem_V_marks = float(df.loc[i, 'sem_V_marks'])
        cursor.execute("""INSERT INTO students VALUES (?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?,?,?, ?);
                       """, (student_code, department_name, batch_code, student_name, section, semester, year, sem_I_attendance,
                        sem_I_marks, sem_II_attendance, sem_II_marks, sem_III_attendance, sem_III_marks, 
                        sem_IV_attendance, sem_IV_marks, sem_V_attendance, sem_V_marks))
import os, sqlite3

from config import SQL_DB_DIR

## THIS STUDENT ETAILS WILL BE STORED BASED ON STUDENT LOGIN

def insert_student():
    try:
        conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "aspas.db"))
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO student_profile (
            email,
            student_name,
            student_code,
            section,
            department,
            batch_code,
            semester
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "bwubtd23161@brainwareuniversity.ac.in",
            "samiran sasmal",
            "BWU/BTD/23/161",
            "C",
            "Department of Computer Science & Engineering - Cyber Security & Data Science".lower(),
            "BTECH CSE DS-2023-SEC-A".lower(),
            6
        ))

        conn.commit()
        conn.close()
        print("Inserted succesfully")
    except Exception as e:
        print(f"Error in inserting to aspas.db [{e}]")

insert_student()
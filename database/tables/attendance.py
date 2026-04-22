import random
from datetime import datetime, timedelta
import pandas as pd

def attendance(cursor):

    # ✅ Students with section (IMPORTANT FIX)
    cursor.execute("SELECT student_code, section FROM students;")
    students_data = cursor.fetchall()
    student_section = {s: sec for s, sec in students_data}
    students = list(student_section.keys())

    # Student-Subject mapping
    cursor.execute("SELECT student_code, subject_code FROM student_subjects;")
    student_subjects = {}
    for s, sub in cursor.fetchall():
        student_subjects.setdefault(s, []).append(sub)

    # ✅ DISTINCT sessions (avoid duplicate timetable rows)
    cursor.execute("""
        SELECT DISTINCT
            cs.session_id,
            cs.subject_code,
            cs.section,
            cs.day_of_week,
            cs.faculty_id,
            t.period_id
        FROM class_session cs
        JOIN timetable t ON cs.session_id = t.session_id
    """)
    sessions = cursor.fetchall()

    # 🎓 Student profiles
    def assign_student_profile():
        profiles = {
            "good": (0.85, 0.95),
            "average": (0.65, 0.8),
            "poor": (0.4, 0.6)
        }
        p = random.choices(
            ["good", "average", "poor"],
            weights=[0.2, 0.5, 0.3]
        )[0]
        return p, random.uniform(*profiles[p])

    student_profiles = {s: assign_student_profile() for s in students}

    # Subject nature
    subject_difficulty = {
        '6BWUVAC01': 'exciting', '6CSECSDSVAC01': 'boring',
        'APT-601': 'normal', 'OEC-CSD601A': 'normal',
        'OEC-CSD601B': 'normal', 'OEC-CSD601C': 'exciting',
        'PCC-CSD601': 'normal', 'PCC-CSD602': 'normal',
        'PCC-CSD691': 'exciting', 'PCC-CSD692': 'exciting',
        'PEC-CSD601A': 'normal', 'PEC-CSD601B': 'normal',
        'PEC-CSD601C': 'normal', 'PEC-CSD602A': 'normal',
        'PEC-CSD602B': 'normal', 'PEC-CSD602C': 'normal',
        'PEC-CSD691A': 'exciting', 'PEC-CSD691B': 'exciting',
        'PEC-CSD691C': 'exciting'
    }

    for student in students:
        profile, base_prob = student_profiles[student]

        cursor.execute("""
            INSERT INTO student_profiles (student_code, profile) VALUES (?, ?)
        """, (student, profile))

    def generate_days(start, end):
        days = []
        current = start
        while current <= end:
            if current.weekday() in [1,2,3,4,5]:  # Tue-Sat
                days.append(current)
            current += timedelta(days=1)
        return days

    def generate_attendance(start_date, end_date):
        records = []
        seen = set()  # ✅ prevent duplicates

        days = generate_days(start_date, end_date)

        for day in days:
            day_name = day.strftime("%A").lower()
            from collections import defaultdict

            sessions_by_day = defaultdict(list)

            for row in sessions:
                session_id, subject_code, section, session_day, faculty_id, period_id = row
                sessions_by_day[session_day.lower()].append(row)

            for session_id, subject_code, section, session_day, faculty_id, period_id in sessions_by_day[day_name]:

                for student in students:

                    if student_section[student] != section:
                        continue

                    if subject_code not in student_subjects.get(student, []):
                        continue

                    key = (student, subject_code, day.strftime("%Y-%m-%d"), period_id)
                    if key in seen:
                        continue
                    seen.add(key)

                    profile, base_prob = student_profiles[student]
                    prob = base_prob

                    # Subject effect
                    nature = subject_difficulty.get(subject_code, "normal")
                    if nature == "boring":
                        prob -= 0.1
                    elif nature == "exciting":
                        prob += 0.05

                    # Mid-week fatigue
                    if day.weekday() in [2, 3, 5]:
                        prob -= 0.05

                    # Random noise
                    prob += random.uniform(-0.05, 0.05)
                    prob = max(0.2, min(0.98, prob))

                    status = "present" if random.random() < prob else "absent"

                    records.append((
                        student,
                        subject_code,
                        day.strftime("%Y-%m-%d"),
                        period_id,
                        status
                    ))

        return records

    # Generate data
    start = datetime(2026, 1, 10)
    end = datetime(2026, 3, 10)

    records = generate_attendance(start, end)

    df = pd.DataFrame(records, columns= ["student_code", "subject_code", "date", "period_id", "status"])
    df.to_csv("datasets/attendance.csv", index= False)

    # Insert safely
    cursor.executemany("""
        INSERT INTO attendance 
        (student_code, subject_code, date, period_id, status)
        VALUES (?, ?, ?, ?, ?)
    """, records)
    cursor.execute("""INSERT INTO subject_total_classes (subject_code, total_classes) VALUES

-- Core Subjects
('PCC-CSD601', 45),
('PCC-CSD602', 45),
('PCC-CSD691', 45),
('PCC-CSD692', 45),

-- Elective-II
('PEC-CSD601A', 45),
('PEC-CSD601B', 45),
('PEC-CSD601C', 45),
('PEC-CSD691A', 45),
('PEC-CSD691B', 45),
('PEC-CSD691C', 45),

-- Elective-III
('PEC-CSD602A', 45),
('PEC-CSD602B', 45),
('PEC-CSD602C', 45),

-- Open Elective-I
('OEC-CSD601A', 45),
('OEC-CSD601B', 45),
('OEC-CSD601C', 45),

-- Extra
('APT-601', 30),
('6CSECSDSVAC01', 45),
('6BWUVAC01', 30);""")

    cursor.execute("""
        INSERT INTO attendance_summary 
            (student_code, subject_code, total_classes, classes_taken, attended_classes, attendance_percentage)

            SELECT 
                a.student_code,
                a.subject_code,
                stc.total_classes,
                COUNT(*) AS classes_taken,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS attended_classes,
                (SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS attendance_percentage

            FROM attendance a

            JOIN subject_total_classes stc 
            ON a.subject_code = stc.subject_code

            GROUP BY a.student_code, a.subject_code;
        """)
    
    # Insert into daily_attendance_summary
    cursor.execute("""
        INSERT INTO daily_attendance_summary 
(date, subject_code, section, total_students, present_count, absent_count)

SELECT 
    date,
    subject_code,
    section,
    COUNT(*) AS total_students,
    SUM(CASE WHEN final_status = 'present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN final_status = 'absent' THEN 1 ELSE 0 END) AS absent_count

FROM (
    SELECT 
        a.student_code,
        a.date,
        a.subject_code,
        s.section,

        CASE 
            WHEN SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) > 0 
            THEN 'present'
            ELSE 'absent'
        END AS final_status

    FROM attendance a
    JOIN students s ON a.student_code = s.student_code

    GROUP BY a.student_code, a.date, a.subject_code, s.section
) sub

GROUP BY date, subject_code, section;
    """)
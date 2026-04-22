## inserting data in-------
# subjects table
# student_subjects

import re
import pandas as pd
from PyPDF2 import PdfReader

def student_subjects(cursor):
    subject_map = {
        "machine learning and its applications": ("PCC-CSD601", "core", 6, 3),
        "data mining and data warehousing": ("PCC-CSD602", "core", 6, 3),
        "machine learning and its applications lab": ("PCC-CSD691", "lab", 6, 1.5),
        "data mining and data warehousing lab": ("PCC-CSD692", "lab", 6, 1.5),

        # Elective-II (Sem 6)
        "big data and analytics": ("PEC-CSD601A", "elective", 6, 3),
        "data handling and visualization": ("PEC-CSD601B", "elective", 6, 3),
        "web technology": ("PEC-CSD601C", "elective", 6, 3),
        "big data and analytics lab": ("PEC-CSD691A", "lab", 6, 1.5),
        "data handling and visualization lab": ("PEC-CSD691B", "lab", 6, 1.5),
        "web technology lab": ("PEC-CSD691C", "lab", 6, 1.5),

        # Elective-III (Sem 6)
        "intelligent database system": ("PEC-CSD602A", "elective", 6, 3),
        "data modelling and simulation": ("PEC-CSD602B", "elective", 6, 3),
        "information extraction and retrieval": ("PEC-CSD602C", "elective", 6, 3),

        # Open Elective-I (Sem 6)
        "software project management": ("OEC-CSD601A", "elective", 6, 3),
        "information security analysis and audit": ("OEC-CSD601B", "elective", 6, 3),
        "operational research": ("OEC-CSD601C", "elective", 6, 3),

        # Extra Added
        "aptitude": ("APT-601", "skills", 6, 0),
        "internet of things (iot) and applications": ("6CSECSDSVAC01", "value added course", 6, 0),
        "basic ai tools & applications": ("6BWUVAC01", "Value Added Course", 6, 0)
    }

    for name, (code, subject_type, sem, credits) in subject_map.items():
        cursor.execute("""
            INSERT INTO subjects (subject_code, subject_name, subject_type, semester, credits)
            VALUES (?, ?, ?, ?, ?)
        """, (code, name, subject_type, sem, credits))


    file_path = "datasets/Elective Paper allocation_SEM VI-2025-2026.pdf"
    reader = PdfReader(file_path)

    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    pattern = re.compile(
        r"SEC ([A-D]) VI\s+(BWU/BTD/23/\d+)\s+([A-Za-z\s\.]+?)\s+([ABC]\.\s.*?)(?=SEC|$)",
        re.DOTALL
    )

    for match in pattern.finditer(full_text):

        student_code = match.group(2)
        electives_block = match.group(4)

        # Extract subject names
        electives_block = re.sub(r"\s*BCSE DS 2023\s*$", "", electives_block)
        chosen_subjects = re.findall(
            r"[ABC]\.\s(.*?)(?=\s+[ABC]\.|$)", 
            electives_block, 
            re.DOTALL
        )

        for subject_name in chosen_subjects:
            subject_name = subject_name.strip().lower()

            if subject_name in subject_map:
                subject_code, _, semester, _ = subject_map[subject_name]

                cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, subject_code, int(semester)))
                if subject_name == "big data and analytics" or subject_name=="data handling and visualization" or subject_name=="web technology":
                    cursor.execute("""
                        INSERT INTO student_subjects (student_code, subject_code, semester)
                        VALUES (?, ?, ?)
                    """, (student_code, subject_code.replace("0", '9'), int(semester)))

    core_subjects = pd.read_csv("datasets/student_details.csv")
    for student_code in core_subjects["student_code"]:
        cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, "PCC-CSD601", 6))
        cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, "PCC-CSD602", 6))
        cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, "PCC-CSD691", 6))
        cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, "PCC-CSD692", 6))
        cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, "APT-601", 6))
        cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, "6BWUVAC01", 6))
        
    iot = pd.read_csv("datasets/iot_students.csv")
    for student_code in iot["student_code"]:
        cursor.execute("""
                    INSERT INTO student_subjects (student_code, subject_code, semester)
                    VALUES (?, ?, ?)
                """, (student_code, "6CSECSDSVAC01", 6))

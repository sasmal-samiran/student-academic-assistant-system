import sqlite3, re
import pandas as pd
from services import groq_api
import os, logging, joblib

from config import ML_MODEL_DIR, SQL_DB_DIR
from utils.functions import extract_entities
from ai_engine.student_repository import STUDENT_REPOSITORY
from utils.logger import setup_logger

logger = setup_logger(__name__)

model = joblib.load(os.path.join(ML_MODEL_DIR, "attendance_model.pkl"))

def _predict(user_query, model=model):
    try:
        conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "university.db"))
        cursor = conn.cursor()

        # --- Load students ---
        cursor.execute("SELECT student_code, student_name FROM students;")
        data = cursor.fetchall()

        students = {name: code for code, name in data}
        student_codes_list = [code for code, _ in data]

        # --- Load profiles ---
        cursor.execute("SELECT student_code, profile FROM student_profiles;")
        profiles = cursor.fetchall()
        student_profiles = {code: profile for code, profile in profiles}

        # --- Extract entities ---
        entities = extract_entities(user_query, students.keys(), student_codes_list)

        if entities["codes"]:
            student_code = entities["codes"][0]
        elif entities["names"]:
            student_code = students[entities["names"][0]]
        else:
            student_code = STUDENT_REPOSITORY['student_code']

        # --- Get subjects ---
        cursor.execute("""
            SELECT s.subject_code
            FROM subjects s
            JOIN student_subjects ss
            ON s.subject_code = ss.subject_code
            WHERE ss.student_code = ?
        """, (student_code,))
        subject_codes = [row[0] for row in cursor.fetchall()]

        # --- Difficulty mapping ---
        subject_difficulty = {
            '6BWUVAC01': 'exciting', '6CSECSDSVAC01': 'boring',
            'APT-601': 'normal', 'OEC-CSD601A': 'normal',
            'OEC-CSD601B': 'normal', 'OEC-CSD601C': 'exciting',
            'PCC-CSD601': 'normal', 'PCC-CSD602': 'normal',
            'PCC-CSD691': 'exciting', 'PCC-CSD692': 'exciting',
            'PEC-CSD601A': 'normal', 'PEC-CSD601B': 'normal',
            'PEC-CSD691A': 'exciting', 'PEC-CSD691B': 'exciting',
            'PEC-CSD691C': 'exciting'
        }

        # --- Profile ---
        profile = student_profiles.get(student_code, "average")

        # --- Attendance data ---
        cursor.execute("""
            SELECT subject_code, classes_taken, attended_classes,
                total_classes - classes_taken AS remaining_classes, attendance_percentage
            FROM attendance_summary
            WHERE student_code = ?
        """, (student_code,))
        
        attendance_summary = cursor.fetchall()
        
        df = pd.DataFrame(attendance_summary, columns=[
            "subject_code", "classes_completed", "classes_attended",
            "remaining_classes", "current_attendance_percent"
        ])

        # --- Filter only student subjects ---
        df = df[df["subject_code"].isin(subject_codes)]

        # --- Add difficulty feature ---
        df["subject_difficulty"] = df["subject_code"].map(subject_difficulty).fillna("normal")
        df["profile"] = profile

        # One-hot encoding
        df = pd.get_dummies(df, columns=["subject_difficulty", "profile"], drop_first=True)

        # --- Final features for model ---
        required_cols = [
            "classes_completed",
            "classes_attended",
            "remaining_classes",
            "current_attendance_percent",
            "subject_difficulty_boring",
            "subject_difficulty_exciting",
            "subject_difficulty_normal",
            "profile_average",
            "profile_good",
            "profile_poor"
        ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0

        X = df[required_cols]

        # --- Prediction ---
        predictions = model.predict(X)

        df["prediction"] = predictions
        df["total_classes"] = df["subject_code"].isin(["APT-601", "6BWUVAC01"]).map({True: 30, False: 45})
        df["predicted_attendance_percent"] = round((df["prediction"] / df["total_classes"]) * 100, 2)
        df["current_attendance_percent"] = df["current_attendance_percent"].round(2)

        current_overall_attendance = sum(df['current_attendance_percent'] * df['classes_completed']) / sum(df['classes_completed'])
        predicted_overall_attendance = sum(df['predicted_attendance_percent'] * df['total_classes']) / sum(df['total_classes'])

        result = df[["subject_code", "current_attendance_percent", "predicted_attendance_percent"]].to_dict(orient="records")
        
        cursor.execute("""SELECT a.subject_code, a.attendance_percentage, s.subject_name 
                FROM attendance_summary a JOIN subjects s ON a.subject_code = s.subject_code 
                WHERE student_code = ?;""", (student_code,))
        attendance_data = cursor.fetchall()
        
        predicted_attendance_record = {'subject_code':[], 
                                    'attendance':[], 
                                    'subject_name': [],
                                    'predicted_attendance': []}
        for subject in attendance_data:
            predicted_attendance_record['subject_code'].append(subject[0])
            predicted_attendance_record['attendance'].append(round(subject[1], 0))
            predicted_attendance_record['subject_name'].append(subject[2])
        predicted_attendance_record['predicted_attendance'] = df['predicted_attendance_percent'].round(0).tolist()

        conn.close()
        return ({
            "current_overall_attendance": round(current_overall_attendance, 2),
            "predicted_overall_attendance": round(predicted_overall_attendance, 2),
            "predictions": result
        }, predicted_attendance_record)
    except Exception as e:
        logger.error(str(e))

def predict(user_query):
    fetched_data, predicted_attendance_record = _predict(user_query)

    prompt = f"""
        Role: You are an attendance predictor assistant.

        Task:
        You are given current_overall_attendance, predicted_overall_attendance, and a dataset containing subject_code, current_attendance_percent, predicted_attendance_percent
        {fetched_data} 

        Instructions:
        - Return ONLY valid HTML inside <section>...</section>
        - Use simple tags: <h2>, <table>, <tr>, <th>, <td>, <p>
        - use symbols in bottom section with separate p tags for each sentences with relaevant colours
        - Make it colorfull with interactice visuals
        - Do NOT perform any calculations
        - Use the values exactly as provided

        OUTPUT FORMAT:
        - at top show current_overall_attendance and predicted_overall_attendance
        - at middle create a table containing subject_code, current_attendance_percent, predicted_attendance_percent in comparision with proper highlighting of predicted attendance (light green if >=75 else light red) 
        - at bottom highlight improvement or decline with proper discussion about user's attendance behaviour
        
        User query: {user_query}"""
    
    try:
        result = groq_api.call_groq(prompt)
        
        if result:
            result = result.replace("```html", "").replace("```", "")

            # Find all <section> tags
            sections = [m.start() for m in re.finditer(r"<section>", result)]

            if len(sections) >= 2 and "</section>" not in result:
                # Replace LAST <section> with </section>
                last_index = sections[-1]
                result = result[:last_index] + "</section>" + result[last_index + len("<section>"):]

            # Extract clean block
            match = re.search(r"<section>.*?</section>", result, re.DOTALL)

            if match:
                return (match.group(0), predicted_attendance_record)
            else: 
                return (result, predicted_attendance_record)
        else:
            return ("Try again I'm unable to answer this now, but i have given the chart in the dashbooard section", predicted_attendance_record)

    except Exception as e:
        logging.error("Errror during prediction intent: ", e)
        return ("Try again", predicted_attendance_record)
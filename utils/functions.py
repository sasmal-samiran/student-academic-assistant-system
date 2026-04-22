import os, re, sqlite3
from services import groq_api

from config import SQL_DB_DIR
from ai_engine.student_repository import STUDENT_REPOSITORY
from utils.logger import setup_logger

logger = setup_logger(__name__)

def _generate_sql(prompt):
    try:
        result = groq_api.call_groq(prompt)
        start = result.find("SELECT")
        end = result.find(";")
        
        return result[start: end+1]
    
    except Exception as e:
        logger.error(str(e))
    
def execute_sql(prompt):
    sql_query = _generate_sql(prompt)
    conn = sqlite3.connect(os.path.join(SQL_DB_DIR, "university.db"))
    cursor = conn.cursor()
    if not sql_query:
        return None
    try:
        result = cursor.execute(sql_query)
        result=result.fetchall()
    except Exception as e:
        return f"Error in sql: {e}"
    conn.close()
    
    return {
        "sql_query": sql_query,
        "result": result
    }

def generate_chart(data, user_query):
    prompt = f"""
    Role: You are a data visualization assistant.

    Task:
    Based on the user query and provided data, generate a valid Chart.js configuration in JSON format.
    If the response is suitable for visualization, generate a valid Chart.js configuration in JSON format.
    If the response is NOT suitable for visualization, return exactly: None

    STRICT RULES:
    - Return ONLY one of the following:
        1. valid JSON (no explanation, no markdown, no extra text)
        2. None

    - Do NOT include HTML or JavaScript code
    - Do NOT include comments
    - Ensure JSON is properly formatted and parsable

    WHEN TO RETURN NONE:
    Return None if:
    - the data is missing, empty, or insufficient for charting
    - the response is purely textual, descriptive, procedural, or conversational
    - there is no meaningful comparison, trend, proportion, or numeric relationship to visualize
    - the query asks for a single fact, sentence, status, definition, or explanation
    - labels and values cannot be clearly mapped from the provided data
    - visualization would not add useful value

    WHEN TO GENERATE A CHART:
    Generate a chart only if the query and data clearly support visualization such as:
    - comparison between values
    - trend over time
    - distribution/proportion
    - current vs predicted values
    - subject-wise or category-wise numeric analysis

    CHART SELECTION RULE:
    - If query is about comparison → use "bar"
    - If query is about trend over time → use "line"
    - If query is about distribution → use "pie"

    DATA RULES:
    - From the provided data, use only the relevant fields required to create a meaningful visualization; ignore any unnecessary or unrelated data.
    - Use the provided data exactly as given
    - Do NOT generate or assume any new values
    - Labels must come from subject_name or given labels
    - Data must come from current and predicted values

    OUTPUT STRUCTURE:
            {{
        "type": "bar | line | pie",
        "title": "write here a short meaningful title based on user query and the chart you have given",
        "data": {{
            "labels": [...],
            "datasets": [...]
        }}
        }}

    OPTIONAL:
    - You may add "backgroundColor" for better visualization
    - always use white text colours and any dark colour for visuals
    - Keep the structure simple and clean

    IMPORTANT DECISION RULE:
    First decide whether a chart is truly appropriate.
    - If yes, return only valid JSON
    - If no, return only None

    INPUT DATA:
    {data}

    USER QUERY:
    {user_query}
    """
    responce = groq_api.call_groq(prompt)
    
    if responce == "None" or None:
        responce = None
    
    return responce

def extract_entities(query, student_names, student_codes):
    query = re.sub(r'\s+', ' ', query).strip()
    query_lower = query.lower()
    query_upper = query.upper()
    self_keywords = ["my", "me", "myself", "mine", "i", "for me"]
    is_self = any(word in query_lower for word in self_keywords)

    found_names = []
    for name in student_names:
        pattern = r'\b' + re.escape(name.lower()) + r'\b'
        if re.search(pattern, query_lower):
            found_names.append(name)

    code_pattern = r'\b[A-Z]{2,}/[A-Z]{2,}/\d{2}/\d{3}\b'
    extracted_codes = re.findall(code_pattern, query_upper)
    valid_codes = [code for code in extracted_codes if code in student_codes]

    if not found_names and not valid_codes:
        if is_self:
            valid_codes = [STUDENT_REPOSITORY['student_code']]
        else:
            valid_codes = []

    return {"names": found_names, "codes": valid_codes}
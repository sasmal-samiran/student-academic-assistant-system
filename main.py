from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import tempfile, os

from services import speech_to_text
from ai_engine import classify, query_database, query_timetable, query_attendance, semantic_search, predict
from utils.logger import setup_logger
from config import APP_NAME

logger = setup_logger(__name__)

app = FastAPI(title=APP_NAME)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Application started")
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/ai_engine")
async def ai_engine(
        audio: Optional[UploadFile] = File(None),
        text: Optional[str] = Form(None)
    ):
    user_query = None

    if audio:
        try:
            # Save temp audio file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                temp_audio.write(await audio.read())
                temp_audio_path = temp_audio.name

            user_query = speech_to_text.convert(temp_audio_path)

            os.remove(temp_audio_path)

        except Exception as e:
            return {"bot_reply": "Error processing audio input.",
                    "user_query": user_query}

    elif text:
        user_query = text
    
    attendance_record = None
    predicted_attendance_record = None
    chart = None
    intent = classify(user_query)
    print("Intent: ",intent)

    if intent == "query_university_data":
        bot_reply, chart = query_database(user_query)
    elif intent == "timetable":
        bot_reply, chart = query_timetable(user_query)
    elif intent == "attendance":
        bot_reply, attendance_record = query_attendance(user_query)
    elif intent == "prediction":
        bot_reply, predicted_attendance_record = predict(user_query)
    elif intent == "semantic_search":
        bot_reply = semantic_search(user_query)
    elif intent == "greeting":
        bot_reply = "<p>Hello, I'm <strong>ASPAS</strong></p>"
    elif intent == "help":
        bot_reply = """
            <h3>Hello, I am ASPAS</h3>
            <p>I can help you with multiple things:</p>
            <hr>
            <br>
            <ul>
                <li>📅 <strong>Timetable:</strong> Ask about today’s classes, next class, subject timings, faculty, or classroom (e.g., “What is my next class?”)</li>
                <li>📊 <strong>Attendance:</strong> Check your attendance percentage, subject-wise records, daily history, or low attendance alerts (e.g., “Show my attendance in Machine Learning and its Applications”)</li>
                <li>🎓 <strong>University Data:</strong> Get details about subjects, faculty, or your academic profile (e.g., “Who teaches Machine Learning?”)</li>
                <li>🤖 <strong>Prediction:</strong> Get insights like attendance risk or performance analysis</li>
            </ul>
            <p>Just ask in simple language like you normally would 👍</p>
            """
    elif intent == "other":
        bot_reply = "Sorry, I am not permitted to answer related to your query"
    else:
        bot_reply = intent

    return {
        "bot_reply": bot_reply,
        "user_query": user_query,
        "attendance_record": attendance_record if attendance_record else None,
        "predicted_attendance_record": predicted_attendance_record if predicted_attendance_record else None,
        'chart_config': chart if chart else None
    }
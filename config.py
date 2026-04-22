# config/settings.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

## APP CONFIGURATIONS
APP_NAME = "ASPAS"
HOST = "127.0.0.1"
PORT = 8000
DEBUG = True
RELOAD = True

## DIRECTORIES
SQL_DB_DIR = os.path.join(BASE_DIR, "data/sql/")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data/vector/")
ML_MODEL_DIR = os.path.join(BASE_DIR, "data/models/")
DATASETS_DIR = os.path.join(BASE_DIR, "datasets/")

## PATHS
LOG_PATH = os.path.join(BASE_DIR, "logs/error_logs.log")

## MODELS
GROQ_CHAT_MODEL = "openai/gpt-oss-120b"
GROQ_TRANSCRIPTION_MODEL = "whisper-large-v3-turbo"
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
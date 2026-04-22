from groq import Groq
import os
from dotenv import load_dotenv

from config import GROQ_TRANSCRIPTION_MODEL
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

client = Groq(api_key= os.getenv("GROQ_API_KEY"))

def convert(filename):
    try:
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model=GROQ_TRANSCRIPTION_MODEL,
                temperature=0,
                response_format="verbose_json",
                language="en"
            )

        return transcription.text

    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return "Error: File not found"

    except PermissionError:
        logger.error(f"Permission denied: {filename}")
        return "Error: Permission denied"

    except Exception as e:
        logger.exception(f"Transcription failed: {str(e)}")
        return "Error: Transcription failed"
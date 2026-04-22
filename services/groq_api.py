import os
from groq import Groq
from dotenv import load_dotenv

from config import GROQ_CHAT_MODEL
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(prompt):
    try:
        response = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        if not response or not response.choices:
            logger.info("Empty response received from model.")
            return "No response generated. Please try again."

        return response.choices[0].message.content.strip()

    except TimeoutError:
        logger.error(f"Groq API timeout {error_msg}")
        return "Request timed out. Please try again."

    except ConnectionError:
        logger.error(f"Groq API connection error {error_msg}")
        return "Network error. Check your internet connection."

    except Exception as e:
        error_msg = str(e)

        if "rate limit" in error_msg.lower() or "429" in error_msg:
            logger.error(f"Groq API rate limit exceeded {error_msg}")

        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            logger.error(f"Groq API usage limit reached. {error_msg}")

        else:
            logger.exception(f"Groq API Error: {e}")
        return "Something went wrong while processing your request."
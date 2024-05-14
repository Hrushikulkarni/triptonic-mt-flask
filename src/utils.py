import os
from dotenv import load_dotenv
from pathlib import Path

def load_secrets():
  load_dotenv()
  env_path = Path("..") / ".env"
  load_dotenv(dotenv_path=env_path)

  google_gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
  google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
  mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")

  return {
    "GOOGLE_GEMINI_API_KEY": google_gemini_key,
    "GOOGLE_MAPS_API_KEY": google_maps_key,
    "MONGO_CONNECTION_STRING": mongo_connection_string
  }

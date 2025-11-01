import firebase_admin, os
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends
from firebase_admin import credentials, firestore
from fastapi.security import OAuth2PasswordBearer
from typing import Any

from auth import get_user_from_credentials
from processLogs import raw_log_to_json, save_logs

@asynccontextmanager
async def lifespan(app):
    """
    Create a DB connection that persists throughout the server's lifetime.
    """
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(os.environ.get("FIRESTORE_KEY_PATH"))
        firebase_admin.initialize_app(cred)

    app.state.db = firestore.client()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/parse/upload")
async def upload_workout_log(
    user_info: dict[str, Any] = Depends(get_user_from_credentials),
    workout_log_file: UploadFile = File(None),
    workout_log_text: str = Form(None),
):
    """
    Workout logs can be passed in as either a file or as raw text.
    Utilize an LLM to parse the workout logs into JSON.
    """
    workout_logs = await raw_log_to_json(workout_log_file, workout_log_text)
    return save_logs(user_info, workout_logs)
    

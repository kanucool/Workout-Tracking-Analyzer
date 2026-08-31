import firebase_admin, os
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException
from firebase_admin import credentials, firestore
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Any
from collections import deque
import asyncio

from auth import get_user_from_credentials
from processLogs import LogProcessor
from firestore.firestore import FirestoreConnector
import constants.constants as constants

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

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

    app.state.db = FirestoreConnector(db=firestore.client())
    app.state.sem = asyncio.Semaphore(constants.THREAD_LIMIT)
    app.state.reqs = deque()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                )

@app.get("/workouts")
async def get_workouts(user_info: dict[str, Any] = Depends(get_user_from_credentials)):
    processor = LogProcessor(db=app.state.db, sem=app.state.sem, reqs=app.state.reqs)
    return await processor.make_thread(app.state.db.get_workouts, uid=user_info["uid"])


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
    processor = LogProcessor(db=app.state.db, sem=app.state.sem, reqs=app.state.reqs)
    workout_logs = await processor.parse_raw_data(
        workout_log_file=workout_log_file,
        workout_log_text=workout_log_text
    )
    return await processor.save_logs(user_info["uid"], workout_logs)
    

@app.get("/auth/me")
async def authorize(user_info: dict[str, Any] = Depends(get_user_from_credentials)):
    print(user_info)
    return user_info

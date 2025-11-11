import io, os, json, time
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException, File, Form
from google import genai
from google.genai import types
from typing import Optional, Callable
from itertools import zip_longest
from collections import deque
import asyncio
from threading import Lock
from Levenshtein import distance
import time

import models
from firestore.firestore import FirestoreConnector
import constants.constants as constants

GEMINI_KEY = os.environ.get("GEMINI_KEY")
CLIENT = genai.Client(api_key=GEMINI_KEY)

class LogProcessor:
    def __init__(self, db: FirestoreConnector, sem: asyncio.Semaphore, reqs: deque):
        self.db = db
        self.sem = sem
        self.reqs = reqs
        self.req_lock = Lock()
    
    def request_gemini(self, **kwargs):
        while True:
            with self.req_lock:
                curr_time = time.time()
                while self.reqs and self.reqs[0] < curr_time - 60:
                    self.reqs.popleft()
                
                if len(self.reqs) < constants.RATE_LIMIT:
                    self.reqs.append(curr_time)
                    break
                
            time.sleep(1)
        
        return CLIENT.models.generate_content(
                        **kwargs,
                    )

    def parse_workout_chunk(self, workouts: list[str]) -> Optional[models.WorkoutLog]:
        try:
            start = time.time()

            response = self.request_gemini(model='gemini-2.5-flash-lite',
                contents=f"{constants.WORKOUT_LOG_TO_STANDARDIZED_FORMAT_PROMPT}\n{'\n'.join(workouts)}",
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=models.WorkoutLog,
                ),)
            assert response and response.text
            print(f"chunk processed in {time.time() - start}")

            return models.WorkoutLog.model_validate(json.loads(response.text))

        except Exception as e:
            print(f"Parsing workouts chunk failed: {e}")
            return None

    async def make_thread(self, target_func: Callable, **kwargs):
        async with self.sem:
            return await asyncio.to_thread(
                target_func, **kwargs
            )
        
    def condense_workout_log(self, workout_log: models.WorkoutLog) -> models.WorkoutLog:
        exercise_mapping = {}
        workout_log = workout_log.model_copy(deep=True)

        for workout in workout_log.workouts:
            for exercise in workout.exercises:
                standardized_name = ' '.join(sorted(exercise.name.lower().split()))
                exercise.name = ' '.join(map(lambda word: word.strip("()").capitalize(),
                                          exercise.name.lower().split()))

                for prev_standardized, prev_name in exercise_mapping.items():
                    if distance(standardized_name, prev_standardized) <= 2:
                        exercise.name = prev_name
                        break
                else:
                    exercise_mapping[standardized_name] = exercise.name
        
        return workout_log

    async def parse_workout_log(self, workout_log_text: str) -> models.WorkoutLog:
        start = time.time()
        print("Starting log splitter query")

        response = await self.make_thread(
            self.request_gemini,
            model='gemini-2.5-flash-lite',
            contents=f"{constants.SPLIT_BY_DATE_PROMPT}\n{workout_log_text}",
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=models.WorkoutLogRawText
            )
        )
        print(f"Workout log splitter query ran in {time.time() - start} seconds")

        start = time.time()

        assert response and response.text
        workouts = models.WorkoutLogRawText.model_validate(json.loads(response.text))
        print(f"Parsed {len(workouts.workouts)} workouts from log splitter query")
        
        parsing_tasks = [self.make_thread(self.parse_workout_chunk, workouts=list(chunk))
                        for chunk in zip_longest(
                            *(iter(workouts.workouts),) * constants.CHUNK_SIZE, fillvalue=''
                            )
                        ]
        
        parsed_chunks = filter(lambda workout_log: isinstance(workout_log, models.WorkoutLog),
                                await asyncio.gather(*parsing_tasks),)
        
        parsed_workouts = models.WorkoutLog(workouts=[])
        for workout_log_chunk in parsed_chunks:
            assert isinstance(workout_log_chunk, models.WorkoutLog)
            parsed_workouts.workouts.extend(workout_log_chunk.workouts)
        
        print(f"Time to parse workouts via multithreading is {time.time() - start}")

        return await self.make_thread(self.condense_workout_log, workout_log=parsed_workouts)

    def read_pdf(self, pdf_bytes: bytes):
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        file_content = '\n'.join(filter(lambda page: page,
                                    (
                                        page.extract_text()
                                        for page
                                        in pdf_reader.pages
                                    )
                                )
                            )
        return file_content

    async def extract_text_from_file(self, workout_log_file: UploadFile, filename: str,) -> str:
        if filename.endswith(".pdf"):
            pdf_bytes = await workout_log_file.read()
            file_content = await(self.make_thread(self.read_pdf,
                                    pdf_bytes=pdf_bytes))
            
        elif filename.endswith(".txt"):
            file_bytes = await workout_log_file.read()
            try:
                file_content = file_bytes.decode(encoding="utf-8")
            except UnicodeDecodeError:
                file_content = file_bytes.decode(encoding="latin-1")
        else:
            raise HTTPException(status_code=400, detail="The file must be a txt or a pdf.")

        return file_content

    async def parse_raw_data(self, workout_log_file: UploadFile = File(None),
                            workout_log_text: str = Form(None),) -> models.WorkoutLog:
        try:
            if workout_log_file and workout_log_text:
                raise HTTPException(status_code=400, detail="Input either a file or text, not both.")
            
            if workout_log_file:
                filename = (workout_log_file.filename or "invalid").lower()
                file_content = await self.extract_text_from_file(
                                            workout_log_file=workout_log_file,
                                            filename=filename,)
                
                mega_chunks = [file_content[i:i + constants.MEGA_CHUNK_SIZE]
                               for i in range(0, len(file_content), constants.MEGA_CHUNK_SIZE)]

                parsing_tasks = [self.parse_workout_log(chunk) for chunk in mega_chunks]

                parsed_chunks = filter(lambda workout_log: isinstance(workout_log, models.WorkoutLog),
                                await asyncio.gather(*parsing_tasks),)
        
                parsed_workouts = models.WorkoutLog(workouts=[])
                for workout_log_chunk in parsed_chunks:
                    assert isinstance(workout_log_chunk, models.WorkoutLog)
                    parsed_workouts.workouts.extend(workout_log_chunk.workouts)
            
                return await self.make_thread(self.condense_workout_log, workout_log=parsed_workouts)
            
            elif workout_log_text:
                return await self.parse_workout_log(workout_log_text=workout_log_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Parsing workout log failed: {e}")
        
        raise HTTPException(status_code=400, detail="Neither a file or raw text was provided.")


    async def save_logs(self,
                        uid: str,
                        workout_log: models.WorkoutLog,
                        ) -> str:
        try:
            await self.make_thread(self.db.save_workout_log, uid=uid, workout_log=workout_log)
            return "OK"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Saving workout log failed: {e}")
    
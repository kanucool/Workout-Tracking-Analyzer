import pdf4llm, tempfile, os, json, time
from fastapi import UploadFile, HTTPException, File, Form
from google import genai
from google.genai import types
from typing import Any
import asyncio

import models
from firestore.firestore import Firestore
from constants.constants import BASE_PROMPT

GEMINI_KEY = os.environ.get("GEMINI_KEY")
CLIENT = genai.Client(api_key=GEMINI_KEY)


async def parse_workout_log(workout_log_text: str) -> models.WorkoutLog:
    start = time.time()
    response = CLIENT.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=f"{BASE_PROMPT}\n{workout_log_text}",
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=models.WorkoutLog,
        ),
    )
    print(f"query took {time.time() - start} seconds to run")
    assert response and response.text
    return models.WorkoutLog.model_validate(json.loads(response.text))


async def extract_text_from_pdf(filename: str) -> str:
    assert filename.endswith(".pdf")
    return pdf4llm.to_markdown(doc=filename, ignore_images=True)


async def extract_text_from_file(workout_log_file: UploadFile, filename: str) -> str:
    if filename.endswith(".pdf"):
        pdf = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf:
                pdf.write(await workout_log_file.read())

            file_content = pdf4llm.to_markdown(doc=pdf.name, ignore_images=True)
        except Exception as e:
            raise
        finally:
            if pdf and os.path.exists(pdf.name):
                os.unlink(pdf.name)

    elif filename.endswith(".txt"):
        file_bytes = await workout_log_file.read()
        try:
            file_content = file_bytes.decode(encoding="utf-8")
        except UnicodeDecodeError:
            file_content = file_bytes.decode(encoding="latin-1")
    else:
        raise HTTPException(status_code=400, detail="The file must be a txt or a pdf.")

    return file_content


async def raw_log_to_json(workout_log_file: UploadFile = File(None),
                    workout_log_text: str = Form(None)) -> models.WorkoutLog:
    try:
        if workout_log_file and workout_log_text:
            raise HTTPException(status_code=400, detail="Input either a file or text, not both.")
        
        if workout_log_file:
            filename = (workout_log_file.filename or "invalid").lower()
            return await parse_workout_log(await extract_text_from_file(
                                        workout_log_file=workout_log_file,
                                        filename=filename,)
                                    )
        elif workout_log_text:
            return parse_workout_log(workout_log_text=workout_log_text).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing workout log failed: {e}")
    
    raise HTTPException(status_code=400, detail="Neither a file or raw text was provided.")


async def save_logs(uid: str,
                    workout_log: models.WorkoutLog,
                    db: Firestore) -> str:
    try:
        db.save_workout_log(uid, workout_log)
        return "OK"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Saving workout log failed: {e}")


async def main():
    json_data = (await parse_workout_log(await extract_text_from_pdf(
                    "tests/LEG & SHOULDERS Tracking.pdf"
                    ))).model_dump_json(indent=2)
    
    with open("tests/exampleLog.json", "w") as fp:
        fp.write(json_data)


if __name__ == "__main__":
    asyncio.run(main())
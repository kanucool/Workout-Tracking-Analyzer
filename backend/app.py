from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from processLogs import extract_text_from_file, parse_workout_log

app = FastAPI()

@app.post("/parse/upload")
async def upload_workout_log(
    workout_log_file: UploadFile = File(None),
    workout_log_text: str = Form(None),
):
    """
    Workout logs can be passed in as either a file or as raw text.
    Utilize an LLM to parse the workout logs into JSON.
    """
    try:
        if workout_log_file and workout_log_text:
            raise HTTPException(status_code=400, detail="Input either a file or text, not both.")
        
        if workout_log_file:
            filename = (workout_log_file.filename or "invalid").lower()
            return parse_workout_log(await extract_text_from_file(
                                        workout_log_file=workout_log_file,
                                        filename=filename,)
                                    )
        elif workout_log_text:
            return parse_workout_log(workout_log_text=workout_log_text).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing workout log failed: {e}")
    
    raise HTTPException(status_code=400, detail="Neither a file or raw text was provided.") 

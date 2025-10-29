import pdf4llm, tempfile, os
from fastapi import UploadFile, HTTPException


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
            try:
                if pdf and os.path.exists(pdf.name):
                    os.unlink(pdf.name)
            except OSError as e:
                with open("logging/garbage_files.txt", "a") as fp:
                    fp.write(f"{pdf.name if pdf else "DNE"}: {e}\n")

    elif filename.endswith(".txt"):
        file_bytes = await workout_log_file.read()
        try:
            file_content = file_bytes.decode(encoding="utf-8")
        except UnicodeDecodeError:
            file_content = file_bytes.decode(encoding="latin-1")
    else:
        raise HTTPException(status_code=400, detail="The file must be a txt or a pdf.")

    return file_content


def parse_workout_log(workout_log_text: str) -> str:
    return ""
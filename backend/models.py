from pydantic import BaseModel

class WorkoutLogRawText(BaseModel):
    workouts: list[str]

class Sets(BaseModel):
    reps: int
    weight: float
    unit: str

class Exercise(BaseModel):
    name: str
    sets: list[Sets]
    
class Workout(BaseModel):
    date: str
    exercises: list[Exercise]
    notes: list[str]

class WorkoutLog(BaseModel):
    workouts: list[Workout]

from google.cloud.firestore import Client as FirestoreClient

import models

class FirestoreConnector:
    def __init__(self, db: FirestoreClient):
        self.db = db

    def save_workout(self, uid: str, workout: models.Workout):
        self.db.collection("users")\
                .document(uid)\
                .collection("workouts")\
                .document(workout.date)\
                .set(workout.model_dump())
            
    def save_workout_log(self, uid: str, workout_log: models.WorkoutLog):
        user_ref = self.db.collection("users").document(uid).collection("workouts")
        bulk_writer = self.db.bulk_writer()

        try:
            for workout in workout_log.workouts:
                workout_ref = user_ref.document(workout.date)
                bulk_writer.set(workout_ref, workout.model_dump())
        finally:
            bulk_writer.close()
    
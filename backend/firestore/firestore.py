from google.cloud.firestore import Client as FirestoreClient

class Firestore:
    def __init__(self, db: FirestoreClient):
        self.db = db

    

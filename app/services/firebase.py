import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from typing import List, Dict, Any

class FirebaseService:
    def __init__(self):
        self.db = None
        self.bucket = None
        self.initialized = False
        # Mock DB structure: { "teams": { "Team A": ["Alice", "Bob"] }, "tasks": [] }
        self.mock_db = {
            "teams": {},
            "tasks": []
        }
        self._initialize()

    def _initialize(self):
        try:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET", "your-app.appspot.com")
                })
                self.db = firestore.client()
                self.bucket = storage.bucket()
                self.initialized = True
                print("Firebase initialized successfully.")
            else:
                print(f"Warning: Firebase credentials not found at {cred_path}. Running in mock mode.")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")

    def create_team(self, team_name: str) -> str:
        if not self.initialized:
            if team_name in self.mock_db["teams"]:
                return f"Team '{team_name}' already exists."
            self.mock_db["teams"][team_name] = []
            return f"Team '{team_name}' created successfully."
        # Real implementation would go here
        return "Firebase create_team not implemented yet."

    def add_member(self, team_name: str, user_name: str) -> str:
        if not self.initialized:
            if team_name not in self.mock_db["teams"]:
                return f"Team '{team_name}' does not exist."
            if user_name in self.mock_db["teams"][team_name]:
                return f"User '{user_name}' is already in team '{team_name}'."
            self.mock_db["teams"][team_name].append(user_name)
            return f"User '{user_name}' added to team '{team_name}'."
        # Real implementation would go here
        return "Firebase add_member not implemented yet."

    def delete_team(self, team_name: str) -> str:
        if not self.initialized:
            if team_name in self.mock_db["teams"]:
                del self.mock_db["teams"][team_name]
                return f"Team '{team_name}' deleted."
            return f"Team '{team_name}' not found."
        return "Firebase delete_team not implemented yet."

    def remove_member(self, team_name: str, user_name: str) -> str:
        if not self.initialized:
            if team_name in self.mock_db["teams"]:
                if user_name in self.mock_db["teams"][team_name]:
                    self.mock_db["teams"][team_name].remove(user_name)
                    return f"User '{user_name}' removed from '{team_name}'."
            return "Member or team not found."
        return "Firebase remove_member not implemented yet."

    def get_all_teams(self) -> Dict[str, List[str]]:
        if not self.initialized:
            return self.mock_db["teams"]
        # Real implementation would go here
        return {}

    def add_task(self, task_data: Dict[str, Any]) -> str:
        if not self.initialized:
            task_data["id"] = f"mock_{len(self.mock_db['tasks']) + 1}"
            self.mock_db["tasks"].append(task_data)
            return f"Task '{task_data.get('title')}' added with ID: {task_data['id']}"
        
        try:
            doc_ref = self.db.collection('tasks').add(task_data)
            return f"Task added with ID: {doc_ref[1].id}"
        except Exception as e:
            return f"Error adding task: {str(e)}"

    def delete_task(self, task_id: str) -> str:
        if not self.initialized:
            initial_len = len(self.mock_db["tasks"])
            self.mock_db["tasks"] = [t for t in self.mock_db["tasks"] if t.get("id") != task_id]
            if len(self.mock_db["tasks"]) < initial_len:
                return f"Task {task_id} deleted."
            return "Task not found."
        
        try:
            self.db.collection('tasks').document(task_id).delete()
            return f"Task {task_id} deleted."
        except Exception as e:
            return f"Error deleting task: {str(e)}"

    def get_tasks(self, user_id: str = None) -> List[Dict[str, Any]]:
        if not self.initialized:
            if user_id:
                return [t for t in self.mock_db["tasks"] if t.get("assignee", "").lower() == user_id.lower()]
            return self.mock_db["tasks"]
        
        try:
            tasks_ref = self.db.collection('tasks')
            if user_id:
                query = tasks_ref.where('assignee', '==', user_id)
                docs = query.stream()
            else:
                docs = tasks_ref.stream()
            
            return [{**doc.to_dict(), "id": doc.id} for doc in docs]
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

    def upload_file(self, file_path: str, destination_blob_name: str) -> str:
        if not self.initialized:
            return f"Mock: File {file_path} uploaded to {destination_blob_name}"
        
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            return blob.public_url
        except Exception as e:
            return f"Error uploading file: {str(e)}"

firebase_service = FirebaseService()

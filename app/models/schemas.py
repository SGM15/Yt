from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    assignee: Optional[str] = None
    status: str = "pending"
    deadline: Optional[str] = None

class ProjectState(BaseModel):
    tasks: List[Task] = []
    documents: List[str] = []
    messages: List[Dict[str, Any]] = []
    
class UserRequest(BaseModel):
    query: str
    user_id: str

class AgentResponse(BaseModel):
    response: str
    actions_taken: List[str] = []

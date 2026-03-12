from langchain_core.tools import tool
from typing import List
from app.services.firebase import firebase_service
from app.services.calendar import calendar_service
from langchain_community.utilities import SerpAPIWrapper
from app.core.config import settings

@tool
def research_technical_question(query: str) -> str:
    """
    Researches a technical question or project-related topic using Google Search.
    Use this tool when the user asks for technical help, documentation, libraries, or best practices.
    """
    try:
        if not settings.SERPAPI_API_KEY:
            return "Error: SerpAPI Key is missing. Please add SERPAPI_API_KEY to the .env file."
        
        search = SerpAPIWrapper(serpapi_api_key=settings.SERPAPI_API_KEY)
        return search.run(query)
    except Exception as e:
        return f"Error performing search: {str(e)}"

@tool
def assign_task(task_description: str, assignee: str, deadline: str) -> str:
    """Assigns a task to a team member with a deadline and syncs to calendar."""
    task_data = {
        "title": task_description,
        "assignee": assignee,
        "deadline": deadline,
        "status": "pending",
        "created_at": "now" # In real app use datetime
    }
    
    # Save to Firebase
    db_result = firebase_service.add_task(task_data)
    
    # Sync to Calendar (assuming deadline is a valid ISO string or we parse it)
    # For demo, we just use the string as is or mock it
    cal_result = calendar_service.create_event(
        summary=f"Task: {task_description}",
        start_time=deadline, # This needs proper formatting in real usage
        end_time=deadline
    )
    
    return f"{db_result}. {cal_result}"

@tool
def share_document(document_name: str, recipients: List[str]) -> str:
    """Shares a document with specified recipients."""
    # In a real scenario, this would generate a signed URL from Firebase Storage
    return f"Document '{document_name}' shared with {', '.join(recipients)} via Firebase Storage."

@tool
def check_progress(team_name: str) -> str:
    """
    Checks the progress of a team by listing tasks for all its members.
    Returns a detailed status including task assignment, completion status, and ratios.
    """
    teams = firebase_service.get_all_teams()
    if team_name not in teams:
        return f"Team '{team_name}' not found."
    
    members = teams[team_name]
    if not members:
        return f"Team '{team_name}' has no members."
    
    report = []
    all_tasks = firebase_service.get_tasks() # Get all tasks to filter in memory
    
    for member in members:
        member_tasks = [t for t in all_tasks if t.get('assignee') == member]
        total = len(member_tasks)
        completed = len([t for t in member_tasks if t.get('status') == 'completed'])
        
        task_details = []
        for t in member_tasks:
            status_icon = "✅" if t.get('status') == 'completed' else "⏳"
            task_details.append(f"- {t.get('title')} ({status_icon} {t.get('status')})")
            
        if total > 0:
            report.append(f"**{member}**: {completed}/{total} tasks completed")
            report.extend(task_details)
        else:
            report.append(f"**{member}**: No tasks assigned (0/0)")
            
    return "\n".join(report)

@tool
def delete_team(team_name: str) -> str:
    """Deletes a team."""
    return firebase_service.delete_team(team_name)

@tool
def remove_team_member(team_name: str, user_name: str) -> str:
    """Removes a user from a team."""
    return firebase_service.remove_member(team_name, user_name)

@tool
def delete_task(task_id: str) -> str:
    """Deletes a task by its ID."""
    # Note: The user might not know the ID, so the agent might need to search first or the user provides context.
    # For now, we assume the agent can figure it out or asks for it.
    return firebase_service.delete_task(task_id)

@tool
def get_performance_insights(user_id: str) -> str:
    """Retrieves performance insights for a user."""
    tasks = firebase_service.get_tasks(user_id)
    completed = len([t for t in tasks if t.get('status') == 'completed'])
    total = len(tasks)
    
    if total == 0:
        return f"No tasks found for user {user_id}."
        
    return f"User {user_id} has completed {completed} out of {total} tasks."

@tool
def set_reminder(task_id: str, time: str) -> str:
    """Sets a smart deadline reminder."""
    # This would ideally interface with the Scheduler service dynamically
    return f"Reminder set for task {task_id} at {time}."

@tool
def create_team(team_name: str) -> str:
    """Creates a new team."""
    return firebase_service.create_team(team_name)

@tool
def add_team_member(team_name: str, user_name: str) -> str:
    """Adds a user to a team."""
    return firebase_service.add_member(team_name, user_name)

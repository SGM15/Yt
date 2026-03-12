from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.models.schemas import UserRequest, AgentResponse
from app.agents.graph_new import app_graph
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.services.scheduler import start_scheduler
import os

from app.services.firebase import firebase_service

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup_event():
    start_scheduler()
    print(f"Using Model: {settings.MODEL_NAME}")

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/api/teams")
async def get_teams():
    return firebase_service.get_all_teams()

@app.delete("/api/teams/{team_name}")
async def delete_team(team_name: str):
    return {"message": firebase_service.delete_team(team_name)}

@app.delete("/api/teams/{team_name}/members/{member_name}")
async def remove_member(team_name: str, member_name: str):
    return {"message": firebase_service.remove_member(team_name, member_name)}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    return {"message": firebase_service.delete_task(task_id)}

@app.get("/api/member/{member_name}")
async def get_member_details(member_name: str):
    tasks = firebase_service.get_tasks(member_name)
    completed_count = len([t for t in tasks if t.get('status') == 'completed'])
    total_count = len(tasks)
    
    return {
        "name": member_name,
        "completed_tasks": completed_count,
        "total_tasks": total_count,
        "tasks": tasks
    }

@app.post("/chat", response_model=AgentResponse)
async def chat(request: UserRequest):
    try:
        # Use user_id as thread_id for persistence
        config = {"configurable": {"thread_id": request.user_id}}
        inputs = {"messages": [HumanMessage(content=request.query)]}
        
        result = app_graph.invoke(inputs, config=config)
        
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        return AgentResponse(response=response_text)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return AgentResponse(response="Error: Unauthorized. Please check your API Key in the .env file.")
        if "429" in error_msg or "rate limit" in error_msg.lower():
            return AgentResponse(response="Error: Rate limit exceeded. Please wait a moment before trying again.")
        print(f"Error processing request: {e}")
        return AgentResponse(response=f"Sorry, I encountered an error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

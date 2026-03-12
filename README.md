# TrackUp

TrackUp is a conversational AI agent for managing group project activities. It helps teams with task assignment, document sharing, progress tracking, performance insights, and smart deadline reminders.

## Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **AI/ML:** LangChain, LangGraph
- **Model:** GitHub GPT-4o
- **Database:** (To be implemented, currently in-memory/mock)

## Features

- **Task Assignment:** Assign tasks to team members with deadlines.
- **Document Sharing:** Share documents with specific recipients.
- **Progress Tracking:** Check the status of the project.
- **Performance Insights:** Get insights into team member performance.
- **Smart Reminders:** Set reminders for deadlines.

## Setup

### Run in GitHub Codespaces

1.  Click the green **Code** button on the repository page and select **Open with Codespaces**.
2.  Once the codespace is ready, dependencies will be installed automatically.
3.  Copy `.env.example` to `.env` and fill in your API keys:
    ```bash
    cp .env.example .env
    ```
4.  Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```

### Run Locally

1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up environment variables:
    Copy `.env.example` to `.env` and fill in your API keys.
    ```bash
    cp .env.example .env
    ```
5.  Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```

## Usage

Send a POST request to `/chat` with a JSON body:

```json
{
  "query": "Assign the report task to Alice with a deadline of next Friday",
  "user_id": "user123"
}
```
from fastapi import FastAPI, HTTPException
import requests
import os
from datetime import datetime

app = FastAPI()

# Notion API Credentials
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.get("/")
def read_root():
    return {"message": "Study Manager AI Backend is Running!"}

@app.post("/add_log")
def add_log(task_name: str, status: str, mistakes: str = "None", rewards: str = "None"):
    """Adds a new study log entry to Notion."""
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Task/Quest Name": {"title": [{"text": {"content": task_name}}]},
            "Status": {"select": {"name": status}},
            "Mistakes & Corrections": {"rich_text": [{"text": {"content": mistakes}}]},
            "Boss Battles & Rewards": {"rich_text": [{"text": {"content": rewards}}]},
            "Date": {"date": {"start": datetime.utcnow().isoformat()}}
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", json=data, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to add log: {response.json()}")
    return {"message": "Log added successfully!"}

@app.get("/analyze_mistakes")
def analyze_mistakes():
    """Analyzes mistakes and suggests improvements."""
    response = requests.post("https://api.notion.com/v1/databases/{DATABASE_ID}/query", headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data: {response.json()}")
    data = response.json()
    mistake_trends = {}
    for entry in data.get("results", []):
        mistakes = entry["properties"]["Mistakes & Corrections"]["rich_text"]
        if mistakes:
            mistake_text = mistakes[0]["text"]["content"]
            if mistake_text in mistake_trends:
                mistake_trends[mistake_text] += 1
            else:
                mistake_trends[mistake_text] = 1
    return {"Mistake Analysis": mistake_trends}

@app.get("/search_web")
def search_web(query: str):
    """Fetches study recommendations from the web."""
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key=YOUR_GOOGLE_API_KEY"
    response = requests.get(search_url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch web results.")
    return response.json()
import time
from fastapi import FastAPI
from threading import Thread

app = FastAPI()

# Global variable to track the last time the server was active
last_active_time = time.time()

# Function to check the time of inactivity and make the app "sleep"
def monitor_inactivity():
    global last_active_time
    while True:
        # Check if the server has been inactive for more than 20 minutes (1200 seconds)
        if time.time() - last_active_time > 1200:
            print("Server is going to sleep due to inactivity.")
            # Put the server into sleep mode (we're just simulating it here)
            time.sleep(60)  # Sleep for 1 minute (you can adjust as needed)
            print("Server is awake!")
        time.sleep(10)  # Check every 10 seconds

# Start the inactivity monitor in a separate thread
Thread(target=monitor_inactivity, daemon=True).start()

@app.get("/")
async def root():
    global last_active_time
    last_active_time = time.time()  # Update the last active time when a request comes in
    return {"message": "Server is active!"}


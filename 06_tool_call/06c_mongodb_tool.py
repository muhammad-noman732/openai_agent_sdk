import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from typing_extensions import Any
import asyncio
import httpx 
from bson import ObjectId
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    FunctionTool,
    function_tool
)

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# ------------------------------
# Load API Key (Gemini via OpenAI client)
# ------------------------------
load_dotenv()

# ------------------------------
# MongoDB Connection
# ------------------------------
uri = os.getenv("MONGO_URL")
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    print(e)

# ------------------------------
# Initialize OpenAI-compatible Gemini client
# ------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client,
)

# ------------------------------
# Input Schema for the Tool
# ------------------------------
class TodoInput(BaseModel):
    """
    Schema for creating a To-Do item.

    Attributes:
        title (str): The title or title of the To-Do task.
        description (str): Detailed description of the task.
    """
    title: str
    description: str


# ------------------------------
# Tool Function to Create a To-Do
# ------------------------------
@function_tool
def create_todo(data: TodoInput) -> dict:
    """
    Create a new To-Do item and store it in MongoDB.

    Purpose:
        This tool allows the agent to add a new task to a MongoDB collection.
        It validates input using Pydantic, inserts the task, and returns the full stored document.

    Input Arguments:
        data (TodoInput): A Pydantic model containing:
            - title (str): Title of the To-Do.
            - description (str): Details about the To-Do.

    Behavior:
        1. Connects to the "todo_agent" database and the "todo" collection.
        2. Inserts a new document with the title and description.
        3. Returns a dictionary containing:
            - id (str): The unique MongoDB ID of the new To-Do.
            - title (str): The title of the To-Do.
            - description (str): The description of the To-Do.
        4. Handles any exceptions and returns an error message if insertion fails.

    Returns:
        dict: {
            "id": str,           # MongoDB-generated unique ID
            "title": str,        # Title of the To-Do
            "description": str   # Description of the To-Do
        }
        OR
        str: Error message if creation fails.
    """
    try:
        db = client["todo_agent"]
        collection = db["agent"]

        new_todo = {
            "title": data.title,
            "description": data.description
        }

        # Insert into MongoDB
        result = collection.insert_one(new_todo)

        return {
            "id": str(result.inserted_id),
            **new_todo
        }

    except Exception as e:
        return f"Error in creating todo: {e}"




   

# ------------------------------
# Tool Function to fetch all To-Dos
# ------------------------------
@function_tool
def fetch_todos() -> list[dict]:
    """
    Fetch all To-Do items from MongoDB.

    Purpose:
        Retrieves all tasks stored in the 'todo' collection.

    Input Arguments:
        None

    Behavior:
        1. Connects to the 'todo_agent' database and 'todo' collection.
        2. Retrieves all documents.
        3. Converts MongoDB ObjectId to string for readability.
        4. Returns a list of dictionaries representing the tasks.

    Returns:
        list[dict]: A list of todos, each containing:
            - id (str): MongoDB ID
            - title (str): Title of the task
            - description (str): Description of the task
        OR
        str: Error message if fetching fails.
    """
    try:
        db = client["todo_agent"]
        collection = db["agent"]

        todos = []
        for doc in collection.find():
            todos.append({
                "id": str(doc["_id"]),
                "title": doc["title"],
                "description": doc["description"]
            })

        return todos

    except Exception as e:
        return f"Error in fetching todos: {e}"


# ------------------------------
# Tool Function to fetch single To-Do by Title
# ------------------------------
@function_tool
def fetch_todo_by_title(title: str) -> dict:
    """
    Fetch a single To-Do item from MongoDB by its title.

    Input Arguments:
        title (str): The title of the task to fetch.

    Behavior:
        1. Connects to the 'todo_agent' database and 'agent' collection.
        2. Finds the first document with the given title.
        3. Converts ObjectId to string for readability.
        4. Returns the task as a dictionary.

    Returns:
        dict:
            {
                "id": str,          # The MongoDB ObjectId converted to string
                "title": str,       # The task title
                "description": str  # The task description
            }

        OR

        str:
            An error message if the task is not found or an error occurs.
    """
    try:
        # Connect to the database and collection
        db = client["todo_agent"]
        collection = db["agent"]

        # Search by title
        doc = collection.find_one({"title": title})
        if not doc:
            return f"No todo found with title: {title}"

        # Return structured dictionary
        return {
            "id": str(doc["_id"]),
            "title": doc["title"],
            "description": doc["description"]
        }

    except Exception as e:
        return f"Error in fetching todo: {e}"

# ------------------------------
# Tool Function to Update To-Do by Title
# ------------------------------
@function_tool
def update_todo_by_title(title: str, new_title: str | None = None, new_description: str | None = None) -> dict:
    """
    Update an existing To-Do item in MongoDB by matching its title.

    Args:
        title (str): The current title of the To-Do item to update.
        new_title (Optional[str]): New title for the To-Do (if provided).
        new_description (Optional[str]): New description for the To-Do (if provided).

    Returns:
        dict: {
            "success": bool,             # Whether the update was successful
            "message": str,              # A human-readable status message
            "updated_doc": dict | None   # The updated To-Do document, or None if not found
        }

    Example:
        >>> update_todo_by_title("Buy groceries", new_title="Buy fruits")
        {
            "success": True,
            "message": "To-Do updated successfully.",
            "updated_doc": {
                "id": "64f1d6a9c3f5a1f7b8123456",
                "title": "Buy fruits",
                "description": "Milk, eggs, bread"
            }
        }
    """
    try:
        db = client["todo_agent"]
        collection = db["agent"]

        update_fields = {}
        if new_title:
            update_fields["title"] = new_title
        if new_description:
            update_fields["description"] = new_description

        if not update_fields:
            return {"success": False, "message": "No fields provided to update.", "updated_doc": None}

        result = collection.update_one(
            {"title": title},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            return {"success": False, "message": f"No To-Do found with title '{title}'.", "updated_doc": None}

        # Fetch the updated document
        updated_doc = collection.find_one({"title": update_fields.get("title", title)})
        return {
            "success": True,
            "message": "To-Do updated successfully.",
            "updated_doc": {
                "id": str(updated_doc["_id"]),
                "title": updated_doc["title"],
                "description": updated_doc["description"]
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "updated_doc": None}

# ------------------------------
# Tool Function to Delete To-Do by Title
# ------------------------------
@function_tool
def delete_todo_by_title(title: str) -> dict:
    """
    Delete an existing To-Do item from MongoDB by matching its title.

    Args:
        title (str): The title of the To-Do item to delete.

    Returns:
        dict: {
            "success": bool,   # Whether the delete was successful
            "message": str     # Human-readable status message
        }

    Example:
        >>> delete_todo_by_title("Buy groceries")
        {
            "success": True,
            "message": "To-Do deleted successfully."
        }
    """
    try:
        db = client["todo_agent"]
        collection = db["agent"]

        result = collection.delete_one({"title": title})

        if result.deleted_count == 0:
            return {"success": False, "message": f"No To-Do found with title '{title}'."}

        return {"success": True, "message": "To-Do deleted successfully."}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


# ------------------------------
# Create the To-Do Agent
# ------------------------------
agent = Agent(
    name= "MongoTodoAgent",
    instructions=(
        "You are a smart To-Do assistant. "
        "You can create, update, list, and delete tasks in a MongoDB database. "
        "Always store and retrieve tasks efficiently, and respond clearly to the user."
    ),
    model=llm_model,
    tools=[create_todo , delete_todo_by_title, update_todo_by_title, fetch_todo_by_title , fetch_todos]   
)

# ------------------------------
# Run & Test the Agent
# ------------------------------

query = input("enter you query")
result = Runner.run_sync(
    agent,
    query,
      
)
print("=== Agent Output ===")
print(result.final_output)

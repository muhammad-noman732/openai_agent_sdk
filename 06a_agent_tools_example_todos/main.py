from agents import Agent ,Runner , AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ItemHelpers ,  function_tool
from pydantic import BaseModel 
from dotenv import load_dotenv
import os
from typing import Dict , Any
from datetime import datetime
import json
load_dotenv()


# Load Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

externel_client : AsyncOpenAI= AsyncOpenAI(
     api_key= GOOGLE_API_KEY,
     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
) 


llm_model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
       model="gemini-2.5-flash",
      openai_client= externel_client
)



@function_tool
def list_todos() -> str:
    """
    Return the list of todos from a JSON file.
    """
    try:
        print("Listing todos...")
        with open("./todo.json", "r") as f:
            data = json.load(f)   # <-- load JSON from file
        return data
    except FileNotFoundError:
        raise FileNotFoundError("The file todo.json was not found.")
    except Exception as e:
        raise RuntimeError(f"Error reading todos: {e}")
    

@function_tool
def add_todo(task: str = "", completed: bool = False, priority: str = "") -> Dict[str, Any]:
    """
    Add a todo to the todos.json file
    """
    try:
        print("Adding a todo...")
        # Read existing todos
        try:
            with open('./todo.json', "r") as file:
                todos = json.load(file)
        except FileNotFoundError:
            # if file not found start from empty todos
            todos = []
        except json.JSONDecodeError:
            raise ValueError("Error decoding todo.json")

        # Create new todo
        new_todo = {
            "id": len(todos) + 1,
            "task": task,
            "completed": completed,
            "priority": priority,
            "due_date": datetime.now().isoformat()
        }

        # Append to the todos
        todos.append(new_todo)

        # Save back to file
        with open('./todo.json', "w") as file:
            json.dump(todos, file, indent=2)

        return new_todo

    except Exception as e:
        raise Exception(f"Failed to add todo: {e}")
    


@function_tool
def delete_todo(id: str) -> str:
    """
    Delete a todo by its id from todo.json.
    """
    try:
        print("Deleting todo...")

        # Step 1: Read existing todos from the JSON file
        try:
            with open('./todo.json', "r") as file:
                todos = json.load(file)  # load the list of todos
        except FileNotFoundError:
            return "No todos found. The file does not exist."
        except json.JSONDecodeError:
            raise ValueError("Error decoding todo.json. The file may be corrupted.")

        # Step 2: Find and remove the todo with matching id
        todo_found = False
        for todo in todos:
            if str(todo["id"]) == str(id):  # compare IDs as strings
                todos.remove(todo)
                todo_found = True
                break  # stop loop after removing

        if not todo_found:
            return f"Todo with id {id} not found."

        # Step 3: Save updated list back to JSON file
        with open('./todo.json', "w") as file:
            json.dump(todos, file, indent=2)

        return f"Todo with id {id} deleted successfully."

    except Exception as e:
        return f"Error deleting todo: {e}"



# Pydantic model for todo update
class TodoUpdate(BaseModel):
    task: str| None = None
    completed: bool | None = None
    priority: str | None = None


# tool to update the todo
@function_tool 
def update_todo(id: str , data: TodoUpdate):
    """
       get the todo by id and data and update
    """
    try:
        print("editing todos...")
        try:
            # read the file
            with open('./todo.json' , "r") as file :
                todos = json.load(file) 
        except FileNotFoundError:
            return "No file found . File does not exists"
        except json.JSONDecodeError:
            raise ValueError ("error in decoding json.todos")
        
        # find the todo and updata 
        todo_found = False
        for todo in todos:
            if str(todo["id"]) == str(id):
                    # todo["task"]= data.get("task" , todo["task"])
                    # todo["completed"]= data.get("completed" , todo.get("completed" , False))
                    # todo["priority"]= data.get("priority" , todo.get("priority" ,""))
                    # todo["due_date"]= datetime.now().isoformat()
                
                if data.task is not None:
                      todo["task"] = data.task
                if data.completed is not None:
                       todo["completed"] = data.completed
                if data.priority is not None:
                       todo["priority"] = data.priority

                todo["due_date"] = datetime.now().isoformat()

                todo_found = True
                break # break if todo update
             
        if not todo_found :
             return f"no todo found with {id}"
  
        # Step 3: Save updated list back to JSON file
        with open('./todo.json', "w") as file:
            json.dump(todos, file, indent=2)
        
        return f"todo with {id} updated successfully"
    
    except Exception as e:
        return f"Error updating todo: {e}"
    



agent = Agent(
     name ="Todo Assistant",
    instructions = "you are todo helpful assistant , you can add , get , updata and delete todos",
    model= llm_model,
    tools= [list_todos , add_todo , delete_todo , update_todo]
)


query = input ("enter your query")

result = Runner.run_sync(
    agent,
    input=query,
   )


print(result.final_output)



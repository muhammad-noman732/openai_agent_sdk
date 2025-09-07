import os
import json
from dotenv import load_dotenv
from typing_extensions import TypedDict, Any

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    FunctionTool,
    function_tool
)

# ------------------------------
# Load API Key (Gemini via OpenAI client)
# ------------------------------
load_dotenv()
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
# File Reading Tool
# ------------------------------
@function_tool(name_override="read_data")
def read_file(ctx: RunContextWrapper[Any], path: str) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents
    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except Exception as e:
        return f"Error reading file: {e}"


# ------------------------------
# File Writing Tool
# ------------------------------
@function_tool(name_override="write_data")
def write_file(ctx: RunContextWrapper[Any], path: str, content: str) -> str:
    """Write content to a file.

    Args:
        path: The path of the file to write.
        content: The text content to write into the file.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ File '{path}' written successfully."
    except Exception as e:
        return f"Error writing file: {e}"


# ------------------------------
# Agent Setup
# ------------------------------
agent = Agent(
    name="File Assistant",
    instructions=(
        "You are a file assistant. "
        "Use 'read_data' when the user asks to read a file. "
        "Use 'write_data' when the user asks to create or update a file. "
        "Always confirm the result back to the user."
    ),
    model=llm_model,
    tools=[read_file, write_file],
)


# ------------------------------
# Run Agent
# ------------------------------
if __name__ == "__main__":
    query = input("Enter your query: ")

    result = Runner.run_sync(
        agent,
        input=query,
     )

for tool in agent.tools:
    if isinstance(tool, FunctionTool):
        print(tool.name)
        print(tool.description)
        print(json.dumps(tool.params_json_schema, indent=2))
        print()
    print("=== FINAL OUTPUT ===")
    print(result.final_output)

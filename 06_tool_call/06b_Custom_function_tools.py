import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from typing_extensions import Any
import asyncio
import httpx
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    FunctionTool,
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
# Step 1: Python function for GitHub User Info
# ------------------------------
async def get_github_user(username: str) -> str:
    """
    Get full GitHub user profile data.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.github.com/users/{username}")

        if response.status_code != 200:
            return f"Error: {response.status_code}, {response.text}"

        data = response.json()
        # Convert dict -> pretty JSON string
        return json.dumps(data, indent=2)

# ------------------------------
# Step 2: Define input validation schema
# ------------------------------
class GithubArgs(BaseModel):
    username: str

# ------------------------------
# Step 3: Tool handler
# ------------------------------
async def run_github_tool(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed = GithubArgs.model_validate_json(args)
    return await get_github_user(parsed.username)

# ------------------------------
# Step 4: Define the FunctionTool
# ------------------------------
tool = FunctionTool(
    name="get_github_user_info",
    description="Fetches full GitHub profile info for a given username",
    params_json_schema=GithubArgs.model_json_schema(),
    on_invoke_tool=run_github_tool,
)

# ------------------------------
# Step 5: Create Agent with Tool
# ------------------------------
agent = Agent(
    name="GitHubAgent",
    model=llm_model,
    tools=[tool],   # Register tool here
)



# ------------------------------
# Step 6: Run & Test
# ------------------------------
if __name__ == "__main__":
    result = Runner.run_sync(
        agent,
        input="Get details of the GitHub user 'muhammad-noman732'."
    )
    print("=== Agent Output ===")
    print(result.final_output)

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel , RunConfig
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import asyncio

# 🔑 Load API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 🔗 External client for Gemini
external_client = AsyncOpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 🎯 Choose the LLM model
llm_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client,
)

# ⚙️ Configure runner with the chosen model
config = RunConfig(
    model=llm_model,
    tracing_disabled=True,
)

"""
this is deterministic where first agent get the input generate 
output the second agent get the output of first agent as output verify
it is good or not /or return result based on the condition and then 
send this result to the third agent all the workflow done in 
Same input → same sequence of steps → same type of output
"""

# agent to create the outline of the story 
story_outline_agent = Agent(
    name="story_outline_agent",
    instructions="Generate a short outline for a story based on the user's request. "
                 "Keep it clear and simple, only 2-3 key points.",
)

# Pydantic model to validate checker output
class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_scifi: bool

# agent to check the outline
outline_checker_agent = Agent(
    name="outline_checker_agent",
    instructions=(
        "Evaluate the given story outline. "
        "Return JSON ONLY in the format: "
        '{"good_quality": true/false, "is_scifi": true/false}.'
    ),
    output_type=OutlineCheckerOutput,
)

# agent to create the final story
story_agent = Agent(
    name="story_writer_agent",
    instructions="Write a short and engaging story based on the given outline. "
                 "Keep it under 200 words.",
    output_type=str,
)

# now we run the main agent of creating the story
async def main():
    input_prompt = input("What kind of story do you want? ")

    # Run outline generator
    outline_result = await Runner.run(
        story_outline_agent,
        input_prompt,
       run_config=config
    )
    print("Outline generated:\n", outline_result.final_output)

    # Run outline checker
    outline_checker_result = await Runner.run(
        outline_checker_agent,
        outline_result.final_output,
         run_config=config
    )

    # if not outline_checker_result.final_output.good_quality:
    #     print("❌ Outline is not good quality, so we stop here.")
    #     exit(0)

    # if no t outline_checker_result.final_output.is_scifi:
    #     print("❌ Outline is not a sci-fi story, so we stop here.")
    #     exit(0)

    print("✅ Outline is good quality and sci-fi. Continuing to write the story...")

    # Run final story generator
    story_result = await Runner.run(
        story_agent,
        outline_result.final_output,
         run_config=config
    )

    print("\n📖 Final Story:\n")
    print(story_result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ItemHelpers ,  function_tool
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
import os
import random
from dotenv import load_dotenv

load_dotenv()

# Load Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

provider: AsyncOpenAI = AsyncOpenAI(
    api_key= GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

#LLM model 
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
      model="gemini-2.5-flash",
      openai_client= provider
)


config = RunConfig(
    model=llm_model,
    model_provider=provider,
    tracing_disabled=True,
)

# Define agent with explicit model
# agent = Agent(
#     name="MathAgent",
#     instructions="You are a helpful math assistant.",
#     model= llm_model 
# )

# =======================run using chainlit (history)============


# # chainlit message start
# @cl.on_chat_start
# async def handle_chat_start():
#     #  create the session for the history 
#     history = cl.user_session.set("history" , [])
#     await cl.Message(content = "Hello , I am Math Agnet , how can i help you today").send()


# # Chainlit handler

# @cl.on_message
# async def handle_message(message: cl.Message):
#     #  get the history from the session
#     history = cl.user_session.get("history")
#     # append the message of the user in the history
#     history.append({"role":"user" , "content": message.content})
#     result = await Runner.run(
#             agent,
#             # input = message.content, if no history 
#             input=history
#       )
#     #  hisroy of the agent response
#     history.append({"role":"user" , "content":result.final_output})
#     cl.user_session.set("history" , history)
#     await cl.Message(content=result.final_output).send()




# =================== run_streamed =================================

# async def main():
#      agent = Agent(
#         name="Joker",
#         instructions="You are a assistant to give jokes",
#         model= llm_model
#     )
#     #  run_streamed to get the text in streaming 
#      result = Runner.run_streamed(agent , "please tell me 5 jokes related to agentc ai")
#      async for event in result.stream_events():
#          if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#             print(event.data.delta, end="", flush=True)

# asyncio.run(main())




#  ===== tool ===
@function_tool
def how_many_jokes():
    return random.randint(1 , 10)

#  ==== stream the response with tool call ===
# async def main():
#      agent = Agent(
#         name="Joker",
#         instructions="First call the `how_many_jokes` tool, then tell that many jokes.",
#         model= llm_model,
#         tools=[how_many_jokes]
#      )

# #  using gemini as model 
#      result = Runner.run_streamed(agent , "hello" , run_config= config)
#      print("=== Run starting ===")
#      async for event in result.stream_events():
#         # We'll ignore the raw responses event deltas
#         if event.type == "raw_response_event":
#             continue
#         elif event.type == "agent_updated_stream_event":
#             print(f"Agent updated: {event.new_agent.name}")
#             continue
#         elif event.type == "run_item_stream_event":
#             if event.item.type == "tool_call_item":
#                 print("-- Tool was called")
#             elif event.item.type == "tool_call_output_item":
#                 print(f"-- Tool output: {event.item.output}")
#             elif event.item.type == "message_output_item":
#                 print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
#             else:
#                 pass  # Ignore other event types


# asyncio.run(main())


#  -------------------tools-------------------
@function_tool("get_weather")
async def get_weather (location : str)-> str:
      """ 
      fetch the weather for the given location
      """
      return f"weather in {location} is 22 degree celcius"


@function_tool("mit_programmer_finder")
async def mit_programmer_finder (number: str)-> str:
      """ 
      Find the mit_programmer based on the their number 
      """
      data ={
             1:"noman",
             2:"arslan",
             3:"ramzan",
      }
      return data.get( 1 , "Not found")


#  ==== stream the response with tool call using chainlit =======
# message at the start of tha chat
@cl.on_chat_start
async def handle_chat_start():
     #  create the session for the history 
    history = cl.user_session.set("history" , [])

    await cl.Message(content = "Hello , I am tool tool call Agnet , how can i help you today").send()

@cl.on_message
async def handle_message(message: cl.Message):
        history = cl.user_session.get("history")
        msg = cl.Message(content="")
        await msg.send()
        # user message
        history.append({"role":"user" , "content": message.content})

        agent = Agent(
        name="too calling",
        instructions="You only respond with haikus , Use get_weather tool to share the temperature of any location",
        tools=[get_weather , mit_programmer_finder],
        model= llm_model
         )
        result = Runner.run_streamed(
            agent,
            # input = message.content, if no history 
            input= history,
            run_config= config
      )
        #  now the result is in the streamed 
        async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data , ResponseTextDeltaEvent):
                        # print(event.data.delta , end = "" , flush= True)
                        await msg.stream_token(event.data.delta)
                        
                
    #  hisroy of the agent response
        history.append({"role":"assistant" , "content":result.final_output})
        cl.user_session.set("history" , history)
        



       

      

# async def main():
#     agent = Agent(
#         name="Joker",
#         instructions="You are joke assistant , get the number of jokes from tool and display that many jokes",
#         model= llm_model
#     )

   
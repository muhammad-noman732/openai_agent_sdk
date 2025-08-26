import chainlit as cl
from agents import Agent,RunConfig,  Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
import os
from dotenv import load_dotenv
import asyncio # for running asynchronous function

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')



# client set up for connecting gemini
#  LLM provider
provider: AsyncOpenAI = AsyncOpenAI(
    api_key= GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

#LLM model 
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
      model="gemini-2.5-flash",
      openai_client= provider
)


config =  RunConfig(
     model = llm_model,
     model_provider = provider,
     tracing_disabled=  True
)
 # Step 3 Running Agent Synchronously
# math_agent: Agent = Agent(
#                      name="MathAgent",
#                      instructions="You are a helpful math assistant.",
#                      model=llm_model) # gemini-2.5 as agent brain - chat completions
# query = input("Enter your query")
# result = Runner.run_sync(math_agent , query)

#  Running agent asynchronouly 
# async def main():
#      agent: Agent = Agent(
#           name = "MathAgent",
#           instructions="You are a helpful math assistant.",
#           model = llm_model
#      )

#      result = await Runner.run(agent , "what is recursion" )
#      print("\nCALLING AGENT\n")
#      print(result.final_output)


# asyncio.run(main())


#  Running agent using streaming
# async def main():
#      agent = Agent(
#           name= "Mathagent",
#           instructions= "you are helpful math assistant",
#           model = llm_model
#      )

#      result = Runner.run_streamed(agent ,"what is openai agent sdk")
#      async for e in result.stream_events():
#           print(e)
# asyncio.run(main())


#  using chainlit 
agent = Agent(
           name= "Mathagent",
           instructions= "you are helpful math assistant",
           model = llm_model
      )

# at the start of chat and creating history
@cl.on_chat_start
async def handle_chat_start():
      cl.user_session.set("history" , [])
      await cl.Message(content = "Hello , I am Math Agnet , how can i help you today").send()


#  getting response of agent in chainlit . when user send a message and response come (cl.on_message)
@cl.on_message
async def handle_message(message: cl.Message):
      history = cl.user_session.get('history')
    #   append the message in the history .this is the message which user give to the llm
      history.append({"role": "user" , "content": message.content})
      result = await Runner.run(
            agent,
            input = history,
      )
        #   append the message in the history .this is the message which llm give to the user
      history.append({"role": "assistant" , "content": result.final_output})
      cl.user_session.set("history" , history)
      await cl.Message(content = result.final_output).send()
# @cl.on_message
# async def main(message: str):
#     # Just echo the message for now
#     await cl.Message(content=f"You said: {message}").send()

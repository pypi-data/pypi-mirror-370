# flake8: noqa: E402
from llmbrix.tracing import configure_arize_tracing

configure_arize_tracing(project_name="4_tool_calling_chatbot_demo")

from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg
from llmbrix.tools import GetDatetime, ListDir

SYSTEM_MSG = "Be super brief. Use provided tools to either get current datetime or list files in dir."
HIST_LIMIT = 5
MODEL = "gpt-5-mini"

gpt = GptOpenAI(model=MODEL)
chat_history = ChatHistory(max_turns=HIST_LIMIT)
system_msg = SystemMsg(content=SYSTEM_MSG)
tools = [GetDatetime(), ListDir()]
agent = Agent(gpt=gpt, chat_history=chat_history, system_msg=system_msg, tools=tools)

while True:
    user_input = input("User input (enter 'q' to exit): ")
    if user_input.lower() in {"q"}:
        break
    user_msg = UserMsg(content=user_input)
    assistant_msg = agent.chat(user_msg)

    print(user_msg)
    print(assistant_msg)

print("Final chat history dump:")

for m in chat_history.get():
    print("\n\n")
    print(m)

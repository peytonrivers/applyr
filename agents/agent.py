from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
import operator

import os

openai_key = os.getenv("OPENAI_KEY")
llm = ChatOpenAI(model="gpt-5.4-nano", temperature = 0.7, api_key=openai_key)

@tool
def multiply(a, b):
    """multiply a time b"""
    return a * b

@tool
def divide(a, b):
    """Divide a by b"""
    return a / b

@tool
def add(a, b):
    """Add a and b"""
    return a + b

@tool
def subtract(a, b):
    """Subtract a and b"""
    return a - b

tools = [multiply, add, divide, subtract]
tool_node = ToolNode(tools)
tools_name = {tool.name: tool for tool in tools}
all_tools = llm.bind_tools(tools)

class State(TypedDict):
    first_name: str
    last_name: str
    messages: Annotated[list, add_messages]


def build_user_profile(state: State):
    first_name = input("What's your first name? ")
    last_name = input("What's your last name? ")
    state["first_name"] = first_name
    state["last_name"] = last_name
    return state

def convert_profile_context(state: State):
    text = f"User Profile:\n\tFirst Name: {state["first_name"]}\n\tLast Name: {state["last_name"]}"
    state["messages"] = [SystemMessage(content=text)]
    return state

def llm_call(state: State):
    last_message = state["messages"][-1]
    if isinstance(last_message, ToolMessage):
        response = all_tools.invoke(state["messages"])
        state["messages"].append(response)
        print(state["messages"])
        return state

    user_input = input("What is your next question or break? ")
    state["messages"].append(HumanMessage(content=user_input))
    response = all_tools.invoke(state["messages"])
    state["messages"].append(response)
    return state

def should_continue(state: State):
    last_human_message = state["messages"][-2]
    last_ai_message = state["messages"][-1]

    if last_human_message.content.lower() == "break":
        return "end"
    
    if last_ai_message.tool_calls:
        print(state["messages"])
        return "tools"

    print(last_ai_message.content)
    return "continue"



workflow = StateGraph(State)

workflow.add_node("build_user_profile", build_user_profile)
workflow.add_node("convert_profile_context", convert_profile_context)
workflow.add_node("llm_call", llm_call)
workflow.add_node("tool_node", tool_node)

workflow.add_edge(START, "build_user_profile")
workflow.add_edge("build_user_profile", "convert_profile_context")
workflow.add_edge("convert_profile_context", "llm_call")
workflow.add_conditional_edges("llm_call", should_continue, {
    "end": END,
    "tools": "tool_node",
    "continue": "llm_call"
})
workflow.add_edge("tool_node", "llm_call")

chain = workflow.compile()

chain.invoke({})
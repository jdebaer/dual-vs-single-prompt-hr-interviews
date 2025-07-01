from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import re

class ConvAgent:

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    def normalize_quotes(self, text):
        replacements = {
            "\u2018": "'",  # Left single quote (‘)
            "\u2019": "'",  # Right single quote (’), also used as an apostrophe
            "\u201C": '"',  # Left double quote (“)
            "\u201D": '"'   # Right double quote (”)
        }

        for fancy, normal in replacements.items():
            text = text.replace(fancy, normal)
    
        return text

    def __init__(self, name, system_message, model_provider, model):
        self.name = name
        self.system_message = system_message
        self.thread_id = name
        self.model_provider = model_provider
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self.model = model

        load_dotenv('./vars/.env') 

        checkpointer = MemorySaver()

        graph_builder = StateGraph(ConvAgent.State)

        if model_provider == "openai":
            print("Using openai 4o")
            self.llm = ChatOpenAI(model="gpt-4o")
        elif model_provider == "groq":
            if self.model == "versatile":
                print("Using versatile")
                self.llm = ChatGroq(model="llama-3.3-70b-versatile")
            elif self.model == "deepseek":
                print("Using deepseek")
                self.llm = ChatGroq(model="deepseek-r1-distill-llama-70b")
            else:
                print("Invalid model for groq")
                exit(-1)
        else:
            print("Unsupported model provider")
            exit(-1)

        graph_builder.add_node("llm_node", self.llm_node)
        graph_builder.set_entry_point("llm_node")
        graph_builder.set_finish_point("llm_node")
        self.graph = graph_builder.compile(checkpointer=checkpointer)

    def llm_node(self, state: State):

        messages = state["messages"]
        response = self.llm.invoke([SystemMessage(self.system_message), *messages])
        return {"messages": [response]}

    def invoke(self, user_input=None):

        if user_input != None:
            output = self.graph.invoke({"messages": [("user", user_input)]}, self.config)

        else:
            output = self.graph.invoke({"messages": []}, self.config)

        output_content = output["messages"][-1].content
        if self.model == "deepseek":
            output_content = re.sub(r"^.*?</think>", "", output_content, flags=re.DOTALL)
            output_content = re.sub(r"<think>.*?</think>", "", output_content, flags=re.DOTALL)
            output_content = re.sub(r"<think>", "", output_content, flags=re.DOTALL)

        output_content = self.normalize_quotes(output_content)

        return output_content, output["messages"][-1].response_metadata["token_usage"]["prompt_tokens"], output["messages"][-1].response_metadata["token_usage"]["completion_tokens"]


def main():
    agent = ConvAgent("agent", "You are an HR job interviewer and are interviewing a candidate to see what their past job experiences were. Start with greeting the candidate and take it from there.", "openai", None)
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if user_input.lower() in ["pass"]:
            print(agent.invoke())
        else: 
            print(agent.invoke(user_input))

if __name__ == '__main__':
    main()

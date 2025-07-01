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

class RewriteAgent:

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    def __init__(self, name):
        self.name = name
        self.thread_id = name
        self.config = {"configurable": {"thread_id": self.thread_id}}

        load_dotenv('./vars/.env') 

        checkpointer = MemorySaver()

        graph_builder = StateGraph(RewriteAgent.State)

        self.llm = ChatOpenAI(model="gpt-4-turbo")

        graph_builder.add_node("llm_node", self.llm_node)
        graph_builder.set_entry_point("llm_node")
        graph_builder.set_finish_point("llm_node")
        self.graph = graph_builder.compile(checkpointer=checkpointer)

    def llm_node(self, state: State):

        messages = state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def invoke(self, dialog=None):

        human_message1 = f"""Can you make the following dialog, which is based on written text, more real, keeping as much information as possible, but replacing complex words by simpler words, cutting long sentences up in multiple utterances, etc.\n\n{dialog}"""
        human_message2 = "Can you rewrite it more, so that the interviewer has to pull information out of the candidate - imagine the candidate is not very verbose, but the interviewer is still able to extract the same information, but in simpler words."

        output = self.graph.invoke({"messages": [("user", human_message1)]}, self.config)
        output = self.graph.invoke({"messages": [("user", human_message2)]}, self.config)
        return output["messages"][-1].content

def main():

    test_dialog = "To provide"
    agent = RewriteAgent("agent")
    print(agent.invoke(test_dialog))

if __name__ == '__main__':
    main()

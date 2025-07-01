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

class SynthAgent:

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

    def __init__(self, name, system_message, model_provider, model=None):
        self.name = name
        self.system_message = system_message
        self.thread_id = name
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self.model_provider = model_provider
        self.model = model

        load_dotenv('./vars/.env') 

        checkpointer = MemorySaver()

        graph_builder = StateGraph(SynthAgent.State)

        if self.model_provider == "openai":
            print("Using openai gpt-4o")
            self.llm = ChatOpenAI(model="gpt-4o")
        elif self.model_provider == "groq":
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
        self.graph = graph_builder.compile()

    def llm_node(self, state: State):

        messages = state["messages"]
        response = self.llm.invoke([SystemMessage(self.system_message), *messages])
        return {"messages": [response]}

    def invoke(self, seed):

        human_message_from_paper=f"""{seed}
Based on the career history above, generate an in-depth job interview between and interviewer and a candidate. 
The interviewer does not know anything about the career history or the candidate's background, but is looking for experiences that demonstrate competencies that are useful in a professional setting, by asking questions.
The interview should have about 16 conversation turns in total, so about 8 turns for each speaker.
Make sure to refer to the interviewer with "interviewer:" and to the candidate with "candidate:" and use those exact speaker labels, all lower case.
Start your output with the first speaker label, without adding things like "interview begins" or "job interview".
"""
        human_message=f"""{seed}
Based on the career history above, generate an in-depth job interview between and interviewer and a candidate. 
The speakers must pass the Turing test, which means they need to speak like human as much as possible. The conversation flow should be natural and smooth. Do not say too many words in each round. Do not talk like an AI assistant, and don't use overly long sentences.
The interviewer does not know anything about the career history or the candidate's background, but is looking for experiences that demonstrate competencies that are useful in a professional setting, by asking questions.
The interview should have about 16 conversation turns in total, so about 8 turns for each speaker.
Make sure to refer to the interviewer with "interviewer:" and to the candidate with "candidate:" and use those exact speaker labels, all lower case.
Start your output with the first speaker label, without adding things like "interview begins" or "job interview".
"""

        output = self.graph.invoke({"messages": [("user", human_message)]}, self.config)

        interview_prompt_tokens = output["messages"][-1].response_metadata["token_usage"]["prompt_tokens"]
        interview_completion_tokens = output["messages"][-1].response_metadata["token_usage"]["completion_tokens"]
        interview = output["messages"][-1].content

        interview_word_count = len(interview.split())

        if self.model == "deepseek":
            interview = re.sub(r"^.*?</think>", "", interview, flags=re.DOTALL)
            interview = re.sub(r"<think>.*?</think>", "", interview, flags=re.DOTALL)
            interview = re.sub(r"<think>", "", interview, flags=re.DOTALL)

        interviewer_lines = "\n".join(
            line for line in interview.splitlines()
            if ("interviewer" in line.strip().lower())
            )
        interviewer_word_count = sum(len(line.split()) for line in interviewer_lines.splitlines())
        interviewer_utterance_count = len(interviewer_lines.splitlines())
        interviewer_avg_word_count = interviewer_word_count / interviewer_utterance_count

        candidate_lines = "\n".join(
            line for line in interview.splitlines()
            if ("candidate" in line.strip().lower())
            )
        candidate_word_count = sum(len(line.split()) for line in candidate_lines.splitlines())
        candidate_utterance_count = len(candidate_lines.splitlines())
        candidate_avg_word_count = candidate_word_count / candidate_utterance_count

        interview_word_count = interviewer_word_count + candidate_word_count

        interviewer_avg_compl_tokens = (interviewer_avg_word_count * interview_completion_tokens) / interview_word_count
        candidate_avg_compl_tokens = (candidate_avg_word_count * interview_completion_tokens) / interview_word_count

        interview = self.normalize_quotes(interview)

        return interview, interview_prompt_tokens, interview_completion_tokens, interviewer_avg_compl_tokens, candidate_avg_compl_tokens, candidate_utterance_count + interviewer_utterance_count

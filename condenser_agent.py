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

class CondenserAgent:

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    def __init__(self, name, system_message="You are an expert summarizer.", model_provider="openai"):
        self.name = name
        self.system_message = system_message
        self.thread_id = name
        self.config = {"configurable": {"thread_id": self.thread_id}}

        load_dotenv('./vars/.env') 

        checkpointer = MemorySaver()

        graph_builder = StateGraph(CondenserAgent.State)

        if model_provider == "openai":
            self.llm = ChatOpenAI(model="gpt-4-turbo")
        elif model_provider == "groq":
            self.llm = ChatGroq(model="llama-3.3-70b-versatile")
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

    def invoke(self, career):

        human_message=f"""Generate a short summary of the following career path, highlighting the most important experiences that signal competency or growth.
Keep the language simple and the keep the telegraphic writing style, without using pronouns as "I" or "they".
Career path:
{career}
"""
        output = self.graph.invoke({"messages": [("user", human_message)]}, self.config)
        return output["messages"][-1].content

def main():

    career="""First role: HR Coordinator from November 2006 to Spring 2007.
Experiences:
Screened profiles, shortlisted candidates, coordinated recruitment process, conducted telephonic interviews, scheduled further interviews, prepared offer and appointment letters, completed joining formalities, provided induction on HR policies, and created a friendly work environment for new hires. Managed employee records, addressed staff concerns, handled HR administrative issues, managed exit formalities, and conducted performance appraisals.

Next role: Management Trainee, QA from August 2007 to December 2007.
Experiences:
Involved in the quality process of various projects according to ISO 9001:2000 standards. Monitored reports and quality objectives, conducted QMS induction for new hires, organized kick-off meetings for projects, and ensured compliance with statutory documentation requirements. Received training on Software Development Life Cycle.

Next role: HR Assistant from March 2008 to Summer 2010.
Experiences:
Sourced and shortlisted resumes from job portals, job postings, and internal data bank based on recruitment specifications. Sent screened profiles to the hiring manager, coordinated interviews, and facilitated preliminary screening of candidates. Prepared and issued offer letters, managed onboarding and induction for new hires, completed joining formalities, and prepared appointment letters and salary break-up. Assisted in designing performance appraisal forms and setting up a new appraisal system. Assisted in identifying and designing the competency framework. Conducted PMS awareness workshops and guided employees in filling out appraisal forms. Assisted in designing KRAs and ensured timely receipt of appraisal forms. Managed MIS, HRIS, and employee master records. Compiled and generated reports, prepared attrition rate details, and identified reasons for employee separation. Identified training needs, planned training programs, prepared training calendar and budget. Arranged internal and external training, maintained training records, and evaluated training effectiveness. Managed leave and attendance, prepared pay sheet, processed payroll, and updated leave balances. Tested and uploaded data into HRIS software. Maintained personal employee files and updated ISO HR dashboard. Handled employee grievances and performed exit interviews and formalities.
"""

    condenser = CondenserAgent(name="condenser")
    seed = condenser.invoke(career)
    print(seed)

if __name__ == '__main__':
    main()

from conv_agent import ConvAgent
from career_generator import CareerGenerator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from rewrite_agent import RewriteAgent
import sys
import re
import os

def generate_interview(interviewer_system_message, candidate_system_message, model_provider, model=None):

    role_string = "role"
    interviewer_string = "interviewer"
    utterance_string = "utterance"
    candidate_string = "candidate"

    interviewer = ConvAgent(
        name=interviewer_string,
        system_message=interviewer_system_message,
        model_provider=model_provider,
        model=model
    )

    candidate = ConvAgent(
        name=candidate_string,
        system_message=candidate_system_message,
        model_provider=model_provider,
        model=model
    )

    interview_acts = []

    interviewer_utterance = ""
    candidate_utterance = ""

    i = 0

    interviewer_prompt_tokens = 0
    candidate_prompt_tokens = 0

    interviewer_completion_tokens = 0
    candidate_completion_tokens = 0

    interviewer_avg_compl_tokens = 0
    candidate_avg_compl_tokens = 0

    while True:
        if i == 0:
            interviewer_utterance, prompt_tokens, completion_tokens = interviewer.invoke()
        else:
            interviewer_utterance, prompt_tokens, completion_tokens = interviewer.invoke(candidate_utterance)

        interviewer_prompt_tokens += prompt_tokens
        interviewer_completion_tokens += completion_tokens

        interview_acts.append({role_string: interviewer_string, utterance_string: interviewer_utterance})

        if "hank you for your time" in interviewer_utterance:
            
            interviewer_avg_compl_tokens = interviewer_completion_tokens / (i + 1) # The interviewer has an extra utterance which is the closing utterance
            candidate_avg_comp_tokens = candidate_completion_tokens / i 
            break

        candidate_utterance, prompt_tokens, completions_tokens = candidate.invoke(interviewer_utterance)
        #print(candidate_utterance)

        candidate_prompt_tokens += prompt_tokens
        candidate_completion_tokens += completion_tokens

        interview_acts.append({role_string: candidate_string, utterance_string: candidate_utterance})

        i += 1
        if i > 100:
            print("Conversation went rogue")
            break

    interview_prompt_tokens = interviewer_prompt_tokens + candidate_prompt_tokens
    interview_completion_tokens = interviewer_completion_tokens + candidate_completion_tokens

    for interview_act in interview_acts:
        interview_act[utterance_string] = re.sub(r'\n+', ' ', interview_act[utterance_string])

    formal_interview = """"""
    for idx, interview_act in enumerate(interview_acts):

        interview_act_role = interview_act[role_string]
        interview_act_utterance = interview_act[utterance_string]

        if idx == 0:
            interview_act_string = f"{interview_act_role}: {interview_act_utterance}"
        else:
            interview_act_string = f"\n{interview_act_role}: {interview_act_utterance}"
        formal_interview += interview_act_string

    return formal_interview, interview_prompt_tokens, interview_completion_tokens, interviewer_avg_compl_tokens, candidate_avg_comp_tokens, len(interview_acts)

def main():

    test_run = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_run = True
        else:
            record = int(sys.argv[1])
    else:
        record = None

    if test_run:
        print("Test run")
        interview_acts = test_interview_acts
    else:
        print("Not a test run")
        interview_acts = generate_interview(record)

if __name__ == '__main__':
    main()


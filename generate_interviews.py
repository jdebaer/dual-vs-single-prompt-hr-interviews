from career_generator import CareerGenerator
from interview_generator import generate_interview
from rewrite_agent import RewriteAgent
from synth_agent import SynthAgent
from rater_agent import RaterAgent
from condenser_agent import CondenserAgent
import itertools
import json
from experiment_system_prompts import candidate_system_message, interviewer_system_message
import time
import sys

if len(sys.argv) > 1:
    method_arg = sys.argv[1]
else:
    method_arg = None

batch1 = [1405, 315, 299, 923, 988, 1020, 336, 736, 1251, 1370, 355, 1287, 1082, 271, 56, 599, 717, 1232, 688, 757, 895, 1036, 18, 536, 605, 1190, 106, 1596, 838, 1634, 918, 652, 544, 871, 1083, 636, 706, 5, 1253, 95, 1147, 55, 1013, 1307, 1713, 1614, 333, 93, 1343, 1288, 906, 1658, 342, 1565, 954, 974, 893, 863, 1218, 1322, 1366, 1620, 479, 419, 209, 580, 853, 950, 1169, 696, 802, 112, 272, 1157, 105, 793, 1407, 283, 1425, 159, 1413, 1591, 532, 1140, 940, 1329, 753, 198, 965, 648, 1632, 857, 40, 103, 45, 637, 38, 156, 84, 551]

def in_batch(record):
    if record in batch1:
        return True
    else:
        return False

def add_record(file_name, record):
    with open(file_name, "a") as file:
        file.write(json.dumps(record) + "\n")

if method_arg in ["dual-openai", "all"]:
 
    print("Generating dual-openai interviews...")
    with open("seeds.jsonl", "r") as jsonl_file:
        
        for line in jsonl_file:
            record_data = json.loads(line)
            record = record_data["record"]
            if not in_batch(record):
                continue
            seed_value = record_data["seed"]
            candidate_system_message_formatted = candidate_system_message.format(seed=seed_value)        
    
            start_time = time.time()
            interview, prompt_tokens, completion_tokens, interviewer_avg_compl_tokens, candidate_avg_compl_tokens, num_utterances = generate_interview(interviewer_system_message, candidate_system_message_formatted, "openai")
            end_time = time.time()
            el_time = end_time - start_time
            print(f"dual-openai generated for {record}")
            record_data = {
              "record": record,
              "method": "dual-openai",
              "interview": interview,    
              "prompt_tokens": prompt_tokens, 
              "completion_tokens": completion_tokens, 
              "interviewer_avg_compl_tokens": interviewer_avg_compl_tokens, 
              "candidate_avg_compl_tokens": candidate_avg_compl_tokens, 
              "num_utterances": num_utterances,        
              "time": el_time
            }
            add_record("./interviews/dual_openai_interviews.jsonl",record_data)

elif method_arg in ["dual-groq-versatile", "all"]:

    print("Generating dual-groq-versatile interviews...")
    with open("seeds.jsonl", "r") as jsonl_file:
        
        for line in jsonl_file:
            record_data = json.loads(line)
            record = record_data["record"]
            if not in_batch(record):
                continue
            seed_value = record_data["seed"]
    
            candidate_system_message_formatted = candidate_system_message.format(seed=seed_value)
    
            start_time = time.time()
            interview, prompt_tokens, completion_tokens, interviewer_avg_compl_tokens, candidate_avg_compl_tokens, num_utterances = generate_interview(interviewer_system_message, candidate_system_message_formatted, "groq", "versatile")
            end_time = time.time()
            el_time = end_time - start_time
            print(f"dual-groq-versatile generated for {record}")
            record_data = {
              "record": record,
              "method": "dual-groq-versatile",
              "interview": interview,    
              "prompt_tokens": prompt_tokens, 
              "completion_tokens": completion_tokens, 
              "interviewer_avg_compl_tokens": interviewer_avg_compl_tokens, 
              "candidate_avg_compl_tokens": candidate_avg_compl_tokens, 
              "num_utterances": num_utterances,        
              "time": el_time
            }
            add_record("./interviews/dual_groq_versatile_interviews.jsonl",record_data)

elif method_arg in ["dual-groq-deepseek"]:

    print("Generating dual-groq-deepseek interviews...")
    with open("seeds.jsonl", "r") as jsonl_file:
       
        for line in jsonl_file:
            record_data = json.loads(line)
            record = record_data["record"]
            if not in_batch(record):
                continue
            seed_value = record_data["seed"]
    
            candidate_system_message_formatted = candidate_system_message.format(seed=seed_value)
    
            start_time = time.time()
            interview, prompt_tokens, completion_tokens, interviewer_avg_compl_tokens, candidate_avg_compl_tokens, num_utterances = generate_interview(interviewer_system_message, candidate_system_message_formatted, "groq", "deepseek")
            end_time = time.time()
            el_time = end_time - start_time
            print(f"dual-groq-deepseek generated for {record}")
            record_data = {
              "record": record,
              "method": "dual-groq-deepseek",
              "interview": interview,
              "prompt_tokens": prompt_tokens,
              "completion_tokens": completion_tokens,
              "interviewer_avg_compl_tokens": interviewer_avg_compl_tokens,
              "candidate_avg_compl_tokens": candidate_avg_compl_tokens,
              "num_utterances": num_utterances,
              "time": el_time
            }
            add_record("./interviews/dual_groq_deepseek_interviews.jsonl",record_data)

elif method_arg in ["single-openai", "all"]:

    openai_synther = SynthAgent(name="Synther-openai", system_message="You are a helpful dialog generating agent.", model_provider="openai")

    print("Generating single-openai interviews...")
    with open("seeds.jsonl", "r") as jsonl_file:
        
        for line in jsonl_file:
            record_data = json.loads(line)
            record = record_data["record"]
            if not in_batch(record):
                continue
            seed_value = record_data["seed"]
    
            start_time = time.time()
            interview, prompt_tokens, completion_tokens, interviewer_avg_compl_tokens, candidate_avg_compl_tokens, num_utterances  = openai_synther.invoke(seed_value)
            end_time = time.time()
            el_time = end_time - start_time
            print(f"single-openai generated for {record}")
            record_data = {
              "record": record,
              "method": "single-openai",
              "interview": interview,
              "prompt_tokens": prompt_tokens, 
              "completion_tokens": completion_tokens, 
              "interviewer_avg_compl_tokens": interviewer_avg_compl_tokens, 
              "candidate_avg_compl_tokens": candidate_avg_compl_tokens, 
              "num_utterances": num_utterances,       
              "time": el_time
            }
            add_record("./interviews/single_openai_interviews.jsonl",record_data)
    
elif method_arg in ["single-groq-versatile","all"]:

    groq_synther_versatile = SynthAgent(name="Synther-groq-versatile", system_message="You are a helpful dialog generating agent.", model_provider="groq", model="versatile")

    print("Generating single-groq-versatile interviews...")
    with open("seeds.jsonl", "r") as jsonl_file:
       
        for line in jsonl_file:
            record_data = json.loads(line)
            record = record_data["record"]
            if not in_batch(record):
                continue
            seed_value = record_data["seed"]
    
            start_time = time.time()
            interview, prompt_tokens, completion_tokens, interviewer_avg_compl_tokens, candidate_avg_compl_tokens, num_utterances  = groq_synther_versatile.invoke(seed_value)
            end_time = time.time()
            el_time = end_time - start_time
            print(f"single-groq-versatile generated for {record}")
            record_data = {
              "record": record,
              "method": "single-groq-versatile",
              "interview": interview,
              "prompt_tokens": prompt_tokens,    
              "completion_tokens": completion_tokens,    
              "interviewer_avg_compl_tokens": interviewer_avg_compl_tokens,    
              "candidate_avg_compl_tokens": candidate_avg_compl_tokens,    
              "num_utterances": num_utterances,
              "time": el_time        
            }
            add_record("./interviews/single_groq_versatile_interviews.jsonl",record_data)

elif method_arg in ["single-groq-deepseek", "all"]:

    groq_synther_deepseek = SynthAgent(name="Synther-groq-deepseek", system_message="You are a helpful dialog generating agent.", model_provider="groq", model="deepseek")

    print("Generating single-groq-deepseek interviews...")
    with open("seeds.jsonl", "r") as jsonl_file:
       
        for line in jsonl_file:
            record_data = json.loads(line)
            record = record_data["record"]
            if not in_batch(record):
                continue
            seed_value = record_data["seed"]
    
            start_time = time.time()
            interview, prompt_tokens, completion_tokens, interviewer_avg_compl_tokens, candidate_avg_compl_tokens, num_utterances  = groq_synther_deepseek.invoke(seed_value)
            end_time = time.time()
            el_time = end_time - start_time
            print(f"single-groq-deepseek generated for {record}")
            record_data = {
              "record": record,
              "method": "single-groq-deepseek",
              "interview": interview,
              "prompt_tokens": prompt_tokens,    
              "completion_tokens": completion_tokens,    
              "interviewer_avg_compl_tokens": interviewer_avg_compl_tokens,    
              "candidate_avg_compl_tokens": candidate_avg_compl_tokens,    
              "num_utterances": num_utterances,
              "time": el_time        
            }
            add_record("./interviews/single_groq_deepseek_interviews.jsonl",record_data)

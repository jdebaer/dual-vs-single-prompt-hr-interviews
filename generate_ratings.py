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

rater = RaterAgent("Rater")

records = [1405, 315, 299, 923, 988, 1020, 336, 736, 1251, 1370, 355, 1287, 1082, 271, 56, 599, 717, 1232, 688, 757, 895, 1036, 18, 536, 605, 1190, 106, 1596, 838, 1634, 918, 652, 544, 871, 1083, 636, 706, 5, 1253, 95, 1147, 55, 1013, 1307, 1713, 1614, 333, 93, 1343, 1288, 906, 1658, 342, 1565, 954, 974, 893, 863, 1218, 1322, 1366, 1620, 479, 419, 209, 580, 853, 950, 1169, 696, 802, 112, 272, 1157, 105, 793, 1407, 283, 1425, 159, 1413, 1591, 532, 1140, 940, 1329, 753, 198, 965, 648, 1632, 857, 40, 103, 45, 637, 38, 156, 84, 551]

def add_record(file_name, record):
    with open(file_name, "a") as file:
        file.write(json.dumps(record) + "\n")

def find_record_data(file_name, record):
    with open(file_name, "r") as file:
        for line in file:
            record_data = json.loads(line)
            line_record = record_data["record"]
            if record == line_record:
                return record_data

file_names = ["./interviews/dual_openai_interviews.jsonl", "./interviews/dual_groq_versatile_interviews.jsonl", "./interviews/single_openai_interviews.jsonl", "./interviews/single_groq_versatile_interviews.jsonl"]

for record in records:

    interviews = []
    for file_name in file_names:
        record_data = find_record_data(file_name, record)
        interviews.append(record_data)

    pw_comparisons = []
    combinations = list(itertools.combinations(interviews,2))
    for combination in combinations:

        comparison_type = combination[0]["method"] + "_vs_" + combination[1]["method"]

        first_utterance_dialog_0 = combination[0]["interview"].splitlines()[0]
        first_utterance_dialog_1 = combination[1]["interview"].splitlines()[0]

        print(f"Calling rater with {combination[0]['method']} and {combination[1]['method']} for {record}")
        winner_1, reason_1 = rater.invoke(combination[0]["interview"], combination[1]["interview"]) 

        if winner_1 is not None:
            if winner_1 == 0:
                winner_1 = combination[0]["method"]
            else:
                winner_1 = combination[1]["method"]
                
        else:
            winner_1 = "tie"

        print(f"Calling rater with {combination[1]['method']} and {combination[0]['method']} for {record}")
        winner_2, reason_2 = rater.invoke(combination[1]["interview"], combination[0]["interview"])

        if winner_2 is not None:
            if winner_2 == 0:
                winner_2 = combination[1]["method"]
            else:
                winner_2 = combination[0]["method"]
        else:
            winner_2 = "tie"

        winner_list = [winner_1, winner_2]
        reason_list = [reason_1, reason_2]  

        comparison = {
            "type": comparison_type,
            "winner": winner_list,
            "reason": reason_list,
            "first_line_0": first_utterance_dialog_0,
            "first_line_1": first_utterance_dialog_1
        }

        pw_comparisons.append(comparison)       

    new_record_data = {
      "record": record,
      "pw_comparisons": pw_comparisons
    }
    add_record("./ratings/ratings.jsonl",new_record_data)

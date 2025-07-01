import itertools
import json
from experiment_system_prompts import candidate_system_message, interviewer_system_message
import time

dual_openai_win_rates = []
dual_groq_versatile_win_rates = []
single_openai_win_rates = []
single_groq_versatile_win_rates = []

dual_win_rates = []
single_win_rates = []

openai_win_rates = []
groq_versatile_win_rates = []  

with open("./ratings/ratings.jsonl", "r") as jsonl_file:
    
    for line in jsonl_file:
        record_data = json.loads(line)

        pw_comparisons = record_data["pw_comparisons"]
        record = record_data["record"]

        dual_openai_wins = 0
        dual_groq_versatile_wins = 0
        single_openai_wins = 0
        single_groq_versatile_wins = 0

        dual_wins = 0
        single_wins = 0
        openai_wins = 0
        groq_versatile_wins = 0

        for pw_comparison in pw_comparisons:

            comp_type = pw_comparison["type"]
            if "groq" in comp_type:
                if "versatile" not in comp_type:
                    print("Inconsistent naming of groq")
                    exit(-1)
            winner_set = pw_comparison["winner"]

            for winner in winner_set:

                if winner != "tie":
                    if winner not in comp_type:
                        print("Winner not in comp_type")
                        exit(-1)

                match winner:
                    case "dual-openai":
                        dual_openai_wins += 1
                        if "single" in comp_type:
                            dual_wins += 1
                        if "groq-versatile" in comp_type:
                            openai_wins += 1
                    case "dual-groq-versatile":
                        dual_groq_versatile_wins += 1
                        if "single" in comp_type:
                            dual_wins += 1
                        if "openai" in comp_type:
                            groq_versatile_wins += 1
                    case "single-openai":
                        single_openai_wins += 1
                        if "dual" in comp_type:
                            single_wins += 1
                        if "groq-versatile" in comp_type:
                            openai_wins += 1
                    case "single-groq-versatile":
                        single_groq_versatile_wins += 1
                        if "dual" in comp_type:
                            single_wins += 1
                        if "openai" in comp_type:
                            groq_versatile_wins += 1
                    case "tie":
                        pass
                    case _:
                        print("Unknown winner type")
                        exit(-1)

        dual_openai_win_rate = dual_openai_wins / 6
        dual_groq_versatile_win_rate = dual_groq_versatile_wins / 6
        single_openai_win_rate = single_openai_wins / 6
        single_groq_versatile_win_rate = single_groq_versatile_wins / 6

        dual_win_rate = dual_wins / 8
        single_win_rate = single_wins / 8
        openai_win_rate = openai_wins / 8
        groq_versatile_win_rate = groq_versatile_wins / 8

        dual_openai_win_rates.append(dual_openai_win_rate)
        dual_groq_versatile_win_rates.append(dual_groq_versatile_win_rate)
        single_openai_win_rates.append(single_openai_win_rate)
        single_groq_versatile_win_rates.append(single_groq_versatile_win_rate)

        dual_win_rates.append(dual_win_rate)
        single_win_rates.append(single_win_rate)

        openai_win_rates.append(openai_win_rate)
        groq_versatile_win_rates.append(groq_versatile_win_rate)

from scipy.stats import friedmanchisquare
from scipy.stats import wilcoxon

print("Testing all models")

def calc_avg_win_rate(win_rate_list):
    return (sum(win_rate_list)/len(win_rate_list))

dual_openai_avg_win_rate = calc_avg_win_rate(dual_openai_win_rates)
dual_groq_versatile_avg_win_rate = calc_avg_win_rate(dual_groq_versatile_win_rates)
single_openai_avg_win_rate = calc_avg_win_rate(single_openai_win_rates)
single_groq_versatile_avg_win_rate = calc_avg_win_rate(single_groq_versatile_win_rates)
dual_avg_win_rate = calc_avg_win_rate(dual_win_rates)
single_avg_win_rate = calc_avg_win_rate(single_win_rates)
openai_avg_win_rate = calc_avg_win_rate(openai_win_rates)
groq_versatile_avg_win_rate = calc_avg_win_rate(groq_versatile_win_rates)

print(f"Average dual-openai win rate is {dual_openai_avg_win_rate}")
print(f"Average dual-groq-versatile win rate is {dual_groq_versatile_avg_win_rate}")
print(f"Average single-openai win rate is {single_openai_avg_win_rate}")
print(f"Average single-groq-versatile win rate is {single_groq_versatile_avg_win_rate}")
print("")
print(f"Average dual win rate is {dual_avg_win_rate}") 
print(f"Average single win rate is {single_avg_win_rate}")
print("")
print(f"Average openai win rate is {openai_avg_win_rate}")
print(f"Average groq-versatile win rate is {groq_versatile_avg_win_rate}") 
print("")

win_rate_data = [dual_openai_win_rates, dual_groq_versatile_win_rates, single_openai_win_rates, single_groq_versatile_win_rates]
stat, p_value = friedmanchisquare(*win_rate_data)
print(f"Friedman Test p-value: {p_value}")

if p_value < 0.05:
    print("Significant differences detected! Proceed to pairwise tests.")
else:
    print("No significant difference between models.")

print("")
print("Testing single vs. dual")
win_rate_data = [dual_win_rates, single_win_rates]
stat, p_value = wilcoxon(*win_rate_data)

print(f"Wilcoxon Test p-value: {p_value}")
if p_value < 0.05:
    print("Feature significantly impacts win rate.")
else:
    print("Feature does NOT significantly impact win rate.")

print("")
print("Testing openai vs. groq-versatile")
win_rate_data = [openai_win_rates, groq_versatile_win_rates]
stat, p_value = wilcoxon(*win_rate_data)

print(f"Wilcoxon Test p-value: {p_value}")
if p_value < 0.05:
    print("Feature significantly impacts win rate.")
else:
    print("Feature does NOT significantly impact win rate.")

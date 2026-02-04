import pandas as pd
import random
import json
import os

def process_csv(file_path, seed=None):

    if seed is not None:
        random.seed(seed)
    
    df = pd.read_csv(file_path)

    # 1. All indices of 'difficult'
    difficult_indices = df.loc[df["difficulty"] == "difficult", "index"].tolist()
    
    # 2. Number of 'difficult' samples
    N = len(difficult_indices)
    
    # 3. Randomly sample N from 'easy'
    easy_indices = df.loc[df["difficulty"] == "easy", "index"].tolist()
    
    return difficult_indices, N, easy_indices

def clean_indices(index_string):
    if "swebench" in index_string:
        return index_string.split("/")[-1].removesuffix(".py"), "Swebench"
    elif "classeval" in index_string:
        return index_string.split("/")[-2], "Classeval"
    elif "cruxeval" in index_string:
        return index_string.split("/")[-1].removesuffix(".py"), "cruxeval"
    elif "HumanEval" in index_string:
        return index_string.split("/")[-1].removesuffix(".py"), "HumanEval"
    elif "Avatar" in index_string:
        return index_string.split("/")[-2], "Avatar"
    else:
        return index_string.split("/")[-1].removesuffix(".py"), "Real"
    
def sample_input_output(index, dataset):
    input_ouput_root = f"../dataset/re2-bench/input-output/{dataset}"
    if dataset == "Swebench":
        modified_filename = index.split("@@")[0] + "@@" + index.split("@@")[1].rstrip(".py") + "." + index.split("@@")[2] + ".jsonl"
    elif dataset == "cruxeval":
        modified_filename = index.replace("sample", "cruxeval") + ".jsonl"
    elif dataset == "HumanEval":
        modified_filename = index + ".jsonl"
    elif dataset == "Classeval":
        modified_filename = index.split("@")[-1].replace(".", "@") + ".jsonl"
    elif dataset == "Avatar":
        modified_filename = index + ".jsonl"
    elif dataset == "Real":
        modified_filename = index + ".jsonl"
    file_path = os.path.join(input_ouput_root, modified_filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
    else:
        ## sample an input-output pair
        with open(file_path, 'r') as f:
            number_candidates = sum(1 for _ in f)
            return random.randint(0, number_candidates - 1)

def problem_caterorization(ids, benchmarks):
    problems = {}
    for i, b in zip(ids, benchmarks):
        sampled_io = sample_input_output(i, b)
        if b not in problems:
            problems[b] = []
        if sampled_io is not None:
            problems[b].append(
                {
                    "id": i,
                    "benchmark": b,
                    "input-output": sampled_io
                }
                )           
    return problems

if __name__ == "__main__":
    results = {
        "difficult": {},
        "easy": {}
    }
    
    difficult_indices, N, easy_sampled_indices = process_csv("./categorization/all_benchmarks-difficulty_0.25_0.35_0.65_0.75@6.csv", seed=6)
    
    difficult_problems_ids = [clean_indices(idx)[0] for idx in difficult_indices]
    easy_problems_ids = [clean_indices(idx)[0] for idx in easy_sampled_indices]
    
    difficult_benchmarks = [clean_indices(idx)[1] for idx in difficult_indices]
    easy_benchmarks = [clean_indices(idx)[1] for idx in easy_sampled_indices]
    

    hard_problems = problem_caterorization(difficult_problems_ids, difficult_benchmarks)
    easy_problems = problem_caterorization(easy_problems_ids, easy_benchmarks)
    
    results = {
        "difficult":{},
        "easy":{}
    }
    
    hard_samples = []
    easy_samples = []
    ## sample 93 swebench problems from hard:
    swebench_hard = random.sample(hard_problems.get("Swebench", []), 93)
    ## sample 200-93=107 from real:
    real_hard = random.sample(hard_problems.get("Real", []), 107)
    hard_samples.extend(swebench_hard)
    hard_samples.extend(real_hard)
    
    ## sample 200/6=33 swebench from easy:
    swebench_easy = random.sample(easy_problems.get("Swebench", []), 33)
    easy_samples.extend(swebench_easy)
    ## sample 33 real from easy:
    real_easy = random.sample(easy_problems.get("Real", []), 33)
    easy_samples.extend(real_easy)
    ## sample 33 cruxeval from easy:
    cruxeval_easy = random.sample(easy_problems.get("cruxeval", []), 35)
    easy_samples.extend(cruxeval_easy)
    ## sample 33 classeval from easy:
    classeval_easy = random.sample(easy_problems.get("Classeval", []), 33)
    easy_samples.extend(classeval_easy)
    ## sample 33 avatar from easy:
    avatar_easy = random.sample(easy_problems.get("Avatar", []), 33)
    easy_samples.extend(avatar_easy)
    ## sample 33 humaneval from easy:
    humaneval_easy = random.sample(easy_problems.get("HumanEval", []), 33)
    easy_samples.extend(humaneval_easy)
    
    for a in hard_samples:
        results["difficult"][a["id"]] = {
            "benchmark": a["benchmark"],
            "input-output": a["input-output"]
        }
    for b in easy_samples:
        results["easy"][b["id"]] = {
            "benchmark": b["benchmark"],
            "input-output": b["input-output"]
        }
    
    result_path = "./categorization/sampled_problems.json"
    with open(result_path, 'w') as f:
        json.dump(results, f, indent=4)
import json
import requests
import tqdm

def read_test_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取data字段中的对话数据
    dialog_data = data.get("data", [])
    return dialog_data

def score_request(data, url="http://192.168.1.66:9989/score"):
    response = requests.post(url, json=data)
    response.raise_for_status()  # 检查HTTP错误
    return response.json()


def calculate_accuracy(test_data, url):
    correct_count = 0
    process_data = []
    for item in test_data:
        process_data.append(item)
    total_count = len(process_data)
    for i, item in tqdm.tqdm(enumerate(process_data), total=len(process_data), desc="infer"):
      
        cur_prompt_info = {'prompt_mapping': [], 'prompt_acp': [], 'prompt_artificial': ""}
        # cur_prompt_info["prompt_acp"] = rq_clue_server_get_clue(item["history"][:-1], item["history"][-1])
        request_data = {
            "session_id": "",
            "promptInfo": cur_prompt_info,
            "history": item["history"],
            "candidates": item["candidates"],
            "domain": item["domain"]
        }
        response = score_request(request_data, url)
        scores = response.get("response", {})
     
        max_score_key = max(scores.items(), key=lambda x: x[1])[0]
        human_preference = item.get("human_preference", "")
        dialog_id = item.get("dialog_id")
        if max_score_key == human_preference:
            correct_count += 1
        else:
            print(f"预测错误{dialog_id} ,")
            print(response)
            print(f"human_preference: {human_preference}")
            print(f"Predicted: {max_score_key}")
            print()
    accuracy = correct_count / total_count if total_count > 0 else 0
    return accuracy


if __name__ == "__main__":
    test_file_path = "./datasets/test_data/知识库_0403.json"  
    scoring_url = "http://192.168.1.66:9988/score"
    test_data = read_test_file(test_file_path)
    test_data = test_data
    accuracy = calculate_accuracy(test_data, scoring_url)
    print(f"Accuracy: {accuracy:.2%}")

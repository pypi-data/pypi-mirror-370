import json
from typing import Optional, List, Dict
from pathlib import Path
import json
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import random
import os
import ast
import re
from datetime import datetime


def read_action_file(file_path: Optional[Path]):
    """
        读取 action 文件
    """
    with open(file_path, "r", encoding="utf-8") as f:
         data = json.load(f)
    return data


def read_jsonl_from_path(file_path: Optional[Path]):
    """
        读取jsonl文件
    """
    init_data = []
    with open(file_path, "r") as f:
        for line in f.readlines():
            line = json.loads(line)
            init_data.append(line)
    return init_data


def save_jsonl_from_data(save_data: Optional[List[Dict]], 
                         save_file_path: Optional[List]):
    """
         保存jsonl文件
    """
    with open(save_file_path, "w", encoding="utf-8") as f:
        for line in save_data:
            f.write(json.dumps(line, ensure_ascii=False)+"\n")



def split_train_test(file_path:Optional[Path], 
                     save_path: Optional[Path], 
                     train_data_size:Optional[float]=0.99):
    """
        划分 sft数据或者 偏好数据，到 trl,或者 verl 可训练的格式
    
    """
    init_data = read_jsonl_from_path(file_path)
    random.shuffle(init_data)
    train_data, test_data = init_data[:int(train_data_size*len(init_data))], init_data[int(train_data_size*len(init_data)):]

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    with open(os.path.join(save_path, "train.jsonl"), "w") as f:
        for line in train_data:
            f.write(json.dumps(line,ensure_ascii=False)+"\n")
    df = pd.read_json(os.path.join(save_path, "train.jsonl"), lines=True)
    df.to_parquet(os.path.join(save_path, "train.parquet"), engine='pyarrow')

    with open(os.path.join(save_path, "test.jsonl"), "w") as f:
        for line in test_data:
            f.write(json.dumps(line,ensure_ascii=False)+"\n")
    df = pd.read_json(os.path.join(save_path, "test.jsonl"), lines=True)
    df.to_parquet(os.path.join(save_path, "test.parquet"), engine='pyarrow')



def parse_zj_log_file(log_file_path: Optional[Path] = None) -> Optional[List[Dict]]:
    """
        解析振杰的日志文件，到jsonl文件保留
    """
    res_data = []
    with open(log_file_path, "r", encoding="utf-8") as f:
        file_lines = f.readlines()
        i = 0
        topic = None
        while i < len(file_lines):
            try:
                cur_line = file_lines[i]
                # 初始化变量
                # 提取 session_id
                if "AI_warmupWord" in cur_line:
                    topic = None
                if "session_id:" in cur_line:
                    session_id = cur_line.split("session_id:")[1].strip()
                # ast将json改为字典
                if "prompt_info:" in cur_line:
                    prompt_info = ast.literal_eval(cur_line.split("prompt_info:")[1].strip())
                if "topic_dict" in cur_line:
                    topic = cur_line.split("topic_dict:")[1].strip()
                # 提取 qwen_format_history
                if "messages" in cur_line:
                    format_his = cur_line.split("messages")[1]
                    format_his = format_his.replace("\nclue:", "").replace("\n clue:", "").replace("clue:", "")
                    history = ast.literal_eval('{"messages'+format_his)
                    # 检查下列的候选句子
                    while i < len(file_lines) and "生成的第" not in file_lines[i]:
                        i += 1
                    candidates = []
                    while "生成的第" in file_lines[i]:
                        candidates.append(file_lines[i].split("句话:")[1].strip("\n").lstrip("   &nbsp;你好有什么问题请讲 <span>我</span>在线给你解答<sep>"))
                        i += 1
                    # search_text = history["messages"][0]["content"].split("\n")[1].replace("搜索词:", "")
                    # history["messages"][0]["content"] +=  f"您好家长，您是想咨询关于'{search_text}'的问题吗? 现在是什么情况？可以大概描述一下，这边好帮你分析"
                    # 如果 session_id 不是 123，则将数据添加到结果中
                    if session_id and "GPT"  in session_id:
                        res_data.append({
                            "session_id": session_id,
                            "messages": history["messages"],
                            "prompt_info": prompt_info,
                            "topic": topic,
                            "candidates": candidates
                        })
                i += 1
            except:
                i += 1
                continue
    # random.shuffle(res_data)
    print(f"文件: {log_file_path} 解析了 {len(res_data)} 条数据")
    return res_data



def parse_zj_log_file_and_count_time(log_file_path: Optional[Path] = None) -> Optional[List[Dict]]:
    """
        从日志文件中， 解析模型实际的生成时间和运行时间
    """
    timestamp_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})"
    res_data = []
    user_utterance_time = None
    first_response_time = None
    with open(log_file_path, "r", encoding="utf-8") as f:
        file_lines = f.readlines()
        i = 0
        
        while i < len(file_lines):
            cur_line = file_lines[i]
            # 初始化变量
            # 提取 session_id
            if "session_id:" in cur_line:
                session_id = cur_line.split("session_id:")[1].strip()
            if "user utterance:" in cur_line:
                match = re.search(timestamp_pattern, cur_line)
                if match:
                    user_utterance_time = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f")
            if "生成的第1句话:" in cur_line:
                match = re.search(timestamp_pattern, cur_line)
                if match:
                    first_response_time = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f")

            if user_utterance_time is not None and first_response_time is not None:
                delta_seconds = (first_response_time - user_utterance_time).total_seconds()
                res_data.append(delta_seconds)
                user_utterance_time = None
                first_response_time = None

            i += 1
    print(len(res_data))
    print(sum(res_data)/len(res_data))
    return res_data


def check_content_fields(file_path):
    """
        检查 sft数据是否符合标准
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"[行 {line_num + 1}] JSON 解码失败")
                continue

            if "messages" not in data:
                print(f"[行 {line_num + 1}] 缺少 messages 字段")
                continue

            messages = data["messages"]
            if not isinstance(messages, list):
                print(f"[行 {line_num + 1}] messages 不是列表")
                continue

            for msg_idx, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    print(f"[行 {line_num + 1}, 消息 {msg_idx}] 消息不是字典")
                    continue

                if "content" not in msg:
                    print(f"[行 {line_num + 1}, 消息 {msg_idx}] 缺少 content 字段")
                    continue

                content = msg["content"]
                if not isinstance(content, str):
                    print(f"[行 {line_num + 1}, 消息 {msg_idx}] content 类型错误: {type(content)}")

    print("✅ 检查完成")

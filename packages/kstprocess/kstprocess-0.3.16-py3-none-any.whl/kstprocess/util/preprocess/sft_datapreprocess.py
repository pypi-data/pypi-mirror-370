import json
import re
from tqdm import tqdm
import requests
from typing import Optional, List, Dict
from pathlib import Path
from openai import OpenAI
#### 模型调用逻辑 ####
import os
import json
import ast
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from kstprocess.util.format_convert import clean_zb_quote, convert_zb_to_qwen


class DataPreprocess(object):
    def __init__(self):
        self.action_map = {}
        self.reverse_action_map = {}
        for main_label, sub_labels in self.action_map.items():
            for sub_label in sub_labels:
                self.reverse_action_map[sub_label] = main_label

    def extract_action_tags(self, text):
        """提取括号中的多个 action 标签，支持格式如 (标签1、标签2)"""
        match = re.search(r'\(.*?\)', text)  # 匹配括号中的内容，并不包括括号本身
        if match:
            tags_str = match.group(0).strip()
            # 使用 “、” 或 “,” 分割多个标签
            tags = [tag.lstrip("(").rstrip(")") for tag in re.split(r'[、，]', tags_str)]
            return tags
        return []

    def is_diagnosis_or_taodian(self, action_tags):
        """
        判断一组 action 标签中是否包含“问诊”或“套电”
        :param action_tags: list of str
        :return: (is_diagnosis: bool, is_taodian: bool)
        """
        is_diagnosis = False
        is_taodian = False

        for tag in action_tags:
            main_label = self.reverse_action_map.get(tag, None)
            if main_label == "问诊":
                is_diagnosis = True
            elif main_label == "套电":
                is_taodian = True
        return is_diagnosis, is_taodian

    def is_user_leave_contact(self, text):
        """检测用户是否留联"""
        phone_like = bool(re.search(r'\b\d{6,}\b', text))
        contact_keywords = ['电话', '号码', '微信', '手机']
        return phone_like or any(kw in text for kw in contact_keywords)

    def process_conversation(self, messages):
        """处理单条会话数据"""
        rounds = []
        i = 0
        while i < len(messages):
            if messages[i]['role'] == 'user':
                user_msg = messages[i]
                if i + 1 < len(messages) and messages[i + 1]['role'] == 'assistant':
                    assistant_msg = messages[i + 1]
                    rounds.append((user_msg, assistant_msg))
                    i += 2
                else:
                    rounds.append((user_msg, None))
                    i += 1
            else:
                i += 1

        results = []
        user_phone = None

        for idx, (user_turn, assistant_turn) in enumerate(rounds):
            if idx < 1: 
                continue

            if user_phone is None and user_turn:
                user_text = user_turn.get("content", "")
                if self.is_user_leave_contact(user_text):
                    user_phone = user_text
                    continue  # 后续不处理了
            if user_phone is not None:
                result = {
                "round": idx + 1,
                "assistant_action": None,
                "is_diagnosis": None,
                "is_taodian": None,
                "get_phone": True,
                }
                results.append(result)
                continue  # 已留联，后续不处理
            if assistant_turn is None:
                continue
            assistant_content = assistant_turn.get("content", "")
            action_tag = self.extract_action_tags(assistant_content)

            is_diagnosis, is_taodian = self.is_diagnosis_or_taodian(action_tag)

            result = {
                "round": idx + 1,
                "assistant_action": action_tag,
                "is_diagnosis": is_diagnosis,
                "is_taodian": is_taodian,
                "get_phone": False,
            }
            results.append(result)

        return results

    def get_topic(self, utterance, topic_model_url):
        if utterance == "":
            utterance = "  "
        res= requests.get(f"{topic_model_url}?utterance={utterance}")
        return json.loads(res.text)["data"]["item"]

    def read_jsonl_file(self, 
                        file_path,
                        turn_num=6,
                        need_topic_list=[],
                        ignore_count=5,
                        topic_model_url="http://10.14.250.11:30374/paediatrics_topic"
                        ):
        """读取并处理整个 JSONL 文件，仅保留符合规则的对话"""
        results = []
        init_data_size = 0
        filtered_data_size = 0
        with open(file_path, "r", encoding="utf-8") as f:
            init_data = f.readlines()
            for line_idx, line in tqdm(enumerate(init_data), total=len(init_data), desc="infer"):
                try:
                    data = json.loads(line.strip())
                    if "messages" in data.keys():
                        conversation_result = self.process_conversation(data["messages"])
                    else:
                        data = convert_zb_to_qwen(data)
                        conversation_result = self.process_conversation(data["messages"])
                    # 初始化标志位
                    valid_conversation = True
                    count = 0 
                    ac_dialog_flag = False
                    for round_result in conversation_result:
                        if not (round_result["is_diagnosis"] or round_result["is_taodian"]):
                            valid_conversation = False
                            count += 1
                        if round_result["get_phone"]:
                            ac_dialog_flag = True

                    if ac_dialog_flag and count < ignore_count:
                        valid_conversation = True
                    
                    ## 判断轮次有没有大于5的 ## 
                    if conversation_result and conversation_result[-1]["round"] < turn_num:
                        valid_conversation = False

                    if valid_conversation:
                        ## 只有 topic_list 指定的时候，才会请求主题
                        if need_topic_list:
                            ### 这边 拿搜索词进行判断，如果搜索词 不存在，用第一轮访客开口句子
                            dialog_text = data["messages"][0]["content"]
                            if len(dialog_text) <3:
                                dialog_text = data["messages"][2]["content"]
                            messages_topic = self.get_topic(str(dialog_text), topic_model_url)
                            if messages_topic not in need_topic_list:
                                continue

                    for i in range(len(data["messages"])):
                        if data["messages"][i]["role"]:
                            data["messages"][i]["content"] = clean_zb_quote(data["messages"][i]["content"])
                    if valid_conversation:
                        results.append({
                            "messages": data["messages"],   
                        })
                        filtered_data_size += 1
                    init_data_size += 1

                except Exception as e:
                    print(f"解析第 {line_idx + 1} 行失败: {e}")

        print(f"原始数据长度: {init_data_size}")
        print(f"对话结构规则过滤之后长度: {filtered_data_size}")
        return results

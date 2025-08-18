from pathlib import Path
from typing import Optional, List, Dict, Union
import requests
import json
import random


def convert_general_to_dialogue_str(dialog_record, user_utterance):
    """
        对话历史添加轮次信息
        dialogure example：
            [
                {'role': 'CLIENT', 'sentence': '搜索词:厌学情绪严重不想去学校怎么办'}, 
                {'role': 'SERVER', 'sentence': '引导语:现在是什么情况？可以大概描述一下，这边好帮你分析<sep>孩子现在多大了？男孩女孩？<sep>这些症状出现多长时间了呢？<sep>你好，能看到我的消息吗？'}, 
                {'role': 'CLIENT', 'sentence': '访客问题:14周岁 女孩 两年多'}, 
                {'role': 'SERVER', 'sentence': '那在这两年里，孩子是否因为学习压力、人际关系或个人兴趣等方面感到困扰？'}, 
                {'role': 'CLIENT', 'sentence': '访客问题:都有'}, 
                {'role': 'SERVER', 'sentence': '对于学习任务和社交活动，她是否有表现出抵触或者逃避的态度？<sep>在日常生活中，有没有发现她的情绪变化较大，比如易怒、闷闷不乐等？<sep>您好，还在吗？<sep>您微信多少，我加您，我朋友圈有很多案例可以发给你参考下，这样你了解的也更清楚一些，或者您也可以加我微信：17752993722'}
                ]
        utterance example：
            访客问题:跟陌生人说话很害怕 心里很紧张 不知道说什么 一想到要去上学就想哭 特别不想去 现在暑假过去快一个月 一想到还有一个月就开学就哭
    """
    new_dialog_str = ""
    for i, line in enumerate(dialog_record):
        if i == 0:
            new_dialog_str += f"访客搜索词:{line['sentence']}\n"    
        elif line["role"] == "CLIENT":
            new_dialog_str += f"(round {(i+1)//2})user:{line['sentence']}\n"
        else:
            new_dialog_str += f"(round {(i+1)//2})assistant:{line['sentence']}\n"
    new_dialog_str += f"(round {(len(dialog_record)+1)//2})user:{user_utterance}"
    return new_dialog_str


class NativeChatLLMServer(object):
    def __init__(self, dialogue_model_path) -> None:
        self.dialogue_model_url = dialogue_model_path
    
    def post_server_url_test(self,
                             dialogrecord: Optional[List], 
                             dialogId: Optional[str],
                             keyword: Optional[str],
                             utterance: Optional[str],
                             promptInfo: Optional[Dict],
                             topic: Optional[str], 
                             limit: Optional[int]):
        post_data = {
            "robotId": "0000",
            "dialogId": dialogId,
            "keyword":keyword,
            "utterance": utterance,
            "faqAnswers": {},
            "dialogRecord": dialogrecord,
            "promptInfo": promptInfo,
            "limit": limit,
            "task_type": "dialog",
            "topic": topic
        }
        response = requests.post(self.dialogue_model_url, json=post_data)
        generate_text_list = json.loads(response.text)["data"]
        return generate_text_list
    


def get_random_chosen_rejected_pair(score_dict: dict, threshold: int = 2) -> dict:
    if not score_dict or len(score_dict) < 1:
        return None
    highest_score = max(score_dict.values())
    lowest_score = min(score_dict.values())
    if highest_score - lowest_score < threshold:
        return None
    chosen_candidates = [s for s, sc in score_dict.items() if sc == highest_score]
    rejected_candidates = [s for s, sc in score_dict.items() if sc == lowest_score]
    chosen = random.choice(chosen_candidates)
    rejected = random.choice(rejected_candidates)
    return {
        "chosen": chosen,
        "rejected": rejected,
        "chosen_score": highest_score,
        "rejected_score": lowest_score
    }
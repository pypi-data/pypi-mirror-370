import requests
import random
import pandas as pd
import time
from typing import List, Optional, Dict
import json


#### 设置搜索词 ####
class SearchText:
    def __init__(self, config) -> None:
        self.config = config

    def set_common_search_text(self) -> List[str]:
        random.seed(time.time())
        if "xlsx" in self.config["search_text_file_path"]:
            search_text_data = pd.read_excel(self.config["search_text_file_path"], sheet_name=self.config["domain_tag"])
        else:
            search_text_data = pd.read_csv(self.config["search_text_file_path"])
        need_process_search_text = search_text_data["sentence"].tolist()
        if int(self.config["search_text_num"]) > len(need_process_search_text):
            k = len(need_process_search_text)
        else:
            k = int(self.config["search_text_num"])
        need_process_search_text = random.choices(need_process_search_text, k=k)
        return need_process_search_text
    

### 客服模型 ###
class DialogueServer:
    def __init__(self, config) -> None:
        self.dialogue_model_url = config["dialogue_model_path"]
    
    def post_server_url_test(self,
                             dialogrecord: Optional[List], 
                             dialogId: Optional[str],
                             keyword: Optional[str],
                             utterance: Optional[str],
                             promptInfo: Optional[Dict], 
                             limit: Optional[int]):
        post_data = {
            "dialogId": dialogId,
            "keyword":keyword,
            "utterance": utterance,
            "faqAnswers": {},
            "dialogRecord": dialogrecord,
            "promptInfo": promptInfo,
            "limit": limit,
            "task_type": "dialog"
        }
        response = requests.post(self.dialogue_model_url, json=post_data)
        generate_text_list = json.loads(response.text)["data"]
        basic_action_label_list = json.loads(response.text)["action"]
        return generate_text_list, basic_action_label_list


## 转换对话格式
def convert_general_to_dialogue_str(dialog_record, user_utterance):
    new_dialog_str = ""
    for i, line in enumerate(dialog_record):
        if i == 0:
            new_dialog_str += f"{line['sentence']}\n"    
        elif i == 1:
            new_dialog_str += f"{line['sentence']}\n"
        elif line["role"] == "CLIENT":
            new_dialog_str += f"(round {(i)//2})user:{line['sentence']}\n"
        else:
            new_dialog_str += f"(round {(i)//2})assistant:{line['sentence']}\n"
    # new_dialog_str += f"(round {(len(dialog_record)+1)//2})user:{user_utterance}"
    return new_dialog_str


def filter_unexpect_words_sentences(unexpect_words_list:Optional[List[str]], 
                                    input_list: Optional[List[str]]) -> Optional[List[str]]:
    """
    过滤敏感词句子
    :param input_list: 输入列表，每个元素是由 <sep> 连接的句子
    :return: 过滤后的列表，如果某个句子被完全过滤掉，则不添加到结果中
    """
    if input_list is None:
        return None

    filtered_list = []
    for sentences in input_list:
        sentence_list = sentences.split('<sep>')
        filtered_sentences = [sentence for sentence in sentence_list if not any(word in sentence for word in unexpect_words_list)]
        # 如果过滤后的句子列表不为空，则拼接并添加到结果中
        if filtered_sentences:
            filtered_sentences_joined = '<sep>'.join(filtered_sentences)
            filtered_list.append(filtered_sentences_joined)
    return filtered_list
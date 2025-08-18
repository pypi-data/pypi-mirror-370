from typing import Union, List, Dict, Optional
from ltp import StnSplit
import json
from tqdm import tqdm
import requests


class ActionProcessor:
    def __init__(
        self,
        action_model_url: str=None,
        action_map: Dict[str, List[str]]=None,
        domain:str=None
    ) -> None:
        """
        初始化一个用于识别对话行为（action）的处理器
        
        Args:
            action_model_url (str): 动作识别模型的服务地址
            action_map (Dict[str, List[str]]): 行为标签映射表，例如 {"套电": ["要联系方式", "留联"], ...}
        """
        self.sentence_split_model = StnSplit()
        self.action_model_url = action_model_url
        self.action_map = action_map
        self.domain = domain

    def get_key_tag(self, value: str) -> Optional[str]:
        """
        根据具体行为值查找其所属的行为类别 key
        
        Args:
            value (str): 行为值，如 "要联系方式"
        
        Returns:
            Optional[str]: 匹配到的 key，如 "套电"；未找到返回 None
        """
        for k, v in self.action_map.items():
            if value in v:
                return k
        return ''

    def get_action_batch(self, utterance: str) -> List[List[str]]:
        """
        向行为识别服务发送请求，获取每句话对应的意图标签列表
        
        Args:
            utterance (str): 多句话用 \t 分隔的文本输入
        
        Returns:
            List[List[str]]: 每句话对应的动作标签嵌套列表
        """
        content = {
            "utterance": utterance,
            "model_name": self.domain,
            "use_batch": "True"
        }
        res = requests.post(self.action_model_url, json=content)
        return json.loads(res.text)["data"]["intent"]

    def count_response_action_label_num(
        self, response_text: Union[str, List[str]]
    ) -> Union[Dict, List[Dict]]:
        """
        统计给定文本中每个句子或整个回复中的各类行为数量
        
        Args:
            response_text (Union[str, List[str]]): 待分析的响应文本或文本列表
        
        Returns:
            Union[Dict, List[Dict]]: 包含原始文本、行为统计和分句行为的结果字典或列表
        """
        if isinstance(response_text, list):
            # 文本预处理：去除换行符
            response_text = [t.replace("\n", "") for t in response_text]
            all_sentences = []
            for text in response_text:
                sentences = self.sentence_split_model.split(text)
                all_sentences.extend(sentences)
            utterance = "\t".join(all_sentences)
            nested_list = self.get_action_batch(utterance)

            action_results = []
            start_idx = 0
            for text in response_text:
                sentences = self.sentence_split_model.split(text)
                num_sentences = len(sentences)
                end_idx = start_idx + num_sentences
                sentence_actions = nested_list[start_idx:end_idx]
                sentence_flat_actions = [item for sent_ac in sentence_actions for item in sent_ac]
                action_results.append({
                    "text": sentences,
                    "action_list": sentence_flat_actions,
                    "sentence_actions": sentence_actions,
                })
                start_idx = end_idx

            """
            example:
            {
                'text': ['理解您的心情，面对即将重返校园，确实会让人感到焦虑。', '<sep>请问平时在学校是否有被欺负的情况，或是与同学之间有矛盾？'], 
                'action_list': ['辅助推动话术', '疾病相关问诊', '问症状'], 
                'sentence_actions': [['辅助推动话术'], ['疾病相关问诊', '问症状']]
            }
            """

            result_list = []
            for result in action_results:
                action_counts = {
                    key: sum(1 for item in result["action_list"] if item in labels)
                    for key, labels in self.action_map.items()
                }
                result_list.append({
                    "text": result["text"],
                    "action_counts": action_counts,
                    "sentence_actions": result["sentence_actions"],
                })
            """
            example

            {
                'text': ['理解您的心情，面对即将重返校园，确实会让人感到焦虑。', '<sep>请问平时在学校是否有被欺负的情况，或是与同学之间有矛盾？'], 
                'action_counts': {'套电': 0, '邀约': 0, '无': 0, '衔接': 0, '拒诊': 0, '确认': 0, '暖场': 0, '问诊': 2, '答疑': 1}, 
                'sentence_actions': [['辅助推动话术'], ['疾病相关问诊', '问症状']]
            }
            
            """
            

            return result_list

        else:
            # 文本预处理
            response_text = response_text.replace("\t", "   ").replace(" ", "  ").replace("\n", "  ")
            response_text_list = self.sentence_split_model.split(response_text)
            response_text_processed = []
            for text in response_text_list:
                if "<sep>" in text:
                    response_text_processed.extend(text.split("<sep>"))
                else:
                    response_text_processed.append(text)
            utterance = "\t".join(response_text_processed)
            nested_list = self.get_action_batch(utterance)
            flat_list = [item for sublist in nested_list for item in sublist]
            action_counts = {
                key: sum(1 for item in flat_list if item in labels)
                for key, labels in self.action_map.items()
            }
            return {
                "text": response_text_processed,
                "action_counts": action_counts,
                "actions": flat_list
            }

    def clean_data_by_action_and_server_round(
        self, init_data: List[Dict]
    ) -> List[Dict]:
        """
        清洗数据：前8轮中如果包含“套电”行为则过滤
        
        Args:
            init_data (List[Dict]): 原始数据列表
        
        Returns:
            List[Dict]: 过滤后的数据
        """
        end_data = []
        for i, line in enumerate(tqdm(init_data, total=len(init_data), desc="infer")):
            if i < 8:
                chosen_content = line["chosen"][-1]["content"]
                action_counts = self.count_response_action_label_num(chosen_content)["action_counts"]
                if action_counts.get("套电", 0) > 0:
                    continue
            end_data.append(line)
        print(f"{len(init_data)}-->{len(end_data)}")
        return end_data

    def process_by_action(
        self, init_data: List[Dict], server_round: Optional[int] = None
    ) -> List[Dict]:
        """
        根据行为标签筛选高质量样本，支持 SFT / Preference / List 三种格式
        
        Args:
            init_data (List[Dict]): 原始数据列表
            server_round (Optional[int]): 当前服务器交互轮次，用于判断时机合理性
        
        Returns:
            List[Dict]: 筛选后的高质量数据
        """

        def return_hard_type_reward(
            sent_action_counts: Dict[str, int],
            sent_action: List[List[str]],
            round_num: Optional[int] = None
        ) -> bool:
            """
            判断是否符合高质量样本标准
            
            Args:
                sent_action_counts (Dict[str, int]): 行为计数
                sent_action (List[List[str]]): 分句行为列表
                round_num (Optional[int]): 当前对话轮次
            
            Returns:
                bool: 是否保留该样本

            example：
            'sent_action_counts': {'套电': 0,
            '邀约': 0,
            '无': 0,
            '衔接': 0,
            '拒诊': 0,
            '确认': 0,
            '暖场': 0,
            '问诊': 2,
            '答疑': 1},
            'sent_action': [['辅助推动话术'], ['疾病相关问诊', '问症状']]},
            """
            if round_num is None:
                round_num = 1
            flat_action_list = list(set([item for sublist in sent_action for item in sublist]))

            """
            若 “问诊 + 确认” 次数在 1-2 次之间，且无 “套电” 行为，允许保留；
            若有 “套电” 行为且对话轮次≤3，直接剔除；
            若 “套电” 行为包含 “要联系方式”“主动留联” 等，且无 “问诊”，可保留；
            若同时存在 “问诊” 和 “套电”，剔除；
            若只有 “答疑” 无其他行为，剔除；
            若包含 “拒诊” 行为，剔除；
            其他情况默认剔除。
            """
            # 条件判断逻辑略去简化版，请保留原逻辑不变
            if ((sent_action_counts["问诊"] + sent_action_counts["确认"]) <= 2 and 
                (sent_action_counts["问诊"] + sent_action_counts["确认"]) > 0) and \
               sent_action_counts["套电"] == 0 and sent_action_counts["答疑"] >= 0 and \
               sent_action_counts["衔接"] >= 0:
                return True
            elif sent_action_counts["套电"] and round_num <= 3:
                return False
            elif sent_action_counts["问诊"] == 0 and sent_action_counts["答疑"] >= 0 and \
                 sent_action_counts["套电"] > 0:
                if "要联系方式" in flat_action_list or "主动留联" in flat_action_list or "要微信" in flat_action_list:
                    return True
            elif sent_action_counts["问诊"] > 0 and sent_action_counts["套电"] > 0 and \
                 sent_action_counts["答疑"] >= 0:
                return False
            elif sent_action_counts["问诊"] == 0 and sent_action_counts["套电"] == 0 and \
                 sent_action_counts["答疑"] > 0:
                return False
            elif sent_action_counts["拒诊"] >= 0:
                return False
            else:
                return False

        data_type = ""
        if isinstance(init_data[0], dict) and "messages" in init_data[0].keys():
            data_type = "sft"
        elif isinstance(init_data[0], dict) and "chosen" in init_data[0].keys():
            data_type = "preference"
        elif isinstance(init_data[0], str):
            data_type = "list"

        save_data = []

        if data_type == "sft":
            for line in tqdm(init_data, total=len(init_data), desc="infer"):
                msg = line["messages"]
                if "咨询" in msg[0]["content"]:
                    new_msg = msg[1:]
                else:
                    new_msg = msg[2:]
                assistant_utterance_content = []
                server_round_estimated_list = []
                for i, item in enumerate(new_msg):
                    if (i % 2 == 1) and ("prompt" in item["content"]):
                        assistant_utterance_content.append(item["content"].split("prompt")[1])
                    elif (i % 2 == 1):
                        assistant_utterance_content.append(item["content"])
                        server_round_estimated_list.append(i % 2 + 1)
                results = self.count_response_action_label_num(assistant_utterance_content)
                is_use = all([
                    return_hard_type_reward(res["action_counts"], res["sentence_actions"], server_round_estimated_list[k])
                    for k, res in enumerate(results)
                ])
                if is_use:
                    save_data.append(line)

        elif data_type == "preference":
            batch_size = 8
            for start_idx in tqdm(range(0, len(init_data), batch_size), desc="infer"):
                batch = init_data[start_idx:start_idx + batch_size]
                batch_server_round_estimated_list = []
                assistant_utterance_contents = []

                for line in batch:
                    msg = line["chosen"]
                    if "咨询" in msg[0]["content"]:
                        new_msg = msg[1:]
                    else:
                        new_msg = msg[2:]
                    assistant_utterance_contents.append(line["chosen"][-1]["content"])
                    batch_server_round_estimated_list.append(len(new_msg) % 2 + 1)

                results_batch = self.count_response_action_label_num(assistant_utterance_contents)

                for idx, (line, server_round_estimated) in enumerate(zip(batch, batch_server_round_estimated_list)):
                    results = results_batch[idx]
                    is_use = return_hard_type_reward(results["action_counts"], results["sentence_actions"], server_round_estimated)
                    if is_use:
                        save_data.append(line)

        elif data_type == "list":
            results = self.count_response_action_label_num(init_data)
            save_data = [
                init_data[i] for i, res in enumerate(results)
                if return_hard_type_reward(res["action_counts"], res["sentence_actions"], server_round)
            ]

        print(f"{len(init_data)}->{len(save_data)}")
        return save_data
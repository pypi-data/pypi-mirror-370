"""
  对话机器人后处理
    action 处理函数
    rule 处理函数

"""


from typing import Optional, Dict, List
import requests
import json
import configparser
from typing import Union
from typing import Optional, Dict, List
import re
from ltp import StnSplit



class ActionProcessor(object):
    def __init__(self) -> None:
        self.sentence_split_model = StnSplit()
        self.config = configparser.ConfigParser()
        self.config.read('./config/sever.ini')
        self.domain = self.config["other"]["action_model_url_domain"]
        with open(self.config["other"]["action_map_file_path"]) as f:
            self.action_map = json.load(f)

    def get_group_action(self, action_list):
        """
            将目前的指令系统，分层一二级的形式。
                二级标签会额外的映射一级标签
                一级标签会有二级标签的加入
        """
        # 存储一级标签的列表
        level_1_group = [] 
        # 存储二级标签的列表
        level_2_group = []
        for ac in action_list:
            # 特殊处理：将"套电相关"统一转换为"套电"
            if ac == "套电相关":
                ac = "套电"
            # 判断当前动作是否是一级标签（是否存在于action_map的键中）
            if ac in self.action_map.keys():
                level_1_group.append(ac)
            # 不是一级标签则查找其对应的一级标签
            else:
                tmp = self.get_level_1_tag(ac)
                if self.get_level_1_tag(ac):
                    level_1_group.append(tmp)
                level_2_group.append(ac)
        # 对一级标签组去重（避免重复添加同一一级标签）
        level_1_group = list(set(level_1_group))
        ### 处理"只有一级标签但无对应二级标签"的情况 ###
        ## 如果 一级标签存在，但是二级标签不存在，则要添加*, 为了解决只有 答疑没有问诊的问题。
        # 初始化一级标签计数字典（值为1表示暂未找到对应二级标签）
        level_1_count = {key: 1 for key in level_1_group}
        # 遍历二级标签组，检查其对应的一级标签是否存在
        for x in level_2_group:
            if self.get_level_1_tag(x) in level_1_count.keys() and level_1_count[self.get_level_1_tag(x)]==1:
                del level_1_count[self.get_level_1_tag(x)] # 移除该一级标签（表示已找到对应二级标签）
        # 如果仍有一级标签没有对应二级标签，在二级组中添加"*"标识
        if level_1_count:
            level_2_group.append("*") 
        # 边界处理：如果两组都为空，默认都设为["*"]   
        if not level_1_group and not level_2_group:
            level_1_group, level_2_group = ["*"], ["*"]
        return level_1_group, level_2_group

    def get_level_1_tag(self, level_2_tag):
        for key, value in self.action_map.items():
            if level_2_tag in value:
                return key
        return None
    
    def get_action_level_count(self, action_list:Optional[List[List]]):
        from collections import Counter
        ac_map = Counter()

        for action in action_list:
            for ac in action:
                ac_map[self.get_level_1_tag(ac)] += 1
        return ac_map
    
    # 支持返回batch级别的问诊action个数
    def count_response_action_label_num(self, response_text: Union[str, List[str]]):
        if isinstance(response_text, list):
            # 文本预处理
            response_text = [t.replace("<sep>", "").replace("\t", "").replace(" ", "").replace("\n", "") for t in response_text]
            # 标签处理
            all_sentences = []
            for text in response_text:
                sentences = self.sentence_split_model.split(text)
                sentences = [str(item) for item in sentences]
                all_sentences.extend(sentences)
            utterance = "\t".join(all_sentences)
            nested_list = self.get_action_batch(utterance)
            action_results = []
            start_idx = 0
            for text in response_text:
                sentences = self.sentence_split_model.split(text)
                sentences = [str(item) for item in sentences]
                num_sentences = len(sentences)
                end_idx = start_idx + num_sentences
                # 这边要考虑每个句子生成的action是多大
                sentence_actions = nested_list[start_idx:end_idx]
                sentence_flat_actions = [item for sent_ac in sentence_actions for item in sent_ac]
                action_results.append({
                    "text": sentences,  # 原始文本内容
                    "action_list": sentence_flat_actions,  # 对应的 action 列表
                    "sentence_actions": sentence_actions, # 分句对应的action列表
                })
                start_idx = end_idx
            result_list = []
            for result in action_results:
                action_counts = {key: sum(1 for item in result["action_list"] if item in labels) for key, labels in self.action_map.items()}
                result_list.append({
                    "text": result["text"],  # 原始文本内容
                    "action_counts": action_counts,  # 每个文本的 action 数量统计
                    "sentence_actions": result["sentence_actions"], # 分句对应的action列表
                })
            return result_list

        else:
            # 文本预处理
            response_text = response_text.replace("<sep>", "").replace("\t", "").replace(" ", "").replace("\n", "")
            # 标签处理
            response_sent_list = self.sentence_split_model.split(text)
            response_sent_list = [str(item) for item in response_sent_list]
            utterance = "\t".join(response_sent_list)
            nested_list = self.get_action_batch(utterance)
            flat_list = [item for sublist in nested_list for item in sublist]
            action_counts = {key: sum(1 for item in flat_list if item in labels) for key, labels in self.action_map.items()}
            return {
                "text": response_sent_list,  # 原始文本内容
                "action_counts": action_counts,  # 单个文本的 action 数量统计
            }
        
    def process_by_action(self, init_data, server_round, rule_type):
        def strict_rule_1(sent_action_counts, sent_action):
            """
                匹配 前四轮不套电的检查规则
            """
            if ((sent_action_counts["问诊"] + sent_action_counts["确认"]) <=2 and (sent_action_counts["问诊"] + sent_action_counts["确认"])>0) and sent_action_counts["套电"] == 0 and sent_action_counts["答疑"] >= 0 and sent_action_counts["衔接"] >=0:
                return True
            elif sent_action_counts["套电"] and server_round <=4: 
                return False
            elif sent_action_counts["问诊"] == 0 and sent_action_counts["答疑"] >= 0 and sent_action_counts["套电"] > 0:
                flat_action_list = list(set([item for sublist in sent_action for item in sublist]))
                if "要联系方式"  in flat_action_list or "主动留联"  in flat_action_list or "要微信" in flat_action_list:
                    return True
            elif sent_action_counts["问诊"] > 0 and sent_action_counts["套电"] > 0 and sent_action_counts["答疑"] >= 0:
                return False
            elif sent_action_counts["问诊"] == 0 and sent_action_counts["套电"] == 0 and sent_action_counts["答疑"] > 0:
                return False
            elif sent_action_counts["拒诊"] >=0:
                return False
            else:
                return False
        def strict_rule_2(sent_action_counts, sent_action):
            """
                 匹配 prompt rule 函数
            """
            if ((sent_action_counts["问诊"] + sent_action_counts["确认"]) <=2 and (sent_action_counts["问诊"] + sent_action_counts["确认"])>0) and sent_action_counts["套电"] == 0 and sent_action_counts["答疑"] >= 0 and sent_action_counts["衔接"] >=0:
                return False
            elif sent_action_counts["套电"] and server_round <=2: 
                return False
            elif sent_action_counts["问诊"] == 0 and sent_action_counts["答疑"] >= 0 and sent_action_counts["套电"] > 0:
                flat_action_list = list(set([item for sublist in sent_action for item in sublist]))
                if "要联系方式"  in flat_action_list or "主动留联"  in flat_action_list or "要微信" in flat_action_list:
                    return False
            elif sent_action_counts["问诊"] > 0 and sent_action_counts["套电"] > 0 and sent_action_counts["答疑"] >= 0:
                return False
            elif sent_action_counts["问诊"] == 0 and sent_action_counts["套电"] == 0 and sent_action_counts["答疑"] > 0:
                return False
            elif sent_action_counts["拒诊"] >=0:
                return False
            elif sent_action_counts["答疑"] >0 and sent_action_counts["问诊"] == 0 and sent_action_counts["套电"] == 0:
                return True
            else:
                return False
        if rule_type == "1":    
            cur_run_rule = strict_rule_1
        elif rule_type == "2":
            cur_run_rule = strict_rule_2
        else:
            raise NotImplementedError("不存在这个规则")


        data_type = ""
        if isinstance(init_data[0], dict) and "messages" in init_data[0].keys():
            data_type = "sft"
        elif isinstance(init_data[0], str) :
            data_type = "list"   
        save_data = []       
        if data_type == "sft":
            for line in init_data:
                msg = line["messages"]
                new_msg = msg[1:]
                assistant_utterance_content = []
                for i, item in enumerate(new_msg):
                    if (i % 2 == 1) and  ("</think>" in item["content"]):
                        assistant_utterance_content.append(item["content"].split("</think>")[1])
                    elif (i % 2 == 1) and  ("</think>" not in ["content"]):
                        assistant_utterance_content.append(item["content"])
                results = self.count_response_action_label_num(assistant_utterance_content)
                is_use = all([cur_run_rule(res["action_counts"], res["sentence_actions"]) for res in results])
                if is_use:
                    save_data.append(line)

        elif data_type == "list":
            results = self.count_response_action_label_num(init_data)
            save_data = [init_data[i] for i, res in enumerate(results) if cur_run_rule(res["action_counts"], res["sentence_actions"])]
        return save_data


    def get_action_batch(self, utterance: str):
        content = {"utterance": utterance,
        "model_name": self.domain,
        "use_batch": "True"}
        res = requests.post(self.config["other"]["action_model_url"], json=content)
        res = json.loads(res.text)["data"]["intent"]
        return res





class SentPostProcess():
    def __init__(self) -> None:
        self.sent_split_cursor = StnSplit()
    
    def process_inquiry(self, text):
        sentences = text.split('?')
        question_count = len(sentences) - 1    
        if question_count <= 2:
            return text   
        result_sentences = []
        for i in range(2):  
            result_sentences.append(sentences[i].strip() + '?')
        return ' '.join(result_sentences)

    def split_sents(self, text):
        doc = self.sent_split_cursor.split(text)
        return "<sep>".join(doc)
    
    def filter_unexpect_sent(self, text_list, need_filter_list):
        """
            过滤掉 生成候选句中不想要的句子。
        """
        end_text_list = []
        for item in text_list:
            if item in need_filter_list:
                continue
            end_text_list.append(item)  
        return end_text_list       
    
    def filter_unexpect_keyword(self, text_list, need_filter_word_list):
        """
            过滤掉 生成候选句中不想要的关键字
        """
        end_text_list = []
        for item in text_list:
            flag = True
            for w in need_filter_word_list:
                if w in item:
                    flag = False
            if flag:
                end_text_list.append(item)    
        return end_text_list 

    def replace_candidates(self, text_list, replaces_candidates, specialtoken):
            """
            替换文本中的特定内容
            :param text_list: 输入文本列表
            :param replaces_candidates: 需要被替换的内容列表
            :param specialtoken: 替换后的特殊标记
            :return: 替换后的文本列表
            """
            replaced_texts = []
            for text in text_list:
                for candidate in replaces_candidates:
                    # 将每个候选内容替换为特殊标记
                    text = text.replace(candidate, specialtoken)
                replaced_texts.append(text)
            return replaced_texts

    def replace_one_to_one(self, text_list: List[str], replace_dict: Dict[str, str]) -> List[str]:
        """
        一对一替换文本中的特定内容
        :param text_list: 输入文本列表
        :param replace_dict: 替换字典，格式为 {"原词": "替换词"}
        :return: 替换后的文本列表
        """
        replaced_texts = []
        for text in text_list:
            for original, replacement in replace_dict.items():
                # 将每个原词替换为对应的替换词
                text = text.replace(original, replacement)
            replaced_texts.append(text)
        return replaced_texts

    def format_structured_text(self, text_list):
        """
        1.<sep> 咨询报价2.<sep> 地址/电话3.<sep> 套餐详情4.<sep>直接转人工5.<sep> 领取预约礼
        """
        # 使用正则表达式匹配结构化信息（如1.<sep>、2.<sep>等）
        # 并将其替换为换行符 + 序号
        for i in range(len(text_list)):
            text_list[i] = re.sub(r'(\d+)\.<sep>', r' \1.', text_list[i])
        return text_list
    

def recognition_contact_none_and_add_mobile_mask(sentence_list: Optional[List])->Optional[List]:
    """
        识别句子中 “主动留联但未提供联系方式” 的场景，并通过嵌入特殊标签 [[customerMobile]] 来标记需要填充联系方式的位置
    """
    new_sentence_list =  []
    for sentence in sentence_list:
        sentence = re.sub("我的微信 或者您加我也可以", "我的微信[[customerMobile]], 或者您加我也可以", sentence)
        sentence = re.sub("我们的电话也是微信(:|：)", "我们的电话也是微信:[[customerMobile]]", sentence)
        sentence = re.sub("我的微信是，加我方便沟通，您看可以吗", "我的微信是[[customerMobile]]，加我方便沟通，您看可以吗", sentence)
        new_sentence_list.append(sentence)
    return new_sentence_list




def dynamic_join_sentences(sentences, max_length=50):
    """
        动态将文本进行分句
    """
    if not sentences:
        return ""
    result = []
    current_chunk = []
    current_len = 0
    for sentence in sentences:
        sent_len = len(sentence)
        if current_len + sent_len <= max_length:
            current_chunk.append(sentence)
            current_len += sent_len
        else:
            result.append("".join(current_chunk)) 
            current_chunk = [sentence]
            current_len = sent_len
    
    # 处理最后的块
    if current_chunk:
        result.append("".join(current_chunk)) 
    return "<sep>".join(result).lstrip("<sep>").rstrip("<sep>")


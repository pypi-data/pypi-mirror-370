"""
     对话机器人--一些默认的policy。不同科室根据不同的特性进行不同的配置。
"""


from typing import Optional, Dict, List
import json
from cachetools import LRUCache
import configparser
import re
from kstprocess.dialog.postprocess import ActionProcessor



class ContextClueModel():
    def __init__(self) -> None:
        self.session_id = None
        self.nlu_result = LRUCache(maxsize=10000)
        self.topic_dict = LRUCache(maxsize=10000)
        self.action_filter_flag_dict = LRUCache(maxsize=10000)
        self.male_gender_keyword = ["睾丸", "阴茎", "阴毛", "腋毛", "胡须", 
                            "喉结", "变声", "睾丸酮", "雄激素",  "男"
                            "男生", "男孩"]
        
        self.female_gender_keyword = ["姨妈", "月经", "例假", "乳房", "阴毛", "胸部",
                                "腋毛", "初潮", "骨盆", "卵巢", "女生胸部", "女",
                                "女生", "女孩"]
    
    def get_nlu_result_and_get_clue(self, 
                                    session_id: Optional[str],
                                    input_params: Optional[Dict],
                                    user_utterance: Optional[str],
                                    dialogureRecord:Optional[List],
                                    keyword: Optional[str]):

        """
        提取topic信息
        提取性别信息，通过nluResult获取，通过user_utterance中的关键词匹配
        提取身份信息，通过nluResult获取，通过客户对话记录的每一个句子进行识别，如果线上服务中的称呼出错，可以改这里的识别策略
        """
        self.session_id = session_id
        ### 获取对话的 self.topic 信息
        if session_id not in self.topic_dict and "topic" in input_params.keys():
            self.topic_dict[session_id] = input_params["topic"] 
        elif session_id in self.topic_dict  and "topic" in input_params.keys() and input_params["topic"] != "无主题":
            # topic对应的值可能是None
            if input_params["topic"]:
                self.topic_dict[session_id] = input_params["topic"] 


        ### 获取搜索词中的性别信息
        if session_id not in self.action_filter_flag_dict:
            self.action_filter_flag_dict[session_id] = {}

        if session_id in self.nlu_result:
            pass
        else:
            self.nlu_result[session_id] = {"age": None, "gender": None, "height": None, "weight": None, "identity": None}
        
            # if "nluResult" not in input_params or not input_params["nluResult"]:
            #     self.nlu_result[session_id] = {"age": None, "gender": None, "height": None, "weight": None, "identity": None}
            #     self.action_filter_flag_dict[session_id] = {}

        if "nluResult" in input_params.keys():
            for item in json.loads(input_params["nluResult"])["data"][0]["entity"]:
                if item["key"] == "age" and item["value"][0]:
                    self.nlu_result[session_id]["age"] = item["value"][0]
                if item["key"] == "gender" and item["value"][0]:
                    self.nlu_result[session_id]["gender"] = item["value"][0]
                if item["key"] == "height" and item["value"][0]:
                    self.nlu_result[session_id]["height"] = item["value"][0] 
                if item["key"] == "weight" and item["value"][0]:
                    self.nlu_result[session_id]["weight"] = item["value"][0]
                if item["key"] == "identity" and item["name"] == "身份" and item["value"][0]:
                    self.nlu_result[session_id]["identity"] = item["value"][0]

        if user_utterance and keyword:
            if not self.nlu_result[session_id]["gender"]:
                for key in self.female_gender_keyword:
                    if key in user_utterance:
                        self.nlu_result[session_id]["gender"] = "女"
                    if key in keyword:
                        self.nlu_result[session_id]["gender"] = "女"
                for key in self.male_gender_keyword:
                    if key in user_utterance:
                        self.nlu_result[session_id]["gender"] = "男"
                    if key in keyword:
                        self.nlu_result[session_id]["gender"] = "男"
        ### 增加孩子本人 识别模块
        if dialogureRecord and self.nlu_result[session_id]["identity"] != "本人":
            utterance_list = [item["sentence"] for item in dialogureRecord if item["role"]=="CLIENT"]
            # 用户本人身份的正则表达式
            self_pattern = r"(^((?!.*(控制)).)*自[个己])|我的?(奶|姥|爷爷|外[婆公]|父|母|爸|妈|叔|婶|姨|兄|姐).*(专政|管太多|听不懂|没耐心)|我[跟和]?(奶|姥|爷爷|外[婆公]|父|母|爸|妈|叔|婶|姨|兄|姐)|我就?是(孩子|小[男女]?孩|学生)|我(现在|已经?有?|[当目]前|刚满|快要?)?([1-9][0-9]?|[一二三四五六七八九十][一二三四五六七八九]?)岁|(是|^)我(?!.*(想咨询|小孩|孩子|女儿|儿子|侄[子女]|儿童?|娃[娃儿]?))|(本人|我)才?(十?[一二两三四五六七八九]|十|1[0-9]|[1-9])周?岁|(本人|大人)"
            
            # 孩子身份的正则表达式
            child_pattern = r"我的?(儿子|女儿|孩[子女]|小[孩儿女]|婴[幼儿]|侄[子女]|孙[子女]|外?孙[子女])|(侄|孙|外?孙)[子女]|(小|大)?孩[子儿女]们?|(儿子|女儿|孩[子女]|小[孩儿女]|婴[幼儿]|侄[子女]|孙[子女]|外?孙[子女])的?|我[有个]?([1-9][0-9]?|[一二三四五六七八九十][一二三四五六七八九]?)岁的?(儿子|女儿|孩[子女]|小[孩儿女])|(他|她)是我(儿子|女儿|孩[子女]|小[孩儿女]|侄[子女]|孙[子女]|外?孙[子女])|学生|幼儿园|小学|中学"
            
            # 优先级：先检查本人，再检查孩子（可根据实际需求调整）
            for utterance in utterance_list:
                if re.search(self_pattern, utterance):
                    self.nlu_result[session_id]["identity"] = "本人"
                    break  # 一旦匹配成功就退出循环
                
                elif re.search(child_pattern, utterance):
                    self.nlu_result[session_id]["identity"] = "孩子"
                    break  # 一旦匹配成功就退出循环
        

        if "keyword_entity" in input_params.keys() and "data" in input_params["keyword_entity"] and input_params["keyword_entity"]["data"]:
            if input_params["keyword_entity"]["data"]["age"]:
                self.nlu_result[session_id]["age"] = input_params["keyword_entity"]["data"]["age"][0]
            if input_params["keyword_entity"]["data"]["gender"]:
                self.nlu_result[session_id]["gender"] = input_params["keyword_entity"]["data"]["gender"][0]



        if self.nlu_result[session_id]["gender"]:
            self.action_filter_flag_dict[session_id]["gender"] = True
        
        if self.nlu_result[session_id]["age"]:
            self.action_filter_flag_dict[session_id]["age"] = True




    def postprocess_by_age(self, response):
        try:
            if self.session_id in self.nlu_result and  "age" in self.nlu_result[self.session_id] and self.nlu_result[self.session_id]["age"] and int(self.nlu_result[self.session_id]["age"])>=18:
                response = [item.replace("孩子", "") for item in response]
                return response
            else:
                return response
        except:
            return response
        
    def postprocess_by_identity(self, response):
        try:
            if self.session_id in self.nlu_result and  "identity" in self.nlu_result[self.session_id] and self.nlu_result[self.session_id]["identity"] in ["自己", "我自己", "本人", "是本人", "我是孩子"]:
                response = [item.replace("他", "").replace("她", "").replace("它", "").replace("孩子", "") for item in response]
                return response
            else:
                return response
        except:
            return response







class ActionFilter():
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read('./config/sever.ini')
        with open(self.config["other"]["action_map_file_path"]) as f:
            self.action_map = json.load(f)
        self.actions_priority = {"答疑":2, "套电": 1, "问诊": 1, "None":0}
        with open(self.config["other"]["local_prompt_artificial_file"]) as f:
            self.local_prompt_artificial_file = json.load(f)
        self.topic_dict = LRUCache(maxsize=10000)
        self.session_id = None
        self.action_processor = ActionProcessor()

    def return_action_type(self, action:str):
        acquire_contact_type = self.action_map["套电"]
        Interrogation_type = self.action_map["问诊"]
        reply_type = self.action_map["答疑"]
        if action in acquire_contact_type:
            return "套电"
        elif action in Interrogation_type:
            return "问诊"
        elif action in reply_type:
            return "答疑"
        else:
            return "None"
        
    
    def add_prompt_priority(self, basic_action_label_list:Optional[List]=None, 
                                 mapping_prompt:Optional[List]=None,
                                 max_action_num:Optional[int]=4):
        """
             在basic_action_label_list加入 action，如果存在问诊，套电 动作则 不加入
        """
        actions_count = {"套电": 0, "答疑":0, "问诊": 0, "None": 0}
        save_actions = set()

        for basic_ac in basic_action_label_list:
            basic_t = self.return_action_type(basic_ac)
            actions_count[basic_t] += 1
            save_actions.add(basic_ac)

        for mapping_ac in mapping_prompt:
            mapping_t = self.return_action_type(mapping_ac)   
            # 规则1：若动作类型不是"None"，且该类型已有超过2个动作，则不添加（避免同一类型动作过多)
            if mapping_t != "None" and actions_count[mapping_t] > 2:
                continue
            # 规则2：若动作是"套电"类型，且已有"问诊"动作，则不添加（套电和问诊互斥)
            if mapping_t == "套电" and actions_count["问诊"] > 0:
                continue
            # 规则3：若动作是"问诊"类型，且已有"套电"动作，则不添加（同理，问诊和套电互斥）
            if mapping_t == "问诊" and actions_count["套电"] > 0:
                continue
            # 规则4：若当前动作总数未超过上限（max_action_num），则添加该动作
            if len(save_actions) <= max_action_num:
                save_actions.add(mapping_ac)
            else:
                break
        return list(save_actions)

    def count_action_type_num(self, actions:Optional[List]):
        """
            计算一个list 中的action的一级标签（在action_mapping.json里面对应）的数量
        """
        actions_count = {"套电": 0, "答疑":0, "问诊": 0, "None": 0}
        for ac in actions:
            actions_count[self.return_action_type(ac)] += 1
            if ac in self.action_map.keys():
                actions_count[ac] += 1
        return actions_count
    
    def get_order_value(self, actions:Optional[List]):
        """
             按照默认的一级标签的优先级，进行重排。
        """
        action_order_dict = {}
        for ac in actions:
            ac_priority = self.actions_priority[self.return_action_type(ac)]
            action_order_dict[ac] = ac_priority
        action_order_dict = sorted(action_order_dict.items(), key=lambda x: x[1], reverse=True)
        actions = [action for action, _ in action_order_dict]
        return actions


    def add_prompt_strict(self, basic_action_label_list:list, prompt_artificial:list):
        """
           basic_action_label_list 加入action --》全包容策略
        """
        basic_action_label_list.extend(prompt_artificial)
        basic_action_label_list = list(set(basic_action_label_list))
        return prompt_artificial
    

    def fill_action_by_default_config(self, prompt_artificial:Optional[List],
                                            server_round:Optional[str]):
        """
            查找本地配置的指令，例如(默认主题继承)
                    "抽动症": {
                        "1": ["问年龄"],
                        "2": ["问诊"],
                        "3": ["问诊"],
                        "4": ["问诊"],
                        "5": ["治疗套电话术"],
                        "7": ["答疑", "套电相关"],
                        "10": ["套电相关"],
                        "13": ["套电相关"]
                    },
        """

        new_prompt_artificial = []
        for p in prompt_artificial:
            if p in ["问诊", "答疑", "套电", "套电相关"] and self.topic_dict[self.session_id] in self.local_prompt_artificial_file.keys() and server_round in self.local_prompt_artificial_file[self.topic_dict[self.session_id]].keys() and p ==  self.return_action_type(self.local_prompt_artificial_file[self.topic_dict[self.session_id]][server_round]):
                new_prompt_artificial.extend(self.local_prompt_artificial_file[self.topic_dict[self.session_id]][server_round])
            else:
                new_prompt_artificial.append(p)
        return new_prompt_artificial
    
    
    def action_filter_policy_for_prospective_user(self,
                                                  dialogRecord:Optional[List[Dict]],
                                                  user_utterance:str,
                                                  server_round:int,
                                                  action_label_list: Optional[List]):
        """
            倾向套电的， 下一轮 action 更新为要联系方式。
        """
        # ROBOT_WARM ROBOT_GUIDE ROBOT_GREETING
        pattern = r'^(?:[嗯恩]?好的?|可以[的]?$?|方便$|行$|成$|[OoKk]$|谢谢$|[嗯恩]，好$|[嗯恩],好$|好好$|[嗯恩]$|发来看看$|用$)$'
        actions_order_list = [line["action"] for line in dialogRecord if line["subType"] not in ["ROBOT_GREETING", "ROBOT_GUIDE", "ROBOT_WARM"] and line["role"]=="SERVER"]
        last_action = actions_order_list[-1] 
        last_ac_map = self.action_processor.get_action_level_count(last_action)
        if last_ac_map["套电"] > 0 and server_round >3 and re.match(pattern, user_utterance):
            return ["要微信"]
        else:
            return action_label_list
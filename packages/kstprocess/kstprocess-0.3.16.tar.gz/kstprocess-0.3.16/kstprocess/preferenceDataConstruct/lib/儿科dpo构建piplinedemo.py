import json
import time
import configparser
from tqdm import tqdm
from typing import Optional, List, Dict, Union
import ast
import re
from kstprocess.preferenceDataConstruct.lib.action_predict import get_prompt_info
from kstprocess.util.format_convert import add_action_for_train_data_batch
from util.llm_server import request_native_llm_server
from kstprocess.util.util import read_action_file, read_jsonl_from_path
from kstprocess.preferenceDataConstruct.lib.util import SearchText, DialogueServer, convert_general_to_dialogue_str, filter_unexpect_words_sentences
from kstprocess.preferenceDataConstruct.lib.client_server import ClientServer
from util.postprocess.action_util import ActionProcessor
from util.postprocess.duplication_util import DuplicationProcesser
from pathlib import Path



UNEXPECT_WORD_LIST = ["方便", "深入", "分享", "确实", "为了"]



#### DPO 数据集构建 ####
class DpoDatasetConstruct:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read("./config/paediastrics/dpo_config.ini")  
        a = SearchText(self.config["prefix"])
        self.search_text_list = a.set_common_search_text()
        self.client_model = ClientServer(self.config)
        self.assistant_model = DialogueServer(self.config["prefix"])
        self.action_list = read_action_file(self.config["prefix"]["action_file_path"])
        self.max_retries = int(self.config["prefix"]["max_retries"])
        self.delay = int(self.config["prefix"]["delay"])
        self.rag_postprocess = ActionProcessor(action_model_url=self.config["prefix"]["action_model_url"],
                                               action_map=self.action_list, 
                                               domain="paediastric")
        self.duplication_model = DuplicationProcesser()
        self.unexpect_words_list = UNEXPECT_WORD_LIST


    def reward_predict(self, dialog_record_str: Optional[str], 
                             candidates: Optional[List], 
                             clue_information: Optional[str]) -> Optional[List]:
        my_prompt = """
 ##核心原则,重要性按顺序递减##

        1.专业性优先
            **弄清访客画像**：优先解决当前核心问题（如年龄歧义需立即澄清）。
            **关键诊断指标**：优先询问具体症状表现（如“发音是否混淆‘csjz’”）、量化数据（如“近一年身高增长多少厘米？”）或持续时间（如“症状出现多久了？”）。
            **专业术语准确**：使用规范医学术语（如“第二性征发育”），避免模糊描述（如“身体变化”）。
            **避免重复**：若用户已提供信息（如年龄），不再重复询问。
            **减少冗余话术**：避免“为了更好地理解”等无效礼貌用语。
        2.逻辑性规范
            **问诊流程**：按医学逻辑提问（先基础问题→再深入细节），如先确认年龄、性别，再询问具体症状。访客明确了写了年龄了，就不要在问诊了。
            **问题关联性**：不要问跟病症没有多大关系或者无关紧要的问诊，避免跳跃式提问（如“身高如何？是否挑食？睡眠时间？”）。
            **上下文衔接**：问题需与用户主诉直接相关，如用户咨询“发育迟缓”，优先询问“具体表现”而非“持续时间”。
            **问诊和答疑保持一致性和逻辑性**  不要答疑和问诊之间没有共同性。
        3.问诊原子性
            单问题原则：
                每次问诊仅针对 一个核心问题，即使涉及症状列举，也需围绕同一主题（例如：“孩子是否有以下情况：①理解指令困难？②重复语言？③对声音敏感？”）。
                同一主题下的 症状细节追问也是单问题。 例如(从“是否存在异常”到“具体表现形式”)
            禁止多问题：避免将多个独立问题合并为一条回复（如“症状A是否出现？症状B呢？” → 违反规则）。
            例外：列举症状选项不视为多问题，但需明确指向同一核心问题（如“孩子是否出现以下沟通困难：①无法理解指令？②无法表达需求？③与同伴互动时退缩？”）。
            (1)符合原子性原则
                问题：“孩子在理解大人指令时是否有困难？例如：①无法执行‘拿玩具’等简单指令？②对‘为什么’等问题回答模糊？”
                理由: 单一核心问题“语言理解困难”，通过列举症状选项细化，符合原子性原则
            (2)违反原子性原则
                    问题：“孩子在理解大人说话时，是不是也能明白呢？平时和小朋友一起玩的时候，有没有遇到沟通上的困难？”
                    扣分原因：包含两个独立问题（语言理解能力 + 社交沟通困难），违反“单问题原则”。
                    修改建议：拆分为两次问诊，或合并为单一核心问题（如“孩子在理解指令或与同伴互动时，是否遇到困难？具体表现是什么？”）。
            有且一个回复中包含一个问题，大于等于2的问题数打低分。
        4.简洁性与用户感知
            **减少礼貌用语** 如：好的我这边先了解下；了解了，
            **通俗易懂**：使用日常语言（如“尿床”而非“遗尿”），但需避免因过度通俗导致不专业。
            **减少铺垫,套话话术 **
                例如： 解这一点可以帮助我们更好地评估情况。 打零分。
                例如: 了解孩子的具体症状对诊断很重要。  打零分。
        5. 套电和问诊标准分开评判。
            套电更加注重对于访客主诉的回应，同时需要给出具体的福利，不要空泛。同时要符合逻辑性和简洁性用户感知要求
        
        6. 出现具体的敏感词信息全部打零分。
        7. 回复必须要基于事实的，如果回答不是基于事实的，或者上逻辑有问题的上面直接打低分。特别是不同年龄之间的儿童同个症状应该是有不同的表现，回复要注意措辞。
            你好，一般绝经之后就不会再出现了<sep>请问您是第一次出现这种情况吗？<sep>那您的年龄是多大呢？今年虚岁周岁？男孩女孩呢？ 打低分
            理由：女生才有月经的说法，不该问男的女的

                
#### 给下面的句子进行打分 ####
对话记录：raw_history

#### 候选句子 ####
    candidates
#### 输出格式 ####
    输出list，一一对应只输出分数0-10之间。不要给出理由和思考过程直接给出结果。
        ### 输出例子 ###
    输出候选句子一一对应的打分, 越符合条件的分值越高，分值0-10之间。
    不要输出思考过程和得分理由在 同时输出最后结果。
    示例1:
        假设输入的候选句子:[s1,s2,s3,s4,s5]
        [5,2,6,8,4]
    示例2:
        输入候选句子:[s1,s2,s3]
        输出: [6,9,4]
        #### 输出对话 ###

        """
        cur_prompt = my_prompt.replace("raw_history", str(dialog_record_str)).replace( "candidates", str(candidates)).replace("clue_information", clue_information)

        candidates_scores_list = request_native_llm_server(cur_prompt ,
                                                           enable_close_think=True)
        print("---"*50)
        print("---"*50)
        try:
            if "</think>" in candidates_scores_list:
                candidates_scores_list = candidates_scores_list.split("</think>")[1].replace("</output>", "").replace("<output>", "")
            candidates_scores_list = ast.literal_eval(candidates_scores_list)
            candidates_scores = [{"sentence": candidates[i], "score":candidates_scores_list[i] } for i in range(min(len(candidates_scores_list), len(candidates)))]
            print(f"打分结果:{json.dumps(candidates_scores, ensure_ascii=False, indent=1)}")
            return candidates_scores
        except:
            candidates_scores = None
        return candidates_scores

    def get_clue_by_llm(self, dialogure:Optional[List[Dict]], utterance:str):
        history = [h["sentence"] if  type(h)==dict else h for h in dialogure]
        my_prpmpt = """
你作为儿科资深客服，根据访客与客服的对话历史，总结线索。
####步骤####：
1.病症识别：分析访客与客服的对话历史以及访客的搜索词，判断访客的病症或健康问题，若咨询生长发育问题则根据描述推测具体问题。
2.访客画像：根据访客的搜索词和访客的描述，提取关键信息（如年龄、性别、身高、体重、症状持续时间等），形成访客画像。同时考虑是否是第三方咨询，还是患者本人咨询。
3.识别访客意图：根据判断出的访客的病症或健康问题，结合搜索词和访客画像，识别访客的意图。
4.总结访客潜在需求: 思考访客来医院咨询的原因，判断访客主要目的，例如想了解身高发育、体重标准、生长曲线等。
5.访客主要目的:
6.访客留联意向：倾向，中立，拒绝。
####要求####：
    禁止输出“例如：...”这样的解释说明
    所有描述不超过20个字符 多个描述用、分隔
    福利可以给多个，但不超过4个
    输出格式必须为：病症识别：...\n访客画像：...\n访客意图：...\n访客潜在需求：...\n访客留联意向:...\n\n

###举例说明###：
例子1：
    对话历史：
        访客：我家孩子身高170cm，腿长应该多少？
        客服：您好，请问孩子是男孩还是女孩呢？
        访客：男孩
        客服：孩子现在几岁了呢？近年来身高变化大吗？
        访客：14岁，最近一年长得慢了
        客服：建议您带孩子来医院做个详细检查，评估生长发育情况
    访客回复：
        好的
    输出：
       病症：身高发育问题\n访客画像：家长咨询,14岁男孩、身高170cm、近一年身高增长缓慢\n访客意图：咨询身高与腿长比例、描述身高变化\n访客潜在需求：访客想了解孩子身高发育是否正常\n主要目的:孩子是腿长是否符合比例\n访客留联意向:中立\n\n

例子2：
    对话历史：
        访客：我家孩子体重偏轻，怎么办？
        客服：您好，请问孩子几岁了？平时饮食情况如何？
        访客：5岁，吃饭不太好
        客服：孩子是否有挑食或消化问题？建议来医院做个营养评估
    访客回复：
        有点挑食，医院还有这方面的评估吗
输出：
    病症：体重偏轻\n访客画像：5岁儿童、饮食不佳、挑食\n访客意图：咨询体重问题、描述饮食情况\n访客潜在需求：访客想了解孩子体重偏轻的原因及改善方法\n主要目的:孩子体重太轻的办法\n访客留联意向:倾向\n\n

####对话历史####：
history
####访客回复####：
query
输出：
    病症：...\n访客画像：...\n相关知识:...\n访客意图：...\n主要目的：...\n访客潜在需求：...\n\n        
"""
        cur_prompt = my_prpmpt.replace("history", str(history)).replace("query", utterance)
        res = request_native_llm_server(cur_prompt, enable_close_think=True)
        if "</think>" in res:
            res = res.split("</think>")[1].lstrip()
        print(f"****线索服务****:\n{res}")
        return res


    def generate_candidates(self, dialog_record_str: Optional[str], 
                                  generate_text_list: Optional[List],
                                  clue_information: Optional[List],
                                  use_action_list: Optional[List]):
        my_prompt = """
你是一位经验丰富的医疗客服人员，根据提供的访客与客服的对话历史和线索信息，生成五条不同且连贯的话术回复。

### 生成话术应遵循的原则：
1. **多样性与连贯性**：确保每条话术都独特且与前文对话逻辑一致。
2. **针对性解答**：针对访客的主要诉求提供直接有效的回答，避免使用如“了解了”、“确实”这样公式化的表达。
3. **自然度与简洁性**：采用日常交流的语气，不过分礼貌或正式，使对话显得亲切而直接。如果需要获取微信或其他联系方式时，直接询问，并可以提及相关的福利吸引对方分享信息。
    例子: 为了更好地帮助您的孩子，我需要了解更多关于她生活和学习环境的信息。<sep>您平时在家辅导孩子的作业吗？她的学习成绩如何？
            不要出现 为了..这种话术，表明目的，直接进行问诊和答疑就行。
4. **参考风格**：基于给出的候选话术来模仿其对话风格进行创作。
5. **单一目的原则**：每条话术专注于一个目标（如诊断建议或者索要联系方式），不在同一轮对话中同时提出多个请求。
6. **根据动作(Action)定制话术**：根据指定的动作(action_list)，生成相应类型的话术内容。
7. 减少铺垫话术和套话。要有实际的产出。
8. 套电和问诊生成分开。
            套电更加注重对于访客主诉的回应，同时需要给出具体的福利，不要空泛。同时要符合逻辑性和简洁性用户感知要求

    套电偏好话术
        孩子这样的情况要考虑膀胱构造是否完善，脊柱这块是否有存在问题以及是否造成遗尿的倾向，家长，这样吧，我这边有分遗尿的测试表你先帮助孩子测评下，我稍后根据测试的结果建议如何解决，这样更有针对性，也不盲目，你微信多少？我加你发送给你
    不要出现下面这种太过礼貌或者过度询问的句子:`
        为了更详细地分析和提供针对性建议，方便您吗？可以留下您的联系方式，我会分享一些关于如何帮助孩子应对这种情况的知识和实用技巧。
            为了，方便，我会分享这种都是不好的、
9. 生成的问诊偏好列举具体的症状，不要用简单的代词描述：
    例如   不希望出现  有没有观察到孩子在特定环境下更容易出现这种情况？
           希望生成  有没有观察到孩子在紧张，陌生的场景下是不是更容易出现眨眼这样的情况呢？
### 提供的信息：
- 对话历史(dialog_record_str)
- 对话线索(clue_information)
- 候选话术(generate_text_list)
- 当前动作(action_list)

请依据上述指导原则及提供的信息，为以下情景生成五个候选话术，格式如下：

["句子1", "句子2", "句子3", "句子4", "句子5"]

注意：尽量让生成的话术听起来像是来自真实的客服人员，而不是自动化系统。
        """
        cur_prompt = my_prompt.replace("dialog_record_str", dialog_record_str).replace("generate_text_list", str(generate_text_list)).replace("clue_information", clue_information).replace("action_list", str(use_action_list))
        res = request_native_llm_server(cur_prompt, enable_close_think=False)
        if "</think>" in res:
            res = res.split("</think>")[1].lstrip()
        res = ast.literal_eval(res)
        print("****rag候选话术****:\n",  res)
        return res

    def convert_to_qwen_format(self, init_msg: List[Dict]) -> List[Dict]:
        """
        将对话记录转换为 Qwen 格式
        """
        new_format = []
        for line in init_msg:
            if line["role"] == "CLIENT":
                new_format.append({"role": "user", "content": line["sentence"]})
            else:
                new_format.append({"role": "assistant", "content": line["sentence"]})
        return new_format

    def __count_dialogure_round(self, dialog_record:Optional[List]):
        r0 = [record["role"].lower() for record in dialog_record]
        r0t = "".join(r0)
        r0t = r0t.replace("client","C")
        r0t = re.findall("C{1,}", r0t)
        server_round = len(r0t)
        return server_round

    def convert_robot_stytle_pipeline(self, sentences_list):
        generate_text = []
        for sentences in tqdm(sentences_list, total=len(sentences_list), desc="改写中:"):
            sensitive_key_word = []
            for word in self.unexpect_words_list:
                if word in sentences:
                    sensitive_key_word.append(word)
            if sensitive_key_word:
                my_prompt = """
                ###你的任务是负责改写，改写过程中不能够改成原本句子意思和对话风格。
                ###要求:
                    1.改写不要出现敏感词:  sensitive_words
                    2.生成的口气一定不要太客气，保持正常聊天的口气。
                ###输入:
                    原始句子列表: old_sentence
                    存在的敏感词列表: sensitive_key_word
                ###输出格式,只生成改写之后的句子。
                """
                cur_prompt = my_prompt.replace("old_sentence", sentences).replace("sensitive_key_word", str(sensitive_key_word)).replace("sensitive_words", str(self.unexpect_words_list))
                cur_text = request_native_llm_server(cur_prompt)
                generate_text.append(cur_text)
        return generate_text

    def set_sensitive_sentence_reward_to_lower(self, reward_dict_list):
        new_reward_dict_list = []
        set_low_value = 1
        for item in reward_dict_list:
            sentences = item["sentence"]
            for word in self.unexpect_words_list:
                if word in sentences:
                    item["score"] = set_low_value
                    break
            new_reward_dict_list.append(item)
        return new_reward_dict_list
    
    def pipeline_for_dialogure_simulate(self):
        """
        构建 DPO 数据集的主流程
        """
        message_id = 0
        for search_text in tqdm(self.search_text_list, total=len(self.search_text_list), desc="construct:"):
            message_id += 1
            dialog_record = [{
                "role": "CLIENT",
                "sentence": "搜索词:"+search_text},
                {"role": "SERVER",
                 "sentence": f"引导语:您好，请问有什么可以帮助您的？"}
            ]
            rft_history = dialog_record.copy()
            print("###"*50)
            try:
                while True:  # 保持对话循环
                    ### 获取访客模型回复 ###
                    user_utterance = self.client_model.get_client_response(dialog_record, dialog_id=str(message_id))
                    print(dialog_record)
                    print(f"user_utterance:{user_utterance}")
                    match = re.search(r'(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}', user_utterance)
                    if "<dialogover>" not in user_utterance and not match :  # 如果对话未结束
                        dialog_record_str = convert_general_to_dialogue_str(dialog_record, user_utterance)
                        ### 获取 action ###
                        clue_informations = self.get_clue_by_llm(dialog_record, user_utterance)

                        server_round = self.__count_dialogure_round(dialog_record)
                        prompt_info = get_prompt_info(utterance=user_utterance, server_round=server_round, domain="paediastrics")
                        prompt_info["prompt_acp"] = clue_informations


                        generate_text_list, use_action_list = self.assistant_model.post_server_url_test(
                            dialog_record,
                            dialogId=message_id,
                            keyword=search_text,
                            utterance=user_utterance,
                            limit=5,
                            promptInfo=prompt_info
                        )
                        print(f"use_action_list:{use_action_list}")
                        ## 加入rag 部分 ###
                        rag_candidates = self.generate_candidates(dialog_record_str, 
                                                                    generate_text_list, 
                                                                    clue_informations,
                                                                    use_action_list)
                        rag_candidates = filter_unexpect_words_sentences(unexpect_words_list=UNEXPECT_WORD_LIST, rag_candidates=rag_candidates)
                        if rag_candidates:
                            rag_candidates = self.rag_postprocess.process_by_action(rag_candidates)

                        ### 进行去重  ####
                        if rag_candidates and generate_text_list:
                            rag_candidates = self.duplication_model.deduplicate_candidates(rag_candidates)
                            generate_text_list = self.duplication_model.deduplicate_candidates(generate_text_list)

                        print("****过滤和去重后rag候选话术****:\n", rag_candidates)
                        print("****去重后本地模型生成话术****:\n", generate_text_list)

                        ### 将rag 部分的内容和模型生成的内容拼接在一起 ###
                        generate_text_list.extend(rag_candidates)
                        rewrite_sentence = self.convert_robot_stytle_pipeline(generate_text_list)
                        print("****敏感词改写话术****:\n", rewrite_sentence)
                        generate_text_list.extend(rewrite_sentence)
                        generate_text_list = self.duplication_model.deduplicate_candidates(generate_text_list)
                        generate_text_list = self.rag_postprocess.process_by_action(generate_text_list)
                        if len(generate_text_list) <2:
                            flag = True
                        else:
                            flag = False
                        reward_res = self.reward_predict(dialog_record_str, candidates=generate_text_list, clue_information=clue_informations)

                        ### 将打分高的含有敏感词的话术 手动降低分值  ###
                        reward_res = self.set_sensitive_sentence_reward_to_lower(reward_res)
                        print("----"*15)
                        print("****降低分值后的打分***")
                        print(reward_res)
                        print("----"*15)
                        
                        if reward_res and not flag:
                                # 找到最高分和最低分的条目
                                max_item = max(reward_res, key=lambda x: x['score'])
                                min_item = min(reward_res, key=lambda x: x['score'])
                                
                                # 合并结果（确保最高和最低不重复，若分数相同则保留两个）
                                filtered = [max_item, min_item]
                                if max_item["score"]-min_item["score"]< 2:
                                    filtered = []
                        else:
                            filtered = []
                        print("最好最坏打分：")
                        print(filtered)      
                        reward_res = filtered

                        if reward_res and isinstance(reward_res, list) and len(reward_res)>=1 :
                            dpo_history = dialog_record.copy()
                            dialog_record.append({"role": "CLIENT", "sentence": user_utterance})
                            rft_history.append({"role": "CLIENT", "sentence": user_utterance})
                            dpo_history.append({"role": "CLIENT", "sentence": user_utterance})
                            def append_and_convert(role, sentence, history):
                                """辅助函数用于追加句子并转换"""
                                temp_history = history.copy()
                                temp_history.append({"role": role, "sentence": sentence})
                                return self.convert_to_qwen_format(temp_history)
                            # 初始化偏好对列表
                            preference_pairs = []


                            # 遍历所有句子，寻找分差大于4的配对, 去掉chonsen 中含有敏感词的偏好对
                            for i in range(len(reward_res)):
                                for j in range(i + 1, len(reward_res)):  # 确保每个对只被检查一次
                                    if abs(reward_res[i]['score'] - reward_res[j]['score']) >= 4:
                                        if reward_res[i]['score'] > reward_res[j]['score']:
                                            chosen_sentence = reward_res[i]['sentence']
                                            rejected_sentence = reward_res[j]['sentence']
                                        else:
                                            chosen_sentence = reward_res[j]['sentence']
                                            rejected_sentence = reward_res[i]['sentence']
                                        ### 去除敏感词 ###
                                        match = filter_unexpect_words_sentences(UNEXPECT_WORD_LIST, [chosen_sentence])
                                        if not match:
                                            continue
                                        chosen_pair = append_and_convert("SERVER", chosen_sentence, dpo_history)
                                        rejected_pair = append_and_convert("SERVER", rejected_sentence, dpo_history)
                                        # 使用集合来避免重复的组合
                                        pair_set = {chosen_sentence, rejected_sentence}
                                        if pair_set not in [set(pair['chosen'][-1]['content'] for pair in preference_pairs), set(pair['rejected'][-1]['content'] for pair in preference_pairs)]:
                                            preference_pairs.append({"chosen": chosen_pair, "rejected": rejected_pair})

                            highest_score_sentence = max(reward_res, key=lambda x: x['score'])
                            dialog_record.append({"role": "SERVER", "sentence": highest_score_sentence["sentence"]})
                            rft_history.append({"role": "SERVER", "sentence": highest_score_sentence["sentence"]})


                            with open(self.config["prefix"]["dpo_save_file_path"], "a") as f:
                                for i, item in enumerate(preference_pairs):
                                
                                    item = add_action_for_train_data_batch([item])[0]
                                    print(item)
                                    f.write(json.dumps(item, ensure_ascii=False) + "\n")


                            print("---"*50)
                            print(f"当前对话：{dialog_record}")
                            print("---"*50)
                            print()
                        else:
                            break 
                    else:
                        time.sleep(self.delay)  # 如果对话结束，等待一段时间
                        break  # 退出循环

                with open(self.config["prefix"]["rft_save_file_path"], "a") as file:
                    rft_history = self.convert_to_qwen_format(rft_history)
                    file.write(json.dumps({"messages": rft_history}, ensure_ascii=False) + "\n")
            except KeyboardInterrupt:
                return 
            except:
                continue
    
    
    def pipeline_for_prompt(self, file_path:Optional[Path]):
        def convert_prompt_data(prompt_data):
            prompt_data["prompt"][-1]["content"] = prompt_data["prompt"][-1]["content"].split("action:")[0]
            dialog_record = []
            search_text = ""
            for item in prompt_data["prompt"]:
                if item["role"] == "user":
                    dialog_record.append({"role": "CLIENT", "sentence": item["content"]})
                elif item["role"] == "system":
                    ### 默认用\n 分开，第二个是搜索词，第三个是引导语
                    _, search_text, guide_text = item["content"].split("\n")
                    dialog_record.append({"role": "CLIENT", "sentence": search_text})
                    dialog_record.append({"role": "SERVER", "sentence": guide_text})
                else:
                    dialog_record.append({"role": "SERVER", "sentence": item["content"]})
            user_utterance = dialog_record[-1]["sentence"]
            return dialog_record, search_text,user_utterance
            
        prompt_data = read_jsonl_from_path(file_path=file_path)
        prompt_data = prompt_data[3000:]
        for message_id, item in tqdm(enumerate(prompt_data), total=len(prompt_data), desc="构建数据..."):
            ### 解析messages 函数 ###
            try:
                dialog_record, search_text, user_utterance = convert_prompt_data(item)
                server_round = self.__count_dialogure_round(dialog_record)
                prompt_info = get_prompt_info(utterance=user_utterance, server_round=server_round, domain="paediastrics")
                generate_text_list, use_action_list = self.assistant_model.post_server_url_test(
                    dialog_record[:-1],
                    dialogId=message_id,
                    keyword=search_text,
                    utterance=user_utterance,
                    limit=5,
                    promptInfo=prompt_info)
                dialog_record_str = convert_general_to_dialogue_str(dialog_record, user_utterance)
                print(dialog_record_str)
                clue_informations = self.get_clue_by_llm(dialog_record, user_utterance)
                generate_text_list = self.duplication_model.deduplicate_candidates(generate_text_list)
                rag_candidates = self.generate_candidates(dialog_record_str, 
                                                            generate_text_list, 
                                                            clue_informations,
                                                            use_action_list)
                rag_candidates = filter_unexpect_words_sentences(unexpect_words_list=UNEXPECT_WORD_LIST, input_list=rag_candidates)
                if rag_candidates:
                    rag_candidates = self.rag_postprocess.process_by_action(rag_candidates)
                print(generate_text_list)
                print("****rag_g****")
                print(rag_candidates)
                all_text_list = []
                all_text_list.extend(generate_text_list)
                all_text_list.extend(rag_candidates)
                if len(generate_text_list) >1:
                    reward_res = self.reward_predict(dialog_record_str, candidates=all_text_list, clue_information=clue_informations)
                    print("打分结果:")
                    print(reward_res)
                    if reward_res:
                        # 找到最高分和最低分的条目
                        max_item = max(reward_res, key=lambda x: x['score'])
                        min_item = min(reward_res, key=lambda x: x['score'])
                        
                        # 合并结果（确保最高和最低不重复，若分数相同则保留两个）
                        filtered = [max_item["sentence"], min_item["sentence"]]
                        if max_item["score"]-min_item["score"]< 2:
                            filtered = []
                            continue
                        with open("./偏好数据构建.jsonl", "a") as file:
                            item["chosen"] = [{"role": "assistant", "content": filtered[0]}]
                            item["rejected"] = [{"role": "assistant", "content": filtered[1]}]
                            file.write(json.dumps(item, ensure_ascii=False)+"\n")
                print()
                print()
            except KeyboardInterrupt:
                return
            except:
                continue
       

    
from pathlib import Path
from typing import Optional, List, Dict, Union
import ast
from tqdm import tqdm
import json
import logging
from kstprocess.util.llm_server import request_native_llm_server
from functools import partial
from kstprocess.util.format_convert import add_system_prompt_for_train_data, convert_chosen_rejected_to_prompt
from kstprocess.preferenceDataConstruct.util import NativeChatLLMServer, convert_general_to_dialogue_str, get_random_chosen_rejected_pair
from kstprocess.util.postprocess.duplication_util import DuplicationProcesser
from kstprocess.util.postprocess.action_util import ActionProcessor

root_logger = logging.getLogger()

# 设置根日志记录器的级别为 CRITICAL，这样只有严重错误会被记录
root_logger.setLevel(logging.CRITICAL)

# 移除所有现有的处理器以防止日志输出
if root_logger.hasHandlers():
    root_logger.handlers.clear()



class DpoDatasetConstruct(object):
    def __init__(self,  enable_close_think:Optional[bool]=True, 
                        nativeChatLLM_model_path: Optional[str]="http://localhost:9990/dialog_gpt_v1",
                        openai_api_key:Optional[str]="zj", 
                        openai_api_base:Optional[str]="http://192.168.1.67:8888/v1", 
                        model:Optional[str]="llm_zj",
                        is_use_postprocess_action_model:Optional[bool]=True,
                        action_model_url:Optional[str]="http://10.14.250.11:30412/kicp-micro-common-action-service",
                        action_map:Optional[dict]=None,
                        domain:Optional[str]="paediastrics") -> None:
        self.assistant_model = NativeChatLLMServer(nativeChatLLM_model_path)
        self.requsest_llm = partial(request_native_llm_server, 
                                    enable_close_think=enable_close_think,
                                    openai_api_key=openai_api_key,
                                    openai_api_base=openai_api_base,
                                    model=model,
                                    )
        self.post_process_sim_model = DuplicationProcesser()
        self.is_use_postprocess_action_model = is_use_postprocess_action_model
        if is_use_postprocess_action_model:
            self.post_process_action_model = ActionProcessor(action_model_url=action_model_url,
                                                            action_map=action_map,
                                                            domain=domain)

    def get_candidates_scores(self, reward_prompt: Optional[str], 
                                    dialog_record_str: Optional[str], 
                                    candidates: Optional[List]) -> Optional[List]:
        new_prompt = reward_prompt.replace("dialog_record_str", str(dialog_record_str)).replace("candidates", str(candidates))
        res = self.requsest_llm(formatted_dialog=new_prompt)
        if "</think>" in res:
            res = res.split("</think>")[1]
        res = res.split(",")
        res = [int(s) for s in res]
        candidates_scores = {candidates[i]: res[i] for i in range(min(len(res), len(candidates)))}
        print("---"*50)
        print(f"每个句子对应的评分为：{res}")
        print("---"*50)
        return candidates_scores

    def get_clue_by_llm(self, clue_prpmpt:Optional[str],
                              dialogure:Optional[List[Dict]], 
                              utterance:str):
        """
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

        history = [h["sentence"] if  type(h)==dict else h for h in dialogure]
        cur_prompt = clue_prpmpt.replace("history", str(history)).replace("query", utterance)
        res = self.requsest_llm(formatted_dialog=cur_prompt)
        if "</think>" in res:
            res = res.split("</think>")[1]
        print(f"****线索服务****:\n{res}")
        print("###"*50)
        return res


    def generate_candidates_by_large_llm(self, generate_prompt:Optional[str],
                                            dialog_record_str: Optional[str], 
                                            generate_text_list: Optional[List],
                                            clue_information: Optional[List]):


        """
        dialog_record_str example:
            访客搜索词:搜索词:厌学情绪严重不想去学校怎么办
            (round 1)assistant:引导语:现在是什么情况？可以大概描述一下，这边好帮你分析<sep>孩子现在多大了？男孩女孩？<sep>这些症状出现多长时间了呢？<sep>你好，能看到我的消息吗？
            (round 1)user:访客问题:14周岁 女孩 两年多
            (round 2)assistant:那在这两年里，孩子是否因为学习压力、人际关系或个人兴趣等方面感到困扰？
            (round 2)user:访客问题:都有
            (round 3)assistant:对于学习任务和社交活动，她是否有表现出抵触或者逃避的态度？<sep>在日常生活中，有没有发现她的情绪变化较大，比如易怒、闷闷不乐等？<sep>您好，还在吗？<sep>您微信多少，我加您，我朋友圈有很多案例可以发给你参考下，这样你了解的也更清楚一些，或者您也可以加我微信：17752993722
            (round 3)user:跟陌生人说话很害怕 心里很紧张 不知道说什么 一想到要去上学就想哭 特别不想去 现在暑假过去快一个月 一想到还有一个月就开学就哭

        generate_text_list example:
            ['孩子对陌生人的交流有障碍，并且对即将到来的学习生活感到焦虑甚至哭泣。<sep>请问，平时在学校有没有遇到让她特别烦恼的事情，比如被欺负或是成绩不理想？', '孩子对陌生人的交流有障碍，并且对上学有强烈的抗拒感。<sep>除了情绪上的反应外，是否有特定的科目或学习内容让她觉得难以接受或是特别不喜欢？', '除了对学校的恐惧感外，孩子是否还存在社交焦虑，比如在陌生环境中难以融入或与人交流时感觉不安？<sep>这种情况多久了？', '除了对上学有恐惧感外，平时在学校是否有受到欺凌或是被排挤的情况？', '除了对学校有恐惧感外，孩子平时在家是否愿意主动交流，还是说更倾向于独处？']
        
        clue_information exmaple:
            病症识别：厌学情绪、社交恐惧
            访客画像：14岁女孩、厌学情绪持续两年多、社交恐惧
            相关知识:厌学情绪可能由学业压力、人际关系问题引起，社交恐惧表现为对社交场合的极度焦虑
            访客意图：描述厌学情绪及社交恐惧症状
            访客潜在需求：寻求改善厌学情绪及社交恐惧的方法
            主要目的:帮助孩子克服厌学情绪和社交恐惧
        """
        cur_prompt = generate_prompt.replace("dialog_record_str", dialog_record_str).replace("generate_text_list", str(generate_text_list)).replace("clue_information", clue_information)
        res = self.requsest_llm(formatted_dialog=cur_prompt)
        if "</think>" in res:
            res = res.split("</think>")[1]
        res = ast.literal_eval(res)
        # print("****rag候选话术****:\n",  res)
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


    def convert_my_format_to_center(self, history):
        """
        转换成中控的形式， 从系统提示词中抽取出 搜索词，引导语。

        history example：
        [{'role': 'system', 'content': '你是儿科GPT,对话过程中语义自然，不要过于礼貌，你的核心目标：是获取访客的联系方式。当前时间：2025-07-23 17:39:21 \n搜索词:厌学情绪严重不想去学校怎么办\n引导语:现在是什么情况？可以大概描述一下，这边好帮你分析<sep>孩子现在多大了？男孩女孩？<sep>这些症状出现多长时间了呢？<sep>你好，能看到我的消息吗？'}, 
        {'role': 'user', 'content': '访客问题:14周岁 女孩 两年多'}, 
        {'role': 'assistant', 'content': '那在这两年里，孩子是否因为学习压力、人际关系或个人兴趣等方面感到困扰？'}, 
        {'role': 'user', 'content': '访客问题:都有'}, 
        {'role': 'assistant', 'content': '对于学习任务和社交活动，她是否有表现出抵触或者逃避的态度？<sep>在日常生活中，有没有发现她的情绪变化较大，比如易怒、闷闷不乐等？<sep>您好，还在吗？<sep>您微信多少，我加您，我朋友圈有很多案例可以发给你参考下，这样你了解的也更清楚一些，或者您也可以加我微信：17752993722'}, 
        {'role': 'user', 'content': '访客问题:跟陌生人说话很害怕 心里很紧张 不知道说什么 一想到要去上学就想哭 特别不想去 现在暑假过去快一个月 一想到还有一个月就开学就哭\n\naction:<一级:问诊><二级：*>'}]
        """
        def convert(dialog):
            new_dialog = []
            for line in dialog:
                if line["role"] == "user":
                    new_dialog.append({"role": "CLIENT", "sentence": line["content"]})
                if line["role"] == "assistant":
                    new_dialog.append({"role": "SERVER", "sentence": line["content"]})
            return new_dialog
        new_msg = history[1:-1]
        _, search_text, guide_text = history[0]["content"].replace("你是儿科高级咨询师\n你的核心目标是获取访客联系方式。 ", "").split("\n")
        new_msg.insert(0, {"role": "user", "content": search_text})
        new_msg.insert(1, {"role": "assistant", "content": guide_text})
        user_utter = history[-1]["content"]
        if "action" in user_utter:
            user_utter = user_utter.split("action")[0].replace("访客问题:","")
        return search_text, convert(new_msg), user_utter


    def pipeline(self, init_data: Optional[List],
                       clue_prpmpt: Optional[str],
                       large_llm_generate_prompt: Optional[str],
                       reward_prompt: Optional[str],
                       dpoFormatData_save_path: Optional[Path],
                       sftFormatData_save_path: Optional[Path]):
        message_id = 0
        for item in tqdm(init_data, total=len(init_data), desc="construct:"):
            # try:
                message_id += 1
                history = item["messages"]
                prompt_info = item["prompt_info"]
                topic = item["topic"]
                candidates = item["candidates"]
                print(item["messages"])
                print("###"*50)

                # 数据转换
                search_text, dialog_record, user_utterance = self.convert_my_format_to_center(history)

                # 线索提取
                if len(clue_prpmpt) > 0:
                    clue_informations = self.get_clue_by_llm(clue_prpmpt=clue_prpmpt,
                                                            dialogure=dialog_record, 
                                                            utterance=user_utterance)
                else:
                    clue_informations = ""

                # 9990机器回答
                native_dialogure_chat_llm_generate_text_list = self.assistant_model.post_server_url_test(
                    dialog_record,
                    dialogId=message_id,
                    keyword=search_text,
                    utterance=user_utterance,
                    limit=5,
                    promptInfo=prompt_info,
                    topic = topic
                )

                dialog_record_str = convert_general_to_dialogue_str(dialog_record, user_utterance)

                ### 根据本地小模型目前生成的话术和历史对话，本地大模型线索总结再生产 ###
                large_llm_candidates = self.generate_candidates_by_large_llm(generate_prompt=large_llm_generate_prompt,
                                                                     dialog_record_str=dialog_record_str, 
                                                                     generate_text_list=native_dialogure_chat_llm_generate_text_list,
                                                                     clue_information=clue_informations)

                print("****本地大模型目前生成话术****:\n", large_llm_candidates)
                print("****线上模型历史生成话术****:\n", candidates)
                print("****本地小模型目前生成话术****:\n", native_dialogure_chat_llm_generate_text_list)
                print("###"*50)
                # 合并本地小模型生成的回复、本地大模型生成的回复和原始数据中的候选回复，形成候选池
                native_dialogure_chat_llm_generate_text_list.extend(large_llm_candidates)
                native_dialogure_chat_llm_generate_text_list.extend(candidates)


                ### 加入后处理函数 ### 
                print(f"****候选语句个数为****:{len(native_dialogure_chat_llm_generate_text_list)}")
                print(native_dialogure_chat_llm_generate_text_list)
                print("###"*50)
                native_dialogure_chat_llm_generate_text_list = self.post_process_sim_model.deduplicate_candidates(candidates=native_dialogure_chat_llm_generate_text_list)
                print(f"****去重后话术个数为****:{len(native_dialogure_chat_llm_generate_text_list)}")
                print("###"*50)
                print(f"****去重后话术****:\n{native_dialogure_chat_llm_generate_text_list}")
                print("###"*50)
                if self.is_use_postprocess_action_model:
                    native_dialogure_chat_llm_generate_text_list = self.post_process_action_model.process_by_action(native_dialogure_chat_llm_generate_text_list, server_round=(len(dialog_record)-1)//2+1) 
                    print(f"****action规则过滤后话术个数为****:{len(native_dialogure_chat_llm_generate_text_list)}")
                    print(f"****action规则过滤后话术****:\n{native_dialogure_chat_llm_generate_text_list}")
                    
                reward_res = self.get_candidates_scores(reward_prompt=reward_prompt,
                                                        dialog_record_str=dialog_record_str,
                                                        candidates=native_dialogure_chat_llm_generate_text_list)
                rft_history = dialog_record.copy()
                if reward_res and isinstance(reward_res, dict):
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
                    preference_pairs = get_random_chosen_rejected_pair(reward_res, threshold=3)
                    if preference_pairs:
                        chosen_text = preference_pairs["chosen"]
                        rejected_text = preference_pairs["rejected"]
                        chosen_pair = append_and_convert("assistant", chosen_text, history=dpo_history)
                        rejected_pair = append_and_convert("assistant", rejected_text, history=dpo_history)
                        item = {"chosen": chosen_pair, "rejected":rejected_pair}
                        item = add_system_prompt_for_train_data([item])
                        item = convert_chosen_rejected_to_prompt(item)[0]
                        with open(dpoFormatData_save_path, "a") as f:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")

                    highest_score_sentence =  max(reward_res, key=reward_res.get)
                    dialog_record.append({"role": "SERVER", "sentence": highest_score_sentence})
                    rft_history.append({"role": "SERVER", "sentence": highest_score_sentence})
                    
                
                    print("---"*50)
                    print(f"当前对话：{dialog_record}")
                    print("---"*50)
                    print()
                with open(sftFormatData_save_path, "a") as file:
                    rft_history = self.convert_to_qwen_format(rft_history)
                    file.write(json.dumps({"messages": rft_history}, ensure_ascii=False) + "\n")
            # except KeyboardInterrupt:
            #     break
            # except:
            #     continue

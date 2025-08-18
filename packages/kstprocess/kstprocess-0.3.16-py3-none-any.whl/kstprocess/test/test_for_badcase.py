import pandas as pd
from typing import Optional, List, Dict
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch
from util.llm_server import request_native_llm_server
import json
from tqdm import tqdm
from kstprocess.util.format_convert import convert_qwen_format_to_elsxinfo
import requests
from peft import PeftModel

class QwenBatchInference(object):
    def __init__(self, model_path, tokenizer_path, lora_path=None) -> None:
        """
        Args:
            model_path (str): 基础模型路径
            tokenizer_path (str): 分词器路径
            lora_path (str, optional): LoRA 权重路径。默认为 None。
        """
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path,
            padding_side='left',
        )

        # 加载基础模型
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            pad_token_id=self.tokenizer.pad_token_id,
            torch_dtype=torch.bfloat16,
        )

        # 如果提供了 LoRA 权重路径，则加载 LoRA 模型
        if lora_path is not None:
            self.model = PeftModel.from_pretrained(
                self.model,
                lora_path,
                torch_dtype=torch.bfloat16,
            )

        self.max_length = 1400
        self.model.generation_config = GenerationConfig.from_pretrained(
            model_path,
            pad_token_id=self.tokenizer.pad_token_id,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1
        )
        self.model.cuda().eval()
    
    def get_answer(self, llm_reward_url:Optional[str], messages: Optional[List[Dict]], limit:Optional[int]):
        
        t_messages = self.tokenizer.apply_chat_template(
                messages["messages"],
                tokenize=False,
                add_generation_prompt=True
            )
        input_list = [t_messages for _ in range(limit) ]
        batch_input_ids = self.tokenizer.batch_encode_plus(input_list, truncation=True,padding=True, return_tensors='pt').input_ids.cuda()
        generated_ids = self.model.generate(
        batch_input_ids,
        eos_token_id = 151645,     
        max_new_tokens=1024,
        )     
        generated_text_list = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        candidates = []
        for item in generated_text_list:
            candidates.append(item.split("assistant")[-1])
        history = [line["content"] for line in  messages["messages"]]
        if limit != 1:
            sent = get_best_candidate_from_llm(llm_reward_url, history, candidates)
        else:
            sent = candidates[0]
        return candidates, sent

def get_best_candidate_from_llm(reward_model_url, history, candidates):
    param = {"history": history, 
             "candidates": candidates,
             "domain": ""}
    res = requests.post(reward_model_url, json=param)
    res = json.loads(res.text)
    return max(res["response"], key=res["response"].get)


THINKSCOREPROMPT = """
### 现在需要你对模型重新生成之后的结果进行打分，看是否解决原来生成中存在的问题。请你对生成的话术进行评分。 ###

### 输入对话历史 ###
messages
### 原始回复 ###
old_answer
### 原始回复中存在的问题 ###
exist_problem
### 新生成回复 ###
new_generate
### 输出要求 ###
1. 如果新生成回复，原始回复中存在的问题，给出0
2. 如果新生成回复，存在逻辑性，知识性，事实性的问题，给出0
3. 如果新生成回复，符合要求，给出1
输出格式：
{"score": "0 or 1"}

"""


THINKDIFPROMPT = """
### 现在需要你对模型重新生成之后的结果进行打分，看是否解决原来生成中存在的问题(如果没有出现原始回复中的问题，同时符合逻辑性，也算是一种合理性)。请你对生成的话术进行评分。 ###

### 输入对话历史 ###
messages
### 原始回复 ###
old_answer
### 原始回复中存在的问题 ###
exist_problem
### 新生成回复 ###
new_generate
### 输出要求 ###
如果新的生成回复比旧回复好，则输出1
如果新的生成回复比旧回复差，则输出0
输出格式：
{"score": "0 or 1"}

"""

class AutoTestForLLM():
    def __init__(self,  domain: str, 
                        sensitive_words_file_path:Path,
                        tokenizer_path:Optional[Path]="/data/public/Qwen/Qwen2.5/Qwen2.5-7B-Instruct",
                        model_path:Optional[Path]="/data/yuzj/vscodeWorkSpace/paediatrics_rl/saved_model/dapo_model33",
                        lora_path: Optional[Path]=None,
                        ) -> None:
        with open(sensitive_words_file_path) as f:
            self.sensitive_words_file = json.load(f)
        self.domain = domain
        self.my_model = QwenBatchInference(tokenizer_path=tokenizer_path, model_path=model_path, lora_path=lora_path)
        self.sensitive_words = self.sensitive_words_file.get(self.domain, [])

    def contains_sensitive_word(self, sentence: str) -> bool:
        """检查句子中是否包含任何敏感词"""
        for word in self.sensitive_words:
            if word in sentence:
                return True
        return False

    def count_sensitive_sentences(self, sentences: list):
        total_count = len(sentences)
        sensitive_count = sum(self.contains_sensitive_word(sentence) for sentence in sentences)
        ratio = sensitive_count / total_count if total_count > 0 else 0
        return sensitive_count, total_count, ratio

    def auto_annotation_for_log_multi_sheet(
        self,
        xlsx_file_path: Optional[Path] = None,
        save_path: Optional[Path] = "badcase优化结果.xlsx",
        openai_api_base: Optional[str] = "http://192.168.1.66:8945/v1",
        limit: Optional[int] = 5,
        llm_reward_url: Optional[str] = "",
        test_sheet_name:Optional[List]=None,
        is_use_think=False,
    ):
        def get_llm_score(prompt):
            res = request_native_llm_server(prompt, enable_close_think=False, openai_api_base=openai_api_base)
            try:
                score = eval(res.split("</think>")[1].lstrip())["score"]
            except Exception as e:
                print(f"评分解析失败: {e}")
                score = -1
            return res, score

        # 读取所有 sheet
        all_sheets = pd.read_excel(xlsx_file_path, sheet_name=None)

        # 用于存储每个 sheet 的处理结果
        results = {}

        for sheet_name, init_data in all_sheets.items():
            print(sheet_name)
            if (test_sheet_name and sheet_name in test_sheet_name) or not test_sheet_name:
                new_data = []
                num1, num2, whole_ratio = 0, 0, 0
                
                for i, line in tqdm(init_data.iterrows(), total=len(init_data), desc=f"评估中 [{sheet_name}]"):
                    messages = eval(line["messages"])
                    messages_id = line["对话id"]
                    problem_des = line["问题描述"]
                    old_answer = line["生成"]
                    if is_use_think:
                        messages["messages"][-1]["content"] += " /think"
                    else:
                        messages["messages"][-1]["content"] += " /no_think"
                    # 使用 self.my_model 而不是重新初始化
                    candidates, cur_model_answer = self.my_model.get_answer(
                        llm_reward_url=llm_reward_url,
                        messages=messages,
                        limit=limit
                    )
                    cur_prompt1 = THINKDIFPROMPT.replace("messages", str(messages)) \
                                            .replace("old_answer", old_answer) \
                                            .replace("exist_problem", problem_des) \
                                            .replace("new_generate", cur_model_answer)
                    cur_prompt2 = THINKSCOREPROMPT.replace("messages", str(messages)) \
                                                .replace("old_answer", old_answer) \
                                                .replace("exist_problem", problem_des) \
                                                .replace("new_generate", cur_model_answer)

                    if self.domain in ["andrology_ks"] and "男科快手" == sheet_name:
                        _, _, cur_ratio = self.count_sensitive_sentences(candidates)
                    else:
                        cur_ratio = 0
                    whole_ratio += cur_ratio

                    think1, score1 = get_llm_score(cur_prompt1)
                    think2, score2 = get_llm_score(cur_prompt2)

                    if int(score1) == 1:
                        num1 += 1
                    if int(score2) == 1:
                        num2 += 1

                    new_data.append([
                        messages_id, problem_des,
                        convert_qwen_format_to_elsxinfo(messages),
                        old_answer, cur_model_answer,
                        score1, score2, think1, think2
                    ])

                if len(init_data) != 0:    
                    print(f"[{sheet_name}] win rate: {num1 / len(init_data):.2%}")
                    print(f"[{sheet_name}] solve rate: {num2 / len(init_data):.2%}")
                    print(f"[{sheet_name}] sensitive rate: {whole_ratio / len(init_data):.2%}")

                result_df = pd.DataFrame(new_data, columns=[
                    "对话id", "问题描述", "messages", "生成", "优化后回复",
                    "win score", "solve score", "win think", "solve think"
                ])
                results[sheet_name] = result_df

                # 将所有 sheet 写入新文件
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    for sheet_name, df in results.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                print(f"已将所有 sheet 处理完成并保存至：{save_path}")

        
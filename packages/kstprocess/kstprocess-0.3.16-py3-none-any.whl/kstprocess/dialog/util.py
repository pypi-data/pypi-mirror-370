from typing import Optional, List
import re
import json
from typing import Optional, List
import falcon
import setproctitle
import os
from openai import OpenAI
import configparser
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
import torch
from loguru import logger
from transformers import AutoTokenizer
from typing import Optional, List, Dict
import json
import re
from vllm import LLM, SamplingParams
from ltp import StnSplit
from kstprocess.dialog.postprocess import ActionProcessor, SentPostProcess
from abc import ABC, abstractmethod
import copy



class QwenBatchInference(object):
    """
        动态 p值。
        支持 transformers, vllm, openai 形式启动。
    """
    def __init__(self, llm_config) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            llm_config["tokenizer_path"],
            padding_side='left',
        )
        self.llm_config = llm_config
        self.deployment_type = llm_config["deployment_type"]
        # 加载分句模型
        self.sentence_split_model = StnSplit()
        self.max_tokens = int(self.llm_config["max_tokens"])
        #### transformers 启动  ####
        if self.deployment_type in ["transformers"]:
            self.model = AutoModelForCausalLM.from_pretrained(
                            llm_config["model_path"],
                            pad_token_id=self.tokenizer.pad_token_id,
                            torch_dtype=torch.bfloat16,)
            self.max_length =  llm_config["max_length"]
            self.model.generation_config = GenerationConfig.from_pretrained(self.llm_config["model_path"],
                                                                            pad_token_id=self.tokenizer.pad_token_id,
                                                                            do_sample=self.llm_config["do_sample"],
                                                                            top_p=float(self.llm_config["top_p"]),
                                                                            repetition_penalty=float(self.llm_config["repetition_penalty"]),
                                                                            temperature=float(self.llm_config["temperature"]),
                                                                            )
            self.model.cuda().eval()
        elif self.deployment_type in ["vllm", "Vllm"]:
            self.model = LLM(model=self.llm_config["model_path"],
                             max_model_len=self.max_length,
                             enforce_eager=True,
                             trust_remote_code=True,
                             enable_prefix_caching=True,
                             dtype="auto")
            self.sampling_params = SamplingParams(top_p=float(self.llm_config["top_p"]),
                                                  temperature=float(self.llm_config["temperature"]),
                                                  repetition_penalty=float(self.llm_config["repetition_penalty"]),
                                                  max_tokens=self.max_tokens)
        elif self.deployment_type in ["openAI_server"]:
            self.base_url =  llm_config["base_url"] 
            self.local_vllm_client = OpenAI(api_key = "zj",
                base_url=self.base_url)
        
        #### 加载后处理模块 ####
        self.sent_post_process_cursor = SentPostProcess()
        self.actionProcess = ActionProcessor()


    """
    常规问答和模板问答应该采取两种形式。
    模板问答续写模式，常规问答采用rag形式。
    模板问答的优先级高于，常规问答。

    generate_mode = ["completion", "rag", "action", "inference"]
    
    """
    def apply_completion_chat_template(self, messages:Optional[List[Dict]]=None,
                                             template_qa:Optional[List]=None,
                                             action_label_list: Optional[List]=None,
                                             clue_information=None,
                                             generate_mode:Optional[str]=None,
                                             limit:Optional[int]=None)->Optional[List]:
        actions = ""
        if self.llm_config["is_use_action_v2"] == "True" and generate_mode != "warm_up":
            level_1_group, level_2_group = self.actionProcess.get_group_action(action_label_list)
            level_1_group_str = ",".join(level_1_group)
            if level_2_group == []:
                level_2_group_str = "*"
            else:
                level_2_group_str = ",".join(level_2_group)
            actions = f"<一级:{level_1_group_str}><二级：{level_2_group_str}>"
        elif self.llm_config["is_use_action_v2"] == "True" and generate_mode == "warm_up":
            actions = []
            for x in action_label_list:
                level_1_group, level_2_group = self.actionProcess.get_group_action(x)
                level_1_group_str = ",".join(level_1_group)
                if level_2_group == []:
                    level_2_group_str = "*"
                else:
                    level_2_group_str = ",".join(level_2_group)
                cur_ac = f"<一级:{level_1_group_str}><二级：{level_2_group_str}>"
                actions.append(cur_ac)

        t_messages = ""    
        if self.llm_config["action_position"] == "user" and generate_mode!="warm_up":
            # if self.llm_config["is_use_clue_prefix"] == "True":
            #     messages[-1]["content"] +=  f"\nclue:{clue_information}\naction:{actions}"
            # else:
            #     messages[-1]["content"] +=  f"\naction:{actions}"
            messages[-1]["content"] +=  f"\naction:{actions}"
            t_messages = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            if generate_mode in ["rag", "completion"]:
                t_messages += f"{template_qa}<sep>"
        elif self.llm_config["action_position"] == "assistant" and generate_mode!="warm_up":
            t_messages = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            if self.llm_config["is_use_clue_prefix"] and generate_mode in ["rag", "completion"]:
                t_messages += f"\nclue:{clue_information}\n{actions}\t||\t{template_qa}<sep>"
            elif not self.llm_config["is_use_clue_prefix"] and generate_mode in ["rag", "completion"]:
                t_messages += f"\n{actions}\t||\t{template_qa}<sep>"
            else:
                t_messages += f"\n{actions}\t||\t"
        elif self.llm_config["action_position"] == "user" and generate_mode=="warm_up":
            t_messages = []
            for ac in actions:
                cur_messages = copy.deepcopy(messages)
                cur_messages[-1]["content"] +=  f"\naction:{ac}"
                t_message = self.tokenizer.apply_chat_template(
                        cur_messages,
                        tokenize=False,
                        add_generation_prompt=True)
                t_messages.append(t_message)
        if generate_mode=="warm_up":
            return t_messages
        else:
            return [t_messages for _ in range(limit)]     
        
    def generate_text_list(self, generate_mode: Optional[str], 
                                 qwen_format_history:Optional[List],
                                 text_list: Optional[List]):
        """
            qwen_format_history, text_list 都是 拼接之后的结果
        """
        if generate_mode == "warm_up" or  generate_mode == "action_warmup" :
            self.model.generation_config.temperature = 0.8
            self.model.generation_config.top=  0.9
            logger.info(f"AI warm_up: temperature({self.model.generation_config.temperature}) top({self.model.generation_config.top})")
        else:
            self.model.generation_config.temperature =float(self.llm_config["temperature"])
            self.model.generation_config.top =  float(self.llm_config["top_p"])
            logger.info(f"AI chat: temperature({self.model.generation_config.temperature}) top({self.model.generation_config.top})")

        if self.deployment_type in ["transformers"]:
            batch_input_ids = self.tokenizer.batch_encode_plus(text_list, truncation=True,padding=True, return_tensors='pt').input_ids.cuda()
            generated_ids = self.model.generate(
            batch_input_ids,
            eos_token_id = 151645,     
            max_new_tokens=self.max_tokens,
            )     
            generated_text_list = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        elif self.deployment_type in ["vllm", "VLLM", "vLLM"]:
            outputs = self.model.generate(text_list, self.sampling_params, use_tqdm=False)
            for output in outputs:
                generated_text = output.outputs[0].text
                generated_text_list.append(generated_text)

        elif self.deployment_type in ["openAI_server"]:
            response = self.local_vllm_client.chat.completions.create(
                model="paediastrics_server",  
                messages=qwen_format_history,
                top_p=self.model.generation_config.top,
                max_tokens=self.max_tokens,
                temperature=self.model.generation_config.temperature,
            )
            for choice in response.choices:
                content = choice.message.content
                generated_text_list.append(content)

        if self.deployment_type not in ["openAI_server", "vllm", "VLLM", "vLLM"]:
            end_list = []
            for _, res in enumerate(generated_text_list):
                sent = res.split("assistant")[-1]
                end_list.append(sent)
            
            generated_text_list = end_list

        return generated_text_list




class MedicalAdvertisingChatBotGenerator(ABC):
    def __init__(self, config, domain, source) -> None:
        self.config = config
        setproctitle.setproctitle(self.config["generate_config"]["setproctitle"])
        os.environ["CUDA_VISIBLE_DEVICES"]=self.config["generate_config"]["devices"]
        self.domain = domain
        self.source = source

    def add_user_utterance_to_history(self, history:Optional[List], query:Optional[str])->Optional[List]:
        new_history = history.copy()
        new_history.append( 
                {
                    "msgId": "",
                    "role": "CLIENT",
                    'subType': 'INPUT_VISITOR',
                    "sentence": query
                }
                )
        return new_history
    
    ### 计算中控对话的轮次 ###
    def count_dialogure_round(self, dialog_record:Optional[List]):
        """
        统计对话的轮数，这里的 "轮数" 定义为用户连续发言的次数
        例子：
        ['client', 'server', 'client', 'server', 'client', 'client', 'server']
        这里的轮次为3
        """
        r0 = [record["role"].lower() for record in dialog_record]
        r0t = "".join(r0)
        r0t = r0t.replace("client","C")
        r0t = re.findall("C{1,}", r0t)
        self.server_round = len(r0t)


    def add_prompt_to_history_and_convert_history_format_to_qwen(self, prompt:Optional[str], history:Optional[List[Dict]]):
        """
        将原始对话历史和提示词（prompt）转换为符合 Qwen 模型输入格式的对话列表
        """
        
        if len(prompt) > 0:
            format_history = [{"role": "system", "content": prompt}]
        else:
            format_history = []
        i = 0
        while i < len(history):
            cur_query = ""
            # "ROBOT_GUIDE"  引导语  "ROBOT_GREETING" 问候语
            while (i<len(history)) and "subType" in history[i].keys() and history[i]["subType"] in ["kw", "skw", "ROBOT_GREETING", "ROBOT_GUIDE"]:
                i += 1
            while (i< len(history) and history[i]["role"] == "CLIENT" ):
                cur_query += history[i]["sentence"] + "<sep>"
                i += 1
            if len(cur_query) > 0:
                cur_query = re.sub("^<sep>", "", cur_query)
                cur_query = re.sub("<sep>$", "", cur_query)
                format_history.append({"role":"user", "content": "访客问题:"+cur_query.rstrip("<sep>")})
            cur_response = ""
            while i< len(history) and history[i]["role"] == "SERVER":
                cur_response += history[i]["sentence"] + "<sep>"
                i += 1
            if len(cur_response) > 0:
                cur_response = re.sub("^<sep>", "", cur_response)
                cur_response = re.sub("<sep>$", "", cur_response)
                format_history.append({"role":"assistant", "content":cur_response.rstrip("<sep>")}) 
        logger.info(f'current prompt length:{sum([len(item["content"]) for item in format_history])}')
        return format_history

    @abstractmethod
    def pipeline_for_AI_warmupWord(self):
        pass
    
    @abstractmethod
    def pipeline_for_AI_chat():
        pass

    def on_post(self, requests_data, response_data):
        ### 接受参数 ###
        input_params = json.load(requests_data.bounded_stream)
        self.input_params = input_params
        self.session_id = input_params.get("dialogId")
        self.task_type = input_params.get("task_type")
        if self.task_type in ["dialog", "smartScript"]:
            response, basic_action_label_list = self.pipeline_for_AI_chat()
        elif self.task_type in ["warmup"]:
            response = self.pipeline_for_AI_warmupWord()
            prompt_info = self.input_params.get("promptInfo", {'prompt_mapping': [], 'prompt_acp': [], 'prompt_artificial': []})
            basic_action_label_list = prompt_info["prompt_artificial"]
        else:
            raise NotImplementedError(f"not support this task_type: {self.task_type}")


        result = {
            "code": 200,
            "session_id": self.session_id,
            "data": response,
            "action": basic_action_label_list,
            "version": self.config["generate_config"]["version"], 
        }

        response_data.text = json.dumps(result)
        response_data.status = falcon.HTTP_200
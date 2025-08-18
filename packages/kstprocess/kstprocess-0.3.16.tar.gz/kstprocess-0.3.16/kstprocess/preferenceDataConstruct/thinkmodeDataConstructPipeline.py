from kstprocess.util.util import read_action_file, read_jsonl_from_path
from util.llm_server import request_native_llm_server
from util.postprocess.action_util import ActionProcessor
import copy
import json
from typing import Optional, List, Dict
from pathlib import Path
from tqdm import tqdm


THINKCONSTRUCTPROMPT = """
###现在需要你帮忙输出思维链###：
    根据给出的历史：
        history
    给出回复：
        response
    思考你作为高级咨询师为啥会这么说。
对话的任务大概的形式为 通过一系列的问诊，答疑，套电，弄清访客的主诉和具体的病症，给出相应的福利，促使访客留下联系方式。
### 按要求输出格式 ###
response 不要输出额外内容了
### 输出 ### 
"""

REJECTSAMPLEPROMPT = """
### 拒绝采样规则 ###
请你对下列 思考过程和最终回复的相关性，逻辑推理性进行评判。
### 对话 ###
dialog
### 输出格式 ###
拒绝/接受, 不要输出其他
### 输出 ###
"""

def loop(action_file_path: Optional[Path]="./config/paediastric_action.json",
         action_model_url: Optional[str]="http://192.168.1.67:8413/kicp-micro-common-action-service",
         init_data_path:Optional[Path]="./构建推理的数据.jsonl",
         save_path:Optional[Path]="./生成的思维链数据.jsonl",
         openai_api_base:Optional[str]="http://192.168.1.67:8888/v1"):
    ### 加载初始数据 ###
    action_map = read_action_file(file_path=action_file_path)
    cur =  ActionProcessor(action_model_url=action_model_url,
                            action_map=action_map)
    init_data = read_jsonl_from_path(init_data_path)


    for line in tqdm(init_data, total=len(init_data), desc="infer"):
        msg = line["messages"]

        for i, item in tqdm(enumerate(msg), total=len(msg), desc="dialog"):
            try:
                if item["role"] == "assistant" and i >2:
                    response = item["content"]
                    ac_count = cur.count_response_action_label_num(response)["action_counts"]
                    if ac_count["问诊"] > 0 and ac_count["套电"] == 0:
                        history_list = [x["role"]+":"+x["content"] for x in  msg[:i]]
                        history_str = "\n".join(history_list)
                        ### 输出 思维链数据  ###
                        cur_prompt = THINKCONSTRUCTPROMPT.replace("history", history_str).replace("response", response)
                        res = request_native_llm_server(formatted_dialog=cur_prompt, 
                                                        enable_close_think=False,
                                                        openai_api_base=openai_api_base)
                        
                        think_content, response_text = res.split("</think>")
                        think_content = think_content.lstrip("<think>")
                        response_text =  response_text.strip(" ").strip("\n")

                        cur_messages = copy.deepcopy(msg[:i])
                        if response_text == response:
                            cur_messages.append({"role": "assistant", "content": "<think>"+think_content+"</think>" +response})

                            dialog = [x["role"]+":"+x["content"] for x in cur_messages]

                            ### 拒绝采样--使用大模型再次验证 ###
                            cur_prompt2 = REJECTSAMPLEPROMPT.replace("dialog", str(dialog))
                            res = request_native_llm_server(formatted_dialog=cur_prompt2, 
                                                            enable_close_think=True, 
                                                            openai_api_base=openai_api_base)
                            if "接受" in res:
                                with open(save_path, "a") as file:
                                    file.write(json.dumps({"messages": cur_messages}, ensure_ascii=False)+"\n")
            except KeyboardInterrupt:
                return
            except:
                continue

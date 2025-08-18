from kstprocess.util.util import read_jsonl_from_path
import pandas as pd
import os
from typing import Optional, List, Dict
import re
from pathlib import Path
from tqdm import tqdm
import json
from kstprocess.util.format_convert import add_system_prompt_for_train_data, add_action_for_train_data_batch


def convert_preference_data_to_annotation_excel(file_path:Optional[Path], 
                                                save_path:Optional[Path],
                                                domain:Optional[str]="儿科"):
    """
    将指定格式的 JSONL 数据(一般是模型选择出来的偏好数据)转换为偏好标注 Excel 表格
    参数:
        input_path (str): 输入 JSONL 文件路径
        output_path (str): 输出 Excel 文件路径

    目的： 转成 给标注组的 可以导入的数据
    """
    init_data = read_jsonl_from_path(file_path)
    new_data = []
    for i, line in enumerate(init_data):
        cur_dialog_id = i
        _, search_text, guide_text = line["prompt"][0]["content"].split("\n")
        history = ["CLIENT:"+search_text.replace("访客搜索词:", "").replace("搜索词:", ""), "SERVER:"+guide_text.replace("引导语:", "")]
        for item in line["prompt"][1:]:
            if item["role"] =="user":
                utr = "CLIENT:"+item["content"].replace("访客问题:", "")
                if "action" in utr:
                    utr = utr.split("\naction")[0]
                history.append(utr)
            else:
                history.append("SERVER:"+item["content"])
        history = "\n".join(history)
        chosen_content = line["chosen"][0]["content"]
        rejected_content = line["rejected"][0]["content"]
        new_data.append([cur_dialog_id, history, "(1)"+chosen_content, domain, ""])
        new_data.append([cur_dialog_id, history, "(2)"+rejected_content, domain, ""])
    new_data = pd.DataFrame(new_data, columns=["dialog_id", "sentence", "generate", "domain", "score"])
    new_data.to_excel(save_path, index=False)



def combine_auto_test_results_to_annotation(path: Optional[Path] = "自动化测试", 
                                            save_path: Optional[Path] = "./采样数据.xlsx",
                                            filtered_dialog_ids:Optional[List]=[]):
    """
    从指定路径下读取多个 Excel 文件（.xlsx 或 .xls），合并其中的数据，
    然后根据唯一的 dialog_id 抽样部分数据，并排除指定的对话 ID 后保存为新的 Excel 文件。
    
    参数说明：
    -------------------
    path : str 或 Path, optional
        自动化测试结果文件所在的目录路径，默认为 "自动化测试"
        
    save_path : str 或 Path, optional
        最终合并并抽样后的数据保存路径，默认为 "./采样数据.xlsx"
        
    filtered_dialog_ids : list, optional
        需要排除的对话 ID 列表，用于过滤异常或已标注的对话记录，默认为空列表 []
    """                            
    init_data = pd.DataFrame()
    path = str(path)
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path) and file_name.endswith(('.xlsx', '.xls')):
            file = pd.read_excel(file_path)
            init_data = pd.concat([init_data, file], ignore_index=True)
    unique_messageids = init_data['dialog_id'].unique()
    if len(unique_messageids) > 50:
        sampled_messageids = pd.Series(unique_messageids).sample(n=50, random_state=1).tolist()
    else:
        sampled_messageids = unique_messageids.tolist()
    
    sampled_messageids = [dialog_id for dialog_id in sampled_messageids if dialog_id not in filtered_dialog_ids]
    sample_result = init_data[init_data['dialog_id'].isin(sampled_messageids)]
    sample_result.to_excel(save_path, index=False)



def convert_history_to_qwen_format(history_str:str)->Optional[List[Dict]]:
    """
    转转 文本形式的对话历史 --》qwen format格式的
    """
    temp_list = history_str.rstrip("\n").split("\n")
    history_list = []

    for line in temp_list:
        if "CLIENT" in line:
            history_list.append({"role": "user", "content": line.lstrip("CLIENT:")})
        else:
            history_list.append({"role": "assistant", "content": line.lstrip("SERVER:")})
    return history_list



def convert_annotation_xlsx_to_jsonl(file_path: Optional[Path],
                                     save_path: Optional[Path],
                                     system_prompt: Optional[str],
                                     action_map:Optional[Dict],
                                     action_model_url:Optional[str],
                                     domain:Optional[str]):
    """
    将标注组标注过的数据进行转换，
        输入是： xlsx 类型的数据，数据格式遵循标注规范
        输出是： jsonl  
    """
    data = pd.read_excel(file_path) 
    first_step_data = []
    for _, line in data.iterrows():
        print(line)
        if type(line["dialog_id"])!=float:
            dialog_id  = line["dialog_id"]
        if type(line["sentence"]) != float:
            history = convert_history_to_qwen_format(line["sentence"])
        generate_text = line["generate"].replace("\xa0", "")
        generate_text = re.sub(r"(\(\d\))(\[.*\])", "", generate_text)
        first_step_data.append([dialog_id, history, generate_text, line["score"]])

    first_step_data = pd.DataFrame(first_step_data, columns=["dialog_id", "history", "candidate", "tag"])

    group_data =  first_step_data.groupby("dialog_id")
    reward_data = []
    for _, group in tqdm(group_data, total=len(group_data), desc="convert..."):
        if "worst" in group["tag"].tolist() and "best" in group["tag"].tolist():
            best_answer =  group[group["tag"]=="best"]["candidate"].str.lower().iloc[0]
            worse_answer =  group[group["tag"]=="worst"]["candidate"].str.lower().iloc[0]
            best_answer = re.sub("\(\d\)", "", best_answer)
            worse_answer = re.sub("\(\d\)", "", worse_answer)
            ### 处理reward数据 ###
            reward_chosen_list = group.iloc[0]["history"].copy()
            reward_rejected_list = group.iloc[0]["history"].copy()
            reward_chosen_list.append({"role": "assistant", "content": best_answer})
            reward_rejected_list.append({"role": "assistant", "content": worse_answer})
            reward_data.append({"chosen": reward_chosen_list, "rejected": reward_rejected_list})
    reward_data = add_system_prompt_for_train_data(init_data=reward_data, 
                                                   system_prompt=system_prompt)
    reward_data = add_action_for_train_data_batch(init_data=reward_data,
                                                  action_map=action_map,
                                                  action_model_url=action_model_url,
                                                  domain=domain)
    with open(save_path, "w") as f:
        for line in reward_data:
            f.write(json.dumps(line, ensure_ascii=False)+"\n")
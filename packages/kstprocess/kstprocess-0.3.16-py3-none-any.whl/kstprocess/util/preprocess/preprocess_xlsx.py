import os
import pandas as pd
import json
import ast
import shutil
from typing import Optional, List
from pathlib import Path
from collections import Counter
from kstprocess.util.util import save_jsonl_from_data



def construct_intent_file(csv_file_path, saved_json_path):
    data = pd.read_csv(csv_file_path)
    dialog_id =  data["dialog_id"].value_counts().keys()
    res = []
    for d_a in dialog_id:
        dialog_windows = data[data["dialog_id"]==d_a]
        sentence_list = dialog_windows["sentence"].tolist()
        role_list = dialog_windows["role"].tolist()
        action_label_list = dialog_windows["action"].tolist()
        intent_list = dialog_windows["intent"].tolist()
        info = []
        for i, sl  in enumerate(sentence_list):
            rl = role_list[i]
            acll =  action_label_list[i]
            intent = intent_list[i]
            if rl == "SERVER":
                info.append({"role": rl, "utterance": sl, "action": acll})
            else:
                if intent or not type(intent)==intent:
                    info.append({"role": "CLIENT", "utterance": sl, "intent": intent})
                else:
                    info.append({"role": "CLIENT", "utterance": sl})

        res.append({"dialog_id":d_a, "content": info})
    print(saved_json_path+"   生成完毕!!!")
    with open(saved_json_path, "w") as f:
        json.dump(res,f, ensure_ascii=False, indent=1)

def jsonl_format(dialog):
    i = 0
    res = []
    while i <len(dialog):
        window_client = 0
        temp = []
        temp_intent = []
        while (i+window_client) < len(dialog) and dialog[i+window_client]["role"] == "CLIENT":
            temp_intent.append(dialog[i+window_client]["intent"])
            temp.append(dialog[i+window_client]["utterance"])
            window_client += 1

        res.append( {"role":"CLIENT", "utterance": temp, "intent": temp_intent})
        i += window_client
        window_server = 0
        temp = []
        temp_action = []
        while (i+window_server) < len(dialog) and dialog[i+window_server]["role"]  == "SERVER":     
            action = ast.literal_eval(dialog[i+window_server]["action"])
            temp.append(dialog[i+window_server]["utterance"])
            temp_action.append(action)
            window_server += 1
        res.append( {"role":"SERVER", "utterance": temp, "action": temp_action})
        i += window_server
    return res

def convert_to_rag_jsonl(json_file_path, saved_jsonl_path):
    with open(saved_jsonl_path, "w") as file:
        with open(json_file_path) as f:
            data = json.load(f)
            for item in data:
                item = jsonl_format(item["content"])

                file.write(json.dumps(item, ensure_ascii=False)+"\n")
    print(saved_jsonl_path+"   生成完毕!!!")

def convert_xlsx_to_jsonl(xlsx_path: Optional[Path],
                            temp_save_path: Optional[Path]):
    if not os.path.exists(temp_save_path):
        os.makedirs(temp_save_path)
    for i, file_name in enumerate(os.listdir(xlsx_path)):
        try:
            process_file_path = os.path.join(xlsx_path, file_name)
            save_json_file_path = os.path.join(temp_save_path, file_name.replace(".csv", ".json"))
            save_jsonl_file_path = os.path.join(temp_save_path, file_name.replace(".csv", ".jsonl"))
            print(f"处理第{i}/{len(os.listdir(xlsx_path))}")
            construct_intent_file(process_file_path, save_json_file_path)
            convert_to_rag_jsonl(save_json_file_path, save_jsonl_file_path)
        except:
            continue
    whole_json = []
    for i, file_name in enumerate(os.listdir(temp_save_path)):
        if file_name.endswith(".jsonl"):
            with open(os.path.join(temp_save_path, file_name)) as f:
                cur_data = f.readlines()
                whole_json.extend(cur_data)
                print(f"合并{len(cur_data)}条数据,当前共{len(whole_json)}")

    print(f"生成了{len(whole_json)}条jsonl数据")
    print(f"删除{temp_save_path}下的所有数据")
    shutil.rmtree(temp_save_path)
    return whole_json


def clean_client_intent_none(cur_round_sentence:Optional[List], cur_round_intent: Optional[List]):
    new_sentence_list  = []
    new_intent_list = []
    for i, sent in enumerate(cur_round_sentence):
        cur_intent = cur_round_intent[i]
        if type(cur_intent) != str:
            continue
        else:
            new_sentence_list.append(sent)
            new_intent_list.append(cur_intent)
    return new_sentence_list, new_intent_list

def convert_central_control_format_to_qwen_format(msg:list)->list:
        format_list = []
        i = 0
        while i< len(msg):
            # 每一轮首句，一定是 CLIENT 发问
            cur_query = ""
            while (i< len(msg) and msg[i]["role"] == "CLIENT" ):
                cur_query += "<sep>".join(msg[i]["utterance"]) + "<sep>"
                i += 1

            # 处理 server
            cur_response = ""
            action_list = ""
            while i< len(msg) and msg[i]["role"] == "SERVER":
                cur_ac = []
                for ac in msg[i]["action"]:
                    cur_ac.append(",".join(ac))
                cur_ac =  "<sep>".join(cur_ac)
                action_list +=  cur_ac + "<sep>"
                cur_response += "<sep>".join(msg[i]["utterance"]) + "<sep>"
                i += 1
            cur_query = cur_query.rstrip(" ")
            cur_response = cur_response.rstrip("<sep>")
            if i > 2:
                action_list =  action_list.rstrip("<sep>").replace("<sep>", ",")
                format_list.append({"role": "user", "content": f"访客问题: {cur_query}\n action: {action_list}"}) 
            else:
                format_list.append({"role": "user", "content": cur_query})

            if i > 2:
                format_list.append({"role": "assistant", "content": cur_response})  
            else:
                format_list.append({"role": "assistant", "content": cur_response}) 
            
        return format_list


def read_init_intent_action_jsonl_data(data:Optional[List], 
                                       save_file_path:Optional[Path]):
    preprocess_data = []
    for msg in data:
        msg = json.loads(msg)
        first_msg = []
        for i, chat in enumerate(msg):
            if "SERVER" in chat["role"]:
                cur_round_actions_list = chat["action"]
                cur_round_sentence_list = chat["utterance"]
                first_msg.append({"role": "SERVER", 
                                    "utterance": cur_round_sentence_list, 
                                    "action": cur_round_actions_list})
            else:
                first_msg.append(chat)
    
        # 去除前三轮去除client intent=nan 
        second_msg = []
        for i, chat in enumerate(first_msg):
            if "CLIENT" in chat["role"] and i < 6 and "intent" in chat:
                cur_round_intent_list = chat["intent"]
                cur_round_sentence_list = chat["utterance"]
                processed_sentence_list,  processed_actions_list = clean_client_intent_none(cur_round_sentence_list, cur_round_intent_list)
                if processed_sentence_list:
                    second_msg.append({"role": "CLIENT", 
                                        "utterance": processed_sentence_list, 
                                        "intent": processed_actions_list})
            else:
                second_msg.append(chat)
        
        second_msg = convert_central_control_format_to_qwen_format(second_msg)  
        preprocess_data.append({"messages": second_msg})
    save_jsonl_from_data(preprocess_data, save_file_path)
    return preprocess_data


def preprocess_xlsx_datasets(xlsx_path: Optional[Path],
                             save_file_path: Optional[Path]):
    data = convert_xlsx_to_jsonl(xlsx_path=xlsx_path,
                                temp_save_path="./tmp")
    read_init_intent_action_jsonl_data(data=data, save_file_path=save_file_path)

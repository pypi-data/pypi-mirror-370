from typing import Optional, List, Dict
import copy
from tqdm import tqdm
from kstprocess.util.util import read_jsonl_from_path, save_jsonl_from_data, read_action_file
from kstprocess.util.postprocess.action_util import ActionProcessor
from kstprocess.util.postprocess.duplication_util import DuplicationProcesser
import random


# 转换正博的数据格式到qwen "conversation": [{"human": "皮肤科咨询", "assistant": "关于白斑和白癜风的问题免费在线为您解答！（医生微信/电话：18758724005）【本次对话已加密】<sep><sep>您好，你的白斑在什么部位？"}, {"human": "不是白班<sep><picture>", "assistant": "是什么问题？"}, {"human": "我想知道那个脸颊上的是什么<sep>坑坑的", "assistant": "我这边加载不出来图片<sep>要不你您加我微信发图片我帮您看看<sep>18758724005我的微信，您提示一下我加您也行"}]}
def convert_zb_to_qwen(line):
    conversation = line["conversation"]
    msg = []
    for item in conversation:
        msg.append({"role": "user", "content": item["human"]})
        msg.append({"role": "assistant", "content": item["assistant"]})
    return {"messages": msg}

def clean_zb_quote(text):
    if ")" in text:
        pos = text.index(")") + 1
        return text[pos:]
    else:
        return text
    

"""
转换 {"chosen":[], "rejected": []}
-->  {"prpmpt":[], "chosen":[], "rejected": []}
"""
def convert_chosen_rejected_to_prompt(init_data):
    save_data = []
    for line in init_data:
        new_chosen_msg = line["chosen"]
        new_rejected_msg = line["rejected"]
        save_data.append({
            "prompt": new_chosen_msg[:-1],
            "chosen": new_chosen_msg[-1:],  # 排除第一个元素作为prompt
            "rejected": new_rejected_msg[-1:]  # 排除第一个元素作为prompt
        })
    return save_data




def add_system_prompt_for_train_data(init_data: Optional[List[Dict]],
                                     system_prompt = "你是一个儿科咨询师，你的核心目标：是获取访客的联系方式。"):
    save_data = []
    if "chosen" in init_data[0].keys() and "prompt" not in init_data[0].keys():
        data_type = "dpo"
    elif "messages" in init_data[0].keys():
        data_type = "sft"
    elif "prompt" in init_data[0].keys():
        data_type = "dpo2"
    else:
        raise ValueError("format can't open")

    if data_type == "dpo":
        for line in init_data:
            init_prompt = line["chosen"][:-1]
            chosen_response = line["chosen"][-1]
            rejected_reponse = line["rejected"][-1]
            search_text = init_prompt[0]["content"].replace("搜索词:", "").replace("搜索词：", "")
            guide_text = init_prompt[1]["content"].replace("引导语:", "").replace("引导语：", "")
            init_prompt[-1]["content"] = init_prompt[-1]["content"].rstrip("\n").rstrip("<sep>")
            template = f"{system_prompt}\n 搜索词：{search_text} \n 引导语：{guide_text}" 
            new_prompt = [{"role": "system", "content": template}]
            new_prompt.extend(init_prompt[2:])
            chosen_list = copy.deepcopy(new_prompt)
            rejected_list = copy.deepcopy(new_prompt)
            chosen_list.append(chosen_response)
            rejected_list.append(rejected_reponse)
            new_line = {"chosen": chosen_list, "rejected": rejected_list}
            save_data.append(new_line)
    elif data_type == "dpo2":
        for line in init_data:
            search_text = line["prompt"][0]["content"]
            guide_text = line["prompt"][1]["content"]
            search_text = search_text.replace("搜索词:", "").replace("搜索词：", "")
            guide_text = guide_text.replace("引导语:", "").replace("引导语：", "")
            template = f"{system_prompt}\n 搜索词：{search_text} \n 引导语：{guide_text}" 
            new_prompt = [{"role": "system", "content": template}]
            new_prompt.extend(line["prompt"][2:])
            save_data.append({"prompt": new_prompt, "chosen": line["chosen"], "rejected": line["rejected"]})
    elif data_type == "sft":
        for line in init_data:
            search_text = line["messages"][0]["content"]
            guide_text = line["messages"][1]["content"]
            search_text = search_text.replace("搜索词:", "").replace("搜索词：", "")
            guide_text = guide_text.replace("引导语:", "").replace("引导语：", "")
            template = f"{system_prompt}\n 搜索词：{search_text} \n 引导语：{guide_text}" 
            new_prompt = [{"role": "system", "content": template}]
            new_prompt.extend(line["messages"][2:])
            save_data.append({"messages": new_prompt})
    return save_data


                

def add_action_for_train_data_batch(init_data,
                                    action_model_url,
                                    action_map,
                                    domain):
    save_data = []
    cur = ActionProcessor(action_model_url=action_model_url, action_map= action_map, domain=domain)
    # 判断数据类型
    
    if all(key in init_data[0].keys() for key in ["prompt", "chosen", "rejected"]):
        data_type = "dpo2"
    elif all(key in init_data[0].keys() for key in ["chosen", "rejected"]):
        data_type = "dpo"
    elif "messages" in init_data[0].keys():
        data_type = "sft"
    else:
        raise ValueError("Unsupported data format")
    def process_message_pairs(chosen_rejected_pairs):
        """处理一批chosen和rejected消息"""    
        # 获取actions
        histories = [chosen[-1]["content"] for chosen, _ in chosen_rejected_pairs]
        all_counter = cur.count_response_action_label_num(histories)
        best_actions = []
        for al_c in all_counter:
            flat_action = [a for actions in al_c["sentence_actions"]  for a in actions]
            flat_action = list(set(flat_action))
            if len(flat_action) > 1 and "无" in flat_action:
                flat_action.remove("无")
            best_actions.append(flat_action)
        new_pairs = []
        for idx, ((chosen_msg, rejected_msg), action) in enumerate(zip(chosen_rejected_pairs, best_actions)):
            new_chosen_msg = chosen_msg.copy()
            new_rejected_msg = rejected_msg.copy()
            
            # 更新chosen中的倒数第二个用户消息
            user_uter = chosen_msg[-2]["content"]
            if "action" in user_uter:
                user_uter = user_uter.split("\naction:")[0].replace("访客问题:", "")
  
            action = ",".join(action)
            new_user_uter = f"访客问题:{user_uter}\naction:{action}"
            new_chosen_msg[-2]["content"] = new_user_uter
            
            # 更新rejected中的倒数第二个用户消息，使用相同的action
            user_uter = rejected_msg[-2]["content"]
            if "action" in user_uter:
                user_uter = user_uter.split("\naction:")[0].replace("访客问题:", "")
            new_user_uter = f"访客问题:{user_uter}\naction:{action}"
            new_rejected_msg[-2]["content"] = new_user_uter
            new_pairs.append((new_chosen_msg, new_rejected_msg))
        
        return new_pairs
    
    if data_type == "sft":
        # SFT数据处理逻辑保持不变
        for line in tqdm(init_data, desc="sft_convert", total=len(init_data)):
            msg = line["messages"]
            if msg[0]["role"] == "system":
                new_msg = [msg[0]]
                start = 1
            else:
                start = 0
                new_msg = []
            for i in range(start, len(msg), 2):
                if "action:" in msg[i]["content"]:
                    user_uter =  msg[i]["content"].split("action:")[0].replace("\n", "")
                else:
                    user_uter = msg[i]["content"].replace("\n", "")
                if (i+1) == len(msg):
                    break
                assistant_uter = msg[i+1]["content"]
                if assistant_uter ==  "":
                    assistant_uter = "  "
                try:
                    best_action = cur.get_action_batch(",".join(assistant_uter))[0]
                    best_action = ','.join(best_action)
                    new_user_uter = f"访客问题:{user_uter} \n action:{best_action}"
                    new_msg.append({"role": "user", "content": new_user_uter})
                    new_msg.append({"role": "assistant", "content": assistant_uter})
                except KeyboardInterrupt:
                    break
                except:
                    continue
            save_data.append({"messages": new_msg})

    elif data_type == "dpo":
        batch_size = 10  # 设置批量大小
        for start_idx in tqdm(range(0, len(init_data), batch_size), desc="dpo_convert"):
            try:
                batch = init_data[start_idx:start_idx + batch_size]
                chosen_rejected_pairs = [(line["chosen"], line["rejected"]) for line in batch]
                new_pairs = process_message_pairs(chosen_rejected_pairs)
                
                for ((new_chosen_msg, new_rejected_msg), (_, _)) in zip(new_pairs, chosen_rejected_pairs):
                    save_data.append({
                        "prompt": new_chosen_msg[:-1],
                        "chosen": new_chosen_msg[-1:],  # 排除第一个元素作为prompt
                        "rejected": new_rejected_msg[-1:]  # 排除第一个元素作为prompt
                    })
            except:
                continue
    elif data_type == "dpo2":
        batch_size = 10
        for start_idx in tqdm(range(0, len(init_data), batch_size), desc="dpo_convert"):
            batch = init_data[start_idx:start_idx + batch_size]
            chosen_rejected_pairs = [(line["prompt"]+line["chosen"], line["prompt"]+line["rejected"]) for line in batch]
            new_pairs = process_message_pairs(chosen_rejected_pairs)
            for ((new_chosen_msg, new_rejected_msg), (_, _)) in zip(new_pairs, chosen_rejected_pairs):
                save_data.append({
                    "prompt": new_chosen_msg[:-1],
                    "chosen": new_chosen_msg[-1:],  # 排除第一个元素作为prompt
                    "rejected": new_rejected_msg[-1:]  # 排除第一个元素作为prompt
                })
    return save_data




def process_and_filter_data():
    # 1. 读取原始数据
    raw_data = read_jsonl_from_path("/data/yuzj/vscodeWorkSpace/paediatrics_rl/datasets/0508/sft_v2.jsonl")
    
    # 2. 构造 prompt 数据
    prompt_data = []
    for line in raw_data:
        if len(line["messages"]) > 4:
            try:
                for i, item in enumerate(line["messages"]):
                    if i > 2 and item["role"] == "assistant":
                        prompt_data.append({"messages": line["messages"][:i]})
            except Exception as e:
                print(f"Error processing line: {e}")
                continue

    # 3. 去重处理
    cur = DuplicationProcesser()
    deduplicated_data = cur.duplication_sft_data_loop(prompt_data)

    # 4. 加载 action 配置并构建关键词池
    action_config = read_action_file("./config/paediastric_action.json")
    key_pool = set()
    key_pool.update(action_config.get("问诊", []))
    key_pool.update(action_config.get("套电", []))
    key_pool.update(action_config.get("答疑", []))

    # 5. 过滤符合关键词的数据
    filtered_data = []
    for line in deduplicated_data:
        try:
            content = line["messages"][-1]["content"]
            actions_part = content.split("action:", 1)[1].strip()
            actions = actions_part.replace("、", ",").replace("<sep>", ",").split(",")
            actions = [act.strip() for act in actions]

            if any(act in key_pool for act in actions):
                filtered_data.append(line)
        except (IndexError, KeyError) as e:
            print(f"Skipping line due to parsing error: {e}")
            continue

    # 6. 输出统计信息并保存结果
    print(f"{len(deduplicated_data)} -> {len(filtered_data)}")
    save_jsonl_from_data(filtered_data, "filerter_data.jsonl")



def convert_qwen_format_to_elsxinfo(data):
    """
    转换 qwen的格式到 xlsx可以看的格式
    
    """
    new_msg = []
    for i, line in enumerate(data["messages"]):
        if line["role"] == "user":
            new_msg.append(f"user:{line['content']}")
        else:
            if "prompt" in line["content"]:
                new_msg.append(f"assistant:{line['content'].split('prompt')[1]}")
            else:
                new_msg.append(f"assistant:{line['content']}")
    new_msg_str = "\n".join(new_msg)
    return new_msg_str



def convert_action_system(init_data:Optional[List[Dict]],
                          action_map:Optional[Dict],
                          level_two_tag_mask_ratio:Optional[int]=0.1):
    """
         转换现有的指令格式：
            1.加入一二级标签的映射，让模型明白具体的标签映射
            2.进行mask操作，让模型在一级标签时候也能够有好效果。
    """
    action_processor = ActionProcessor(action_map=action_map)
    if all(key in init_data[0].keys() for key in ["prompt", "chosen", "rejected"]):
        data_type = "dpo2"
    elif all(key in init_data[0].keys() for key in ["chosen", "rejected"]):
        data_type = "dpo"
    elif "messages" in init_data[0].keys():
        data_type = "sft"
    elif "prompt" in init_data[0].keys():
        data_type = "dpo2"
    else:
        raise ValueError("Unsupported data format")
    
    if data_type == "dpo2":
        for line in init_data:
            if "action:" in  line["prompt"][-1]["content"]:
                temp = line["prompt"][-1]["content"].split("action:")
                if len(temp) == 2:
                    uttrance, actions_list = temp
                elif len(temp) == 3:
                    uttrance, actions_list = temp[0], temp[2]
                actions_list = actions_list.split(",")
                level_1_tag_list = list(set([action_processor.get_key_tag(a) for a in actions_list]))
                if random.random() < level_two_tag_mask_ratio:
                    level_2_tag_list = ["*"]
                else:
                    level_2_tag_list = actions_list
                level_1_tag_str = ','.join(level_1_tag_list).lstrip(",").lstrip(",")
                level_2_tag_str = ','.join(level_2_tag_list).lstrip(",").rstrip(",")
                new_action = f"action:<一级: {','.join(level_1_tag_list)}><二级: {','.join(level_2_tag_list)}>"
                line["prompt"][-1]["content"] = uttrance + new_action

    if data_type == "sft":
        for line in init_data:
            if len(line["messages"]) == 3:
                continue
            for item in line["messages"]:
                if item["role"] == "user":
                    uttrance, actions_list = item["content"].split("action:")
                    actions_list = actions_list.split(",")
                    level_1_tag_list = list(set([action_processor.get_key_tag(a) for a in actions_list]))
                    if random.random() < level_two_tag_mask_ratio:
                        level_2_tag_list = ["*"]
                    else:
                        level_2_tag_list = actions_list
                    level_1_tag_str = ','.join(level_1_tag_list).lstrip(",").rstrip(",")
                    level_2_tag_str = ','.join(level_2_tag_list).lstrip(",").rstrip(",")
                    new_action = f"action:<一级: {level_1_tag_str}><二级: {level_2_tag_str}>"
                    item["content"] = uttrance + new_action

    return init_data

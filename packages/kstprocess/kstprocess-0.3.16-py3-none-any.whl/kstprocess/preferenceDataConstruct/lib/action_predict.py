import json
import requests


"""
植发科，儿科模拟中控action策略
2025.0311.zhenjie
"""

def get_paediastrics_action_mapping():
    with open ("./config/paediastrics/提示词管理.json", "r") as f:
        mapping = json.load(f)
    return mapping


def get_hair_action_mapping():
    with open ("./config/hair/提示词管理.json", "r") as f:
        mapping = json.load(f)
    return mapping


def get_dialog_next_prompt_mapping_action(utterance, domain):
    if domain == "hair":
        res = requests.get(f"http://10.14.250.11:30300/intention/v2/hairtransplant?utterance={utterance}")
        intent = json.loads(res.text)["data"]["intent"]
        mapping_action = get_hair_action_mapping()
    elif domain == "paediastrics":
        res = requests.get(f"http://10.14.250.11:30373/intention/v1/paediatrics?utterance={utterance}")
        intent = json.loads(res.text)["data"]["intent"]
        mapping_action = get_paediastrics_action_mapping()
    if intent in mapping_action.keys():
        return [mapping_action[intent]]
    else:
        return []

def get_paediastrics_action_artificial():
    return {"早熟":{
                "1": ["问年龄"],
                "2": ["答疑科普", "问诊"],
                "3": ["问诊"],
                "4": ["诊断套电话术"],
                "5": ["套电相关"],
                "8": ["套电相关"],
                "10": ["套电相关"],
                "12": ["套电相关"]
             },
             "多动症": {
                    "1": ["问年龄"],
                    "2": ["问症状"],
                    "3": ["问诊"],
                    "5": ["答疑", "套电相关"],
                    "8": ["套电相关"],
                    "11": ["套电相关"],
                    "16": ["套电相关"]
                },
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
            "自闭症": {"1": ["问年龄"], 
                       "2": ["答疑科普", "问诊"], 
                       "3": ["问诊"], 
                       "4": ["诊断套电话术"], 
                       "5": ["套电相关"], 
                       "8": ["套电相关"], 
                       "10": ["套电相关"], 
                       "12": ["套电相关"]},
            "语言发育迟缓":  {
                        "1": ["问年龄"],
                        "2": ["问诊"],
                        "3": ["答疑科普", "问诊"],
                        "4": ["诊断套电话术"],
                        "5": ["套电相关"],
                        "7": ["套电相关"],
                        "9": ["套电相关"],
                        "12": ["套电相关"]
                        },
            "注意力问题": {
                        "1": ["问年龄"],
                        "2": ["问诊"],
                        "3": ["问诊", "答疑科普"],
                        "4": ["套电相关诊断套电话术"],
                        "5": ["答疑", "套电相关"],
                        "6": ["套电相关"],
                        "8": ["套电相关"],
                        "12": ["套电相关"]
                    },
            "测试量表": {
                        "1": ["问年龄"],
                        "2": ["问诊", "问症状"],
                        "3": ["问诊", "问症状"],
                        "4": ["套电相关测量表套电"],
                        "7": ["答疑诊断分析", "套电相关治疗套电话术"],
                        "8": ["衔接下危害"],
                        "10": ["套电相关食疗套电"],
                        "11": ["答疑科普病因介绍"],
                        "12": ["衔接辅助推动话术"],
                        "14": ["套电相关治疗套电话术"],
                        "16": ["套电相关要电话"]
                    },
             "多指并指":  {
                        "1": ["问年龄"],
                        "2": ["问诊", "问症状"],
                        "3": ["套电相关图片套电话术"],
                        "4": ["套电相关要微信"],
                        "7": ["衔接辅助推动话术"],
                        "8": ["套电相关价格套电话术"],
                        "10": ["套电相关食疗套电"],
                        "11": ["衔接下危害"],
                        "14": ["套电相关福利", "套电相关要微信"]
                    },
            "先天性脱位": {
                        "1": ["问年龄"],
                        "2": ["问诊问部位", "问诊问症状"],
                        "3": ["问诊问持续时长", "问诊问就诊史"],
                        "5": ["套电相关治疗套电话术"],
                        "8": ["套电相关诊断套电话术"],
                        "11": ["套电相关食疗套电"],
                        "14": ["套电相关要联系方式"],
                        "15": ["衔接下危害"],
                        "17": ["衔接辅助推动话术", "套电相关要微信"]
                    },
            "肌无力":  {
                        "1": ["问年龄"],
                        "2": ["问诊问症状"],
                        "3": ["问诊问就诊史"],
                        "4": ["答疑科普病因介绍"],
                        "5": ["套电相关图片套电话术"],
                        "7": ["衔接下危害"],
                        "8": ["问诊问治疗意愿"],
                        "9": ["套电相关治疗套电话术"],
                        "12": ["衔接辅助推动话术"],
                        "13": ["套电相关食疗套电"],
                        "15": ["引导问需要"],
                        "18": ["套电相关邀约话术"]
                    },
            "通用":  {
                        "1": ["问诊"],
                        "2": ["问年龄", "问性别"],
                        "3": ["问诊"],
                        "5": ["答疑", "套电相关要微信"],
                        "7": ["套电相关食疗套电"],
                        "8": ["套电相关食疗套电"],
                        "10": ["答疑科普病因介绍"],
                        "11": ["套电相关福利", "套电相关要联系方式"],
                        "12": ["衔接下危害"],
                        "13": ["引导问需要"],
                        "15": ["套电相关"]
                    },
            "矮小症":   {
                        "1": ["问年龄"],
                        "2": ["问诊"],
                        "3": ["问诊", "答疑科普"],
                        "4": ["诊断套电话术"],
                        "5": ["套电相关"],
                        "7": ["套电相关"],
                        "9": ["套电相关"],
                        "12": ["套电相关"]
                    },  
             "智力低下": {
                        "1": ["问年龄"],
                        "2": ["问诊"],
                        "3": ["问诊", "答疑科普"],
                        "4": ["诊断套电话术"],
                        "5": ["答疑", "套电相关"],
                        "6": ["套电相关"],
                        "8": ["套电相关"],
                        "12": ["套电相关"]
                    },
             "焦虑": {
                        "1": ["自定义话术", "问年龄", "问诊问症状"],
                        "2": ["问诊疾病相关问诊"],
                        "3": ["问诊问持续时长"],
                        "4": ["套电相关测量表套电"],
                        "5": ["套电相关测量表套电"],
                        "8": ["套电相关食疗套电"],
                        "11": ["套电相关福利", "套电相关要微信"],
                        "14": ["套电相关治疗套电话术"]
                    }
        }

def get_hair_action_artificial():
    return {"通用": {"1": ["问诊"], 
                     "2": ["答疑", "问诊"], 
                     "3": ["活动套电话术", "要联系方式"], 
                     "5": ["套电话术", "要联系方式"]
                     }}


def get_dialog_next_prompt_artificial(utterance, server_round, domain):
    if domain == "hair":
        mapping_action = get_hair_action_artificial()
        return mapping_action["通用"].get(str(server_round), [])
    
    elif domain == "paediastrics":
        res = requests.get(f"http://10.14.250.11:30374/paediatrics_topic?utterance={utterance}")
        item = json.loads(res.text)["data"]["item"]
        mapping_action = get_paediastrics_action_artificial()
        if item not in mapping_action.keys():
            return mapping_action["通用"].get(str(server_round), [])
        else:
            return mapping_action[item].get(str(server_round), [])
    


def get_prompt_info(utterance, server_round, domain):
    prompt_info = {'prompt_artificial': [], 'prompt_mapping': [], 'prompt_acp': {}}
    prompt_info["prompt_mapping"] = get_dialog_next_prompt_mapping_action(utterance, domain)
    prompt_info["prompt_artificial"]  = get_dialog_next_prompt_artificial(utterance, server_round, domain)
    return prompt_info



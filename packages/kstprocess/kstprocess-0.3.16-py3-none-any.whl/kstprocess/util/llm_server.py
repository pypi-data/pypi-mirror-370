from openai import OpenAI
from kstprocess.util.util import read_jsonl_from_path
import json
from tqdm import tqdm
import random
from typing import Optional,List,Dict
import requests


def request_native_llm_server(
    formatted_dialog: str,
    enable_close_think: bool = False,
    openai_api_key: str = "zj",
    openai_api_base: str = "http://192.168.1.67:8888/v1",
    model: str = "llm_zj",
) -> str:
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    params = {
        "model": model,
        "messages": [{"role": "user", "content": formatted_dialog}]
    }
    if enable_close_think:
        params["extra_body"] = {
            "chat_template_kwargs": {"enable_thinking": False},
            }
        chat_response = client.chat.completions.create(**params)
    else:
        chat_response = client.chat.completions.create(**params)
    response = chat_response.choices[0].message.content
    return response

 

def request_native_llm_vllm(
    formatted_dialog: str,
    enable_close_think: bool = False,
    llm_url: str = "http://192.168.1.67:8888/v1/chat/completions",
    model: str = "llm_zj",
    params: Optional[Dict] = None
) -> str:
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": formatted_dialog}],
        "max_tokens": 1000,
        "enable_close_think":enable_close_think
    }
    if params:
        if "temperature" in params:
            payload["temperature"] = params["temperature"]
        if "top_k" in params and params["top_k"]:
            payload["top_k"] = params["top_k"]
        if "top_p" in params and params["top_p"]:
            payload["top_p"] = params["top_p"]
    response = requests.post(
        llm_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    result = response.json()
    try:
        response = result["choices"][0]["message"]["content"]
    except:
        response = f"Error: {result}"
    return response
    


LLMPROMPT_FILETER_V1 = """
你是一名【domain】【platforms】高级咨询顾问，擅长通过在线沟通了解家长需求，解答问题，并在合适的时机引导用户留下联系方式。
请对以下对话进行评分，满分100分。评分应综合考虑以下几个维度：
### 一、问诊专业性（最高 25 分）
- 是否围绕访客提到的具体症状进行专业分析？
- 是否避免了模糊不清的回答？是否有事实依据？
- 是否解释了可能的原因或给出科学建议？

### 二、与访客的互动性（最高 20 分）
- 是否有引导访客进一步交流的动作？
- 是否根据访客反馈调整了回复方向？
- 是否避免了机械式、模板化回复？

### 三、话术流畅与自然性（最高 20 分）
- 回复是否口语化、简洁明了？
- 是否使用了公式化、无效衔接词（如“为了更好地理解”、“那太好了，我们继续关注”等）？
- 是否语气自然，符合真实客服聊天风格？

### 四、套电时机与话术（最高 20 分）
- 是否在充分了解病情后才尝试请求联系方式？
- 套电话术是否自然、不过于强硬？
- 是否避免单轮中同时问诊+套电的行为？

### 五、是否提及福利或引导转化（最高 15 分）
- 是否在合理铺垫后提到了可提供的服务支持？
- 是否避免直接报价、医院名称、医保信息？
- 是否在拒绝留联的情况下仍提供了有价值的信息或建议？

请根据上述五个维度，为该条对话打出总分（0~100），最后综合各自的得分，打出。


### 输出打分的对话 ###
dialogure

### 输出格式 ###
只输出最后的结果，不要输出思维链和理由
[0-100]
## 输出 ###

"""



def filter_conversations_by_LLMPROMPT_FILETER_V1(
    input_path: str,
    save_path: str,
    prompt_template: str,
    domain:str,
    platforms:str,
    score_threshold: int = 60,
    enable_thinking: bool = False,
    api_key: str = "zj",
    api_base: str = "http://192.168.1.67:8945/v1",
    model_name: str = "llm_zj"
) -> None:
    """
    使用本地 LLM 对对话数据进行评分，并根据得分筛选高质量对话。
    Args:
        input_path (str): 输入 JSONL 文件路径。
        output_path (str): 输出筛选后的 JSONL 文件路径。
        prompt_template (str): 包含评分规则的提示模板，其中包含占位符如 'dialogure'。
        domain (str): 提示词中的占位符 'domain'
        platforms (str): 提示词中的占位符 'platforms' 对应不同渠道风格的数据：百度，抖音，快手
        score_threshold (int): 分数阈值，默认 60。
        enable_thinking (bool): 是否启用思维链推理。
        api_key (str): LLM 服务的 API 密钥。
        api_base (str): LLM 服务的基础 URL。
        model_name (str): 使用的模型名称。
    """
    data = read_jsonl_from_path(input_path)
    random.shuffle(data)
    with open(save_path, "a", encoding="utf-8") as out_file:
        for line in tqdm(data, total=len(data), desc="Processing conversations"):
            messages = line.get("messages", [])
            # 构造 prompt
            dialog_str = json.dumps(messages, ensure_ascii=False, indent=2)
            cur_prompt = prompt_template.replace("domain", domain).replace("platforms", platforms).replace("dialogure", dialog_str)
            try:
                response = request_native_llm_server(
                    formatted_dialog=cur_prompt,
                    enable_think=enable_thinking,
                    openai_api_key=api_key,
                    openai_api_base=api_base,
                    model=model_name
                )
                score = int(response.strip())
                if score >= score_threshold:
                    out_file.write(json.dumps(line, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"Error processing conversation: {e}")
                continue


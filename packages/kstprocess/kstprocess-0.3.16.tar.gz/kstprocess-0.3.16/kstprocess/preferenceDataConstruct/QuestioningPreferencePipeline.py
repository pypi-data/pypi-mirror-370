from tqdm import tqdm
from openai import OpenAI
import json
from kstprocess.util.util import read_jsonl_from_path
from util.postprocess.action_util import ActionProcessor
from util.llm_server import request_native_llm_server


QUESTIONPROMPT = """
假设一句候选回复,一个问题算一个问诊，那么超过等于2个问题的算是 问诊过多
    例如: 客服：多大年龄？男性女性？有什么症状？   算是三个问诊
    例如: 孩子最近是否接触过可能引起呼吸道不适的物质或环境？<sep>比如烟雾、尘埃或是宠物毛发等？ 举例形式的算是一个问诊。
### 输入对话 ###
对话历史:
dialog
当前回复:
chosen_content
### 输出格式 ###
所有结果按照list形式输出，包含的类型只能够是 str
["原始的问诊个数", "保留一个最佳的问诊句子,不要考虑合并问诊，其他的不变，同时答疑的句子顺序要在问诊的前面,输出最后修改的结果", "修改之后的问诊个数"]
### 输出 ###

"""



def think_by_prompt(dialog, chosen_content):
    prompt = QUESTIONPROMPT.replace("dialog", str(dialog)).replace("chosen_content", str(chosen_content))
    res = request_native_llm_server(prompt).split("</think>")[1]
    return res


# 主处理逻辑
def process_data(input_path, output_path):
    init_data = read_jsonl_from_path(input_path)
    cur_processor = ActionProcessor()
    with open(output_path, "a", encoding="utf-8") as file:
        for line in tqdm(init_data, total=len(init_data), desc="Processing"):
            content = line["chosen"][0]["content"]

            # 获取动作统计
            stats = cur_processor.count_response_action_label_num(content)
            question_count = stats["action_counts"].get("问诊", 0)
            call_count = stats["action_counts"].get("套电", 0)

            # 判断是否需要处理
            if question_count <= 2 or call_count > 0:
                continue

            # 获取LLM优化结果
            try:
                result = eval(think_by_prompt(line["prompt"], line["chosen"]))
            except:
                continue
            if not result or len(result) < 3:
                continue

            original_count, modified_text, new_count = result

            # 只有当问诊数量减少时才写入
            if int(original_count) == int(new_count):
                print("问诊数量未减少，跳过此条数据")
                continue

            # 构建新的偏好对
            new_chosen = [{"role": "assistant", "content": modified_text}]
            new_line = {
                "prompt": line["prompt"],
                "chosen": new_chosen,
                "rejected": line["chosen"]
            }

            # 写入文件
            print(new_line)
            file.write(json.dumps(new_line, ensure_ascii=False) + "\n")
            file.flush()  # 确保及时落盘，防止程序中断导致丢失数据
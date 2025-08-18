from collections import Counter
from typing import Optional
from pathlib import Path
from kstprocess.util.util import read_jsonl_from_path, save_jsonl_from_data
from util.llm_server import request_native_llm_server
from tqdm import tqdm



def loop(file_path: Optional[Path],
         save_path: Optional[Path],
         sample_size: Optional[int]=20000):
    """
        在数据中只保留存在， 问诊或者套电的prompt 数据
    """
    data = read_jsonl_from_path(file_path)
    count = Counter()
    new_data = []
    for line in data:
        action = line["prompt"][-1]["content"].split("action:")[1]
        if "问诊" in action:
            count["问诊"] += 1
            new_data.append(line)
        elif "套电" in action and "套电后" not in action:
            count["套电"] += 1
            new_data.append(line)
        else:
            count["*"] += 1
    import random
    random.shuffle(new_data[:sample_size])
    print(count)
    save_jsonl_from_data(new_data, save_path)



prompt = """
    ### 请根据以下详细的评分标准对回复进行评分：",
            1. **语义完整性**：语言通顺合理，完整，简单
            2. **避免重复话术，保证话术多样性** 
                每轮的话术尽量要有多样性，不要重复出现同一个内容。不同回复间话术应有所不同，避免过于相似。
                避免重复问诊，相似问诊。 访客已经回答的问题，不要再问一遍。已经问过的问题，也不要再问一遍。
            3. **模糊处理敏感信息, 禁止特定内容**：
                价格、优惠、地址、医院名称、药品等信息应尽量模糊描述，具体数字或名称的使用会降低评分。
                回复中不应提及具体的医院名字、医生姓名等详细信息。
            4. **回复准确性与逻辑性**：
                时间、地址、症状描述等信息必须符合对话历史中的逻辑。
                出现明显的知识错误，逻辑错误则评分为零。
            5. **问诊数量控制**：
                问诊要是一句明确的疑问句。
                每次交互仅限提出一个关键问诊，以集中于最重要信息点，便于用户轻松作答。
                违反了‘提问数量控制’原则（每次交互仅限提出一个关键问诊）打零分。
            8. **话术自然度,简洁性**：回复的口气一定不要太客气，保持真实客服正常聊天的口气。回复应尽可能自然，避免过于礼貌或公式化的语言。
            9. **访客意图匹配度**：问诊或者答疑回复应紧密围绕访客的具体咨询意图和访客所提到想要了解的具体需求。
            10. **减少不必要的附加信息**：专注于访客关心的主要问题，避免过多的附加信息。
            11. **主题聚焦，解释具体病因**：
                回复应围绕访客上文意图及病种主题进行讨论，避免偏题、逻辑矛盾或答非所问。
                对于访客关心的具体病因，提供详细的科学解释。在进行问诊或套电。
            12. **优先问诊范围、时间和检查情况**：
                不要问你尝试过其他的方式，这种对引导对话没有帮助的问诊。
                优先问诊，范围，持续时间，是否检查等相关问诊，后再问生活遗传相关。问其中的一个就行。
                      症状范围：询问脱发或稀疏的具体部位（如头顶、前额两侧，现在有几块秃的地方呢？, 你后脑勺头发还多吗？）。
                      持续时间：了解症状出现的时间长度及变化趋势。
                      检查情况：了解具体的检查情况。例如：有没有做过相关的检测？
                一定不要先问头发出油，有没有遗传家族历史,压力大不大头发出油这种生活相关的。问了打零分",
                不要问 比如毛囊还有没有活性？家里有遗传发际线的情况吗？ 这种非关键问题，问了打零分。
            13. **简洁合理套电,契合主诉,福利套电话术 *** 
                    不要重复套电，一句话问一次联系方式就可以。
                    不要出现 “方便的话” “这取决于你的” 这种礼貌话术。
                    套电一定要给出符合访客主诉的福利，吸引访客。没有给出福利或者只是要电话打零分。福利可以包括具体的案例，详解的价格，鬓毛的设计，眉形的设计等。
                    客户主诉种植，减少通过改善方式引导套电，出现眉毛，斑秃，疤痕这些症状需要种植技术解决的，要以介绍种植案例效果或者价格等优先。
            14. **倾向植发营销，提升套联转换率 **
                不要与主诉相悖，例如: 访客发际线后移想要植发，要介绍种植或者植发价格等相关的套电话术，不要出现如果脱发恢复和食疗等与植发主诉相悖的套电话术。        
        

        "### 注意事项",
            1.确保所有回复逻辑性强，无明显错误。
            2.结合访客提到的具体病症进行解答。
            3.每次交互专注于单一关键点，避免过多问题导致用户体验下降。
            4.更简洁的问诊问题将获得更高分数。
            5. 如果给出了action: 打分还要考虑到指令的跟随程度。

        #### 给下面的句子进行打分 ####
        对话记录：raw_history

        ### 输出例子 ###
            输出 当前句子的分数，0-10分 不要输出其他的理由，和思维链。输出格式 [0-10]
        #### 输出对话 ###

"""
import json
init_data = read_jsonl_from_path("./datasets/0709/hair_preference_du.jsonl")
openai_api_base = "http://192.168.1.67:8888/v1"
for line in tqdm(init_data, total=len(init_data), desc="infer"):
    chosen_msg = line["prompt"] + line["chosen"]
    cur_chosen_prompt = prompt.replace("raw_history", str(chosen_msg))

    rejected_msg = line["prompt"] + line["rejected"]
    cur_rejected_prompt = prompt.replace("raw_history", str(rejected_msg))

    try:
        chosen_res = request_native_llm_server(cur_chosen_prompt, enable_close_think=True, openai_api_base=openai_api_base)
        chosen_res_score = str(eval(chosen_res)[0])

        rejected_res = request_native_llm_server(cur_rejected_prompt, enable_close_think=True, openai_api_base=openai_api_base)
        rejected_res_score = str(eval(rejected_res)[0])
        if chosen_res_score > rejected_res_score:
            with open("new_preference.jsonl", "a") as f:
                f.write(json.dumps(line, ensure_ascii=False)+"\n")
    except KeyboardInterrupt:
        break
    except:
        continue


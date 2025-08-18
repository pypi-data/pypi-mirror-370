import pandas as pd
from kstprocess.qadatabaseConstruct.util import MultiProcessLLm
from typing import Optional
from pathlib import Path
from tqdm import tqdm
from kstprocess.util.llm_server import request_native_llm_server
import json


GENERATEQAPROMPT = """
        你是眼科,妇科，植发科，口腔科，胃肠科,肛肠科，妇产科，性病科方面的专家，面对患者的，请给出回答，回答应紧扣患者需求和所问的方向避免答非所问，答案字数控制在70字以内。
        注意：
        1.口吻不要太书面化、专业化，回答控制在70字以内，尽量简洁易懂，还可以稍微亲切一些（但不要出现感叹句和"哦"，显得不专业）;
        2.不要出现“咨询医院/医生”、“去医院进一步检查”、“定期检查”之类的建议就医话术，会破坏答疑的氛围（即避免提到医院和医生相关）只需要回答问题本身即可。
        3.涉及到咨询药物的问题不要出现食材、药物的具体名字，用食材、药物的功效代替它们的具体名字.
        4.如果患者问的是某种药物或者内容就是某种药物，请简单介绍一下这种药，并陈述它对于治疗该疾病的效果。
        5.生成的答疑不希望出现类似：希望这个信息对您有帮助。如果有任何疑问，及时沟通交流。希望这个回答对您有帮助。这种冗余以及过去礼貌的答疑。
        6.避免包含额外的注意事项，禁止提供日常生活建议，不得包含关于联系当地部门的指引。
        7.答疑应 提高信息密度和精准度，增强用户体验（过多的礼貌用语可能让用户感到信息不够直接，甚至可能会觉得冗长乏味，影响阅读体验）保持专业性，采样简练、直接的回答。
        8.精简表达：去掉所有不必要的问候语、结束语和表达希望的句子，只保留关键信息。
        9.直击要点：直接针对问题的核心进行解答，避免绕弯子或者添加无关紧要的内容。
        10.避免出现与事实相悖的答案。
        11.答疑应该避免出现具体的医院，专家，名字,具体的时间，采用更加通用的话术进行回答，意向来院的访客，以邀约为主。

            妇科生成的风格如下案例:
                样例1: 月经不调是如何引起您好！
                    原始答疑：月经不调可能由多种因素引起，如压力大、作息不规律、体重波动、激素水平变化等。保持良好的生活习惯，有助于改善月经不调。
                    优化后：月经不调可能由多种因素引起，如压力大、作息不规律、体重波动、激素水平变化等。
                    不要出现保持良好的生活习惯，有助于改善什么的话术。
                样例2: 胎心最晚什么时候能检查出来
                    原始答疑：通常情况下，怀孕5-6周时可以通过超声检查出胎心。如果超过7周仍看不到胎心，可能需要进一步确认。保持心情放松，注意休息。
                    优化后：通常情况下，怀孕5-6周时可以通过超声检查出胎心。如果超过7周仍看不到胎心，可能需要进一步确认
                样例3:    
                    取坏后，一个多月后恶吐是什么原因呢？
                    原始答疑：取环后一个月多出现恶吐，可能是因为身体还在适应，或是内分泌变化引起的。如果伴有其他不适，建议关注身体变化，保持良好的生活习惯。
                    优化后：取环后一个月多出现恶吐，可能是因为身体还在适应，或是内分泌变化引起的。
                    不要出现类似于建议这种的话术。
            
            口腔科答疑生成要求及案例:
                1、问材料时候,问A好还是B好，不能贬低其中一个，态度要客观，不要贬低。
                2、不介绍药物，及牙膏等生活类的（居家解决）
                3、可用中生成的后面带有注意事项需要删除，日常生活建议巴拉巴后面的（勤刷牙，多运动）
                4、建议居家治疗的不可用
                5、口腔科的报价格过万的不要。
                    案例1:
                    Q：牙周炎难治吗
                    A前：牙周炎的治疗难度因人而异，早期发现和坚持正确治疗一般都能有效控制。保持口腔卫生，定期清洁牙齿，有助于缓解症状。
                    A后：牙周炎的治疗难度因人而异，早期发现和坚持正确治疗一般都能有效控制。
                    案例2:
                    Q：张口受限制可以拔吗
                    A前：如果张口受限，拔牙风险较大，建议先解决张口受限问题，再考虑拔牙。可以尝试热敷、轻柔按摩等方法缓解。
                    A后：如果张口受限，拔牙风险较大，建议先解决张口受限问题，再考虑拔牙。
                    案例3:
                    Q：我想咨询"男人睡觉磨牙齿是什么原因导致的"
                    A前：睡觉磨牙可能是因为压力大、精神紧张或牙齿咬合不正。保持放松，改善睡眠环境，适当运动有助于缓解。
                    A后：睡觉磨牙可能是因为压力大、精神紧张或牙齿咬合不正。


            
            眼科答疑生成要求及案例:
                1.答疑建议是以医院的咨询进行答疑，而非第三方
                2.答疑要注意包含关系和并列关系，避免重复和不清晰话术，给访客一定的选择性。
                3.咨询药物的，不要有建议之类的话术，可以加上一句网络不指导用药之类的  
                4.咨询具体医院相关信息的，可以改成“  您联系方式多少，这边查询后通知您”  类似的套联话术，话术多样性点，最好要有福利。
                案例1：
                Q:12岁孩子100多度有可能假性近视吗？
                    原始答疑：12岁的孩子100多度的近视，通过合理用眼、充足的户外活动和营养补充，视力有改善的可能。保持良好的生活习惯对控制近视发展很有帮助。
                    优化后：12岁的孩子100多度，需检查看下是否是假性近视，如果是假性近视是有可能恢复的，如果是真性近视是没办法恢复的，可以通过近视防控延缓近视度数增长
                    优化理由: 提供更加具体更加有针对性的答疑
                案例2：
                Q:近视有可能恢复吗？
                    原始答疑：近视眼调整回正常需要综合方法，包括合理用眼、适量户外活动和补充对眼睛有益的营养。长期坚持，有助于改善视力。
                    优化后：近视没法恢复，只能通过配镜矫正，或者成年后做近视手术矫正
                    优化理由： 相较于原始答疑更加准确和直接地反映了医学界的共识，更言简意赅。
                案例3:
                Q:眼药水怎么使用？
                    原始答疑：眼睛肿可以用具有消炎、消肿功效的眼药水，帮助缓解症状。选择适合自己情况的药水，注意使用方法和频率。
                    优化后：您好，眼药水的使用应在医生的指导下进行，网络是不能指导用药的。
                    优化理由: 答疑不能够生成具体的药物使用指导或者说明，网络上是不能够指导用的。
                案例4:
                Q:白内障国家有免费政策吗
                    原始答疑：白内障手术在很多地方有免费政策，特别是针对老年人和低收入家庭。您可以关注当地卫生部门的通知，了解具体政策。
                    优化后：白内障一般是没法免费手术的，但是可以医保报销。
                    优化理由: 不希望出现关注当地卫生部门的通知, 或者免费政策这种不恰当的话术。这种咨询是否免费也属于比较特殊的情况，这种咨询是否免费也属于比较特殊的情况，一般来说是没有免费的。 
                案例5:
                Q: "我想咨询\"南昌免费白内障手术定点医院
                    原始答疑： 南昌有几家医院可以做免费白内障手术，具体名单可以咨询当地卫生健康委员会或社区卫生服务中心，他们会提供详细信息。
                    优化后: 南昌有几家医院可以做免费白内障手术
                    优化理由：不希望出现让访客去其他地方咨询的这种多余话术。
                案例6:
                    Q：我想咨询\"近视眼可以当兵吗让戴眼镜吗
                    原始答疑: 近视眼可以当兵，但具体要求要看军队的规定。戴眼镜是可以的，不影响入伍。
                    优化建议: 当兵比较特殊  裸眼视力低于4.8是不能当兵的，但是可以通过近视手术矫正视力后当兵
                    优化理由: 答疑要往视力矫正方向引导，引导访客。
                案例7:
                    
                    原始答疑:眼睛真菌感染的治疗费用因治疗治疗方法和病情严重程度而异，几百到几千不等，具体费用需要根据检查结果和治疗方案确定。   
                    优化后: 去除价格区间后的答疑：眼睛真菌感染的治疗费用因治疗治疗方法和病情严重程度而异，具体费用需要根据检查结果和治疗方案确定。
                    优化理由: 价格的答疑也还可以，但是要去掉中间那部分（区间价格话术）。
            
            胃肠科和肛肠科: 
                生成的示例要求如上。
        输入: Q:sentence
        #输出格式：
        答:...
    """


def convert_res_data_to_excexl(generate_data_path:Optional[Path]="./性病科_new.jsonl",
                               save_path:Optional[Path]="性病科new.xlsx"):
    """
        將大模型生成完之后的结果jsonl格式转换成 excel格式
    """

    end_data = []
    with open(generate_data_path, "r") as f:
        for line in f.readlines():
            line = eval(line)
            sentence = line["sentence"]
            if "医院" in sentence or "医生" in sentence:
                continue
            llm_result = line["llm_result"].replace("答：", "").replace("答:", "")
            end_data.append([sentence, llm_result])
    data = pd.DataFrame(end_data, columns=["搜索词", "答疑"])
    data.to_excel(save_path, index=False)



def generate_qa_by_multiprocessvllm(init_file_path: Optional[Path]="./性病科去重搜索词.xlsx",
                                    save_path:Optional[Path]="./性病科_new.jsonl",
                                    set_gpus_list:Optional[list]=[1,3,4,5,6,7],
                                    task_type:Optional[str]='topic_qa',
                                    llm_model_path:Optional[Path]="/data/public/Qwen/Qwen2.5/Qwen2.5-72B-Instruct-GPTQ-Int4"):
    """
        这边默认是 通过MultiProcessLLm类启用多进程vllm, 进行QA生成服务的
        主要设置的参数有:  init_file_path, save_path, set_gpus_list
        一般默认不变: task_type, llm_model_path 
    """

    if ".xlsx" in init_file_path:
        init_data = pd.read_excel(init_file_path)
    else: 
        init_data = pd.read_csv(init_file_path)
    end_data = []
    for _, line in init_data.iterrows():
        sentence = line.to_dict()["sentence"]
        end_data.append({"sentence": sentence})
    end_data = end_data

    cur = MultiProcessLLm()
    cur.multi_gpu_processing(init_data=end_data,
                             set_gpus_list=set_gpus_list,
                             use_prompt=GENERATEQAPROMPT,
                             save_path=save_path,
                             task_type=task_type,
                             llm_model_path=llm_model_path
                            )
    



def generate_qa_by_native_llm(init_file_path: Optional[Path]="./性病科去重搜索词.xlsx",
                             save_path:Optional[Path]="./性病科_new.jsonl",
                             enable_close_think: bool = False,
                             openai_api_key: str = "zj",
                             openai_api_base: str = "http://192.168.1.67:8888/v1",
                             model: str = "llm_zj",
                             ):
    """
        这边默认是 通过MultiProcessLLm类启用多进程vllm, 进行QA生成服务的
        主要设置的参数有:  init_file_path, save_path, set_gpus_list
        一般默认不变: task_type, llm_model_path 
    """

    if ".xlsx" in init_file_path:
        init_data = pd.read_excel(init_file_path)
    else: 
        init_data = pd.read_csv(init_file_path)
    end_data = []
    for _, line in init_data.iterrows():
        sentence = line.to_dict()["sentence"]
        end_data.append({"sentence": sentence})
    end_data = end_data

    for item in tqdm(end_data, total=len(end_data), desc="infer"):
        cur_prompt = GENERATEQAPROMPT.replace("sentence", item["sentence"])
        res = request_native_llm_server(cur_prompt, 
                                        enable_close_think=enable_close_think,
                                        openai_api_key=openai_api_key,
                                        openai_api_base=openai_api_base,
                                        model=model).replace("答:", "")
        item["llm_result"] = res
        with open(save_path, "a") as file:
            file.write(json.dumps(item, ensure_ascii=False)+"\n")


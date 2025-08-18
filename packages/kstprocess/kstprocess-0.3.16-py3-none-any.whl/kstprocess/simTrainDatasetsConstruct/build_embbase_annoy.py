import pandas as pd
from tqdm import tqdm
from FlagEmbedding import BGEM3FlagModel
from sklearn.cluster import DBSCAN
from annoy import AnnoyIndex
import numpy as np
from functools import wraps
import time
from typing import Optional, List, Dict
from pathlib import Path
from collections import Counter
import os
import json
import re
from kstprocess.util.llm_server import request_native_llm_server


TRAINDATASIMFILTERPROMPT = """      
        ###任务要求：
            判断这两句话是否相似，用于QA检索任务。
            其中相似的两个text被认为, 能够用同一个answer回答。
            不相似的是两个text所代表的answer回答是不一样的。

            (1) 主诉主体，性别不一致，不相似。 例如： t1:做胎儿染色体多少钱  t2:染色体多少钱？ label:是不相似的
            (2) 症状描述不一致，不相似。 例如:  t1:如果两侧都切除了。还能不能生育？  t2: 直接切掉了能生育吗  label: 是不相似的
            （3）侧重点不同的，不相似。 例如: t1: 备孕前需要注意什么吗   t2:备孕前需要吃点什么   label: 是不相似的
            (4)  意图不一致的，不相似。
            (5) 不同疾病、症状、部位、项目等，除非指代相同，不相似。 例如: t1: 我输卵管左侧堵塞。 t2: 我主要是输卵管堵塞。
            （6） 存在实体，实体必须指向同一个事物，否则不相似，例如地址，机构，姓名，性别等 
            例如: t1:不孕不育男的有什么症状吗 t2:不育不孕有什么症状  label: 不相似
            (7) 同一个症状不同阶段的检查差异是不相似的。 t1: 备孕前需要检查哪些项目  t2: 怀孕了该检查哪些项目 label: 不相似
        ###数据格式为：
            第一句话:text1
            第二句话:text2
        ####按照下面格式输出最后的结果,只输出结果，不输出思考过程：
        相似/不相似。
    """


def merge_files_in_directory(directory: str) -> pd.DataFrame:
    """合并指定目录下的所有 CSV 和 XLSX 文件"""
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                all_files.append(os.path.join(root, file))
            elif file.endswith('.xlsx'):
                all_files.append(os.path.join(root, file))

    if not all_files:
        raise FileNotFoundError("No CSV or XLSX files found in the directory.")

    dataframes = []
    for file in all_files:
        if file.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.endswith('.xlsx'):
            df = pd.read_excel(file)
        dataframes.append(df)

    merged_df = pd.concat(dataframes, ignore_index=True)
    return merged_df

def monitor_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Function '{func.__name__}' executed in {duration:.4f} seconds")
        return result
    return wrapper

@monitor_time
def use_sklearn_DBSCAN(emb_data:list, eps:float):
    clf = DBSCAN(metric="cosine", eps=eps, min_samples=2)
    cluster_result = clf.fit_predict(emb_data)
    return cluster_result

def read_data(input_data_path: Optional[Path]):
    if "xlsx" in input_data_path:
        init_data = pd.read_excel(input_data_path)
    elif "csv" in input_data_path:
        init_data = pd.read_csv(input_data_path)
    else:
        print("find path and combined!")
        init_data = merge_files_in_directory(input_data_path)
    preprocess_data = []
    init_data = init_data[["sentence", "dignum"]]
    init_data = init_data.dropna()
    
    for i, line in init_data.iterrows():
        preprocess_data.append({
            'sentence': line["sentence"],
            'dignum': line["dignum"]
        })
    
    print(f"preprocess_data length: {len(preprocess_data)}")
    return preprocess_data

def get_highest_dignum(object_sentence: Optional[List[Dict]]):
    max_idx = 0
    max_digum_value = 0
    for i, line in enumerate(object_sentence):
        if max_digum_value < line["dignum"]:
            max_idx = i
            max_digum_value = line["dignum"]
    return object_sentence[max_idx]

# 根据频度的高低 保存数据
def save_clustered_data_by_frequence(embeddings_data: Optional[List] = [],
                                     preprocess_data: Optional[List] = [],
                                     eps: Optional[float] = 0.02):
    embeddings_data = embeddings_data.astype(np.float32)
    whole_cluster_data = use_sklearn_DBSCAN(embeddings_data, eps)
    whole_cluster_data_count = Counter(whole_cluster_data)
    no_repeat_data = []

    for cluster_id, nums in tqdm(whole_cluster_data_count.items(), total=len(whole_cluster_data_count), desc="聚类完毕，生成去重后搜索词"):
        if cluster_id != -1 and nums > 1:
            object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
            object_sentence = [preprocess_data[i] for i in object_idx]
            no_repeat_data.append(get_highest_dignum(object_sentence))
        else:
            object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
            object_sentence = [preprocess_data[i] for i in object_idx]
            for sentence in object_sentence:
                no_repeat_data.append(sentence)
    
    return no_repeat_data


def duplication_search_text_loop(init_data: Optional[List[Dict]],
                                 bge_path: Optional[Path],
                                 eps: Optional[float]):
    search_text_data = [line["sentence"] for line in init_data]

    model = BGEM3FlagModel(bge_path)
    embeddings_data = model.encode(search_text_data, batch_size=256, max_length=512)['dense_vecs']

    no_repeat_data = save_clustered_data_by_frequence(embeddings_data=embeddings_data,
                                                      preprocess_data=init_data,
                                                      eps=eps)
    print(f"{len(init_data)} -> {len(no_repeat_data)}")
    end_data = pd.DataFrame(no_repeat_data)
    return end_data


def duplication_pipeline(file_path: Optional[Path],
             save_path: Optional[Path],
             use_bge_path: Optional[Path],
             eps: Optional[float] = 0.1):
    print("begin duplication")
    init_data = read_data(input_data_path=file_path)
    data = duplication_search_text_loop(init_data, 
                                        bge_path=use_bge_path, 
                                        eps=eps)
    res_search_list = data["sentence"].tolist()
    end_data = pd.DataFrame({"sentence": res_search_list}) 
    end_data.to_csv(save_path, index=False) 
    print(f"end data length: {len(end_data)}")




def clean_similarity_trainData_by_llm(file_path: Optional[Path], 
                                        llm_label_file: Optional[Path],
                                        enable_close_think: bool = False,
                                        openai_api_key: str = "zj",
                                        openai_api_base: str = "http://192.168.1.67:8888/v1",
                                        model: str = "llm_zj",
                                    ):
    init_data = []
    data = pd.read_csv(file_path)
    for _, line in data.iterrows():
        init_data.append({"text1": line["QA_sentence"], 
                         "text2":line["Online_sentence"]})
    
    for item in tqdm(init_data, total=len(init_data), desc="infer"):
        cur_prompt = TRAINDATASIMFILTERPROMPT.replace("text1", item["text1"]).replace("text2", item["text2"])
        res = request_native_llm_server(cur_prompt, 
                                        enable_close_think=enable_close_think,
                                        openai_api_key=openai_api_key,
                                        openai_api_base=openai_api_base,
                                        model=model).replace("答:", "")
        item["llm_result"] = res
        with open(llm_label_file, "a") as file:
            file.write(json.dumps(item, ensure_ascii=False)+"\n")
    



def construct_simpair_by_annoy(QA_file_path:Optional[Path]="./datasets/耳鼻喉_0224_数据处理/原始数据/耳鼻喉-搜索词-压缩.xlsx",
                                domain_file_path:Optional[Path]="",
                                duplication_domain_file_path:Optional[Path]="./datasets/耳鼻喉_0224_数据处理/原始数据/耳鼻喉_访客问句统计_2024-11-01-2025-02-11.csv",
                                save_file_path:Optional[Path]="甲状腺线上top5召回.csv",
                                use_duplication_process=False,
                                bge_model_path='/data/public/bge-m3',
                                duplication_eps:Optional[float]=0.02,):



    if use_duplication_process:
        duplication_pipeline(file_path=domain_file_path,
                save_path=duplication_domain_file_path, 
                use_bge_path=bge_model_path,
                eps=duplication_eps)

    if ".csv" in duplication_domain_file_path:
        init_data = pd.read_csv(duplication_domain_file_path)
    elif "xlsx" in duplication_domain_file_path:
        init_data = pd.read_excel(duplication_domain_file_path)

    if ".csv" in QA_file_path:
        QA_data = pd.read_csv(QA_file_path)
    elif "xlsx" in QA_file_path:
        QA_data = pd.read_excel(QA_file_path)

    # 语料句子和其嵌入向量
    sentence_list = init_data["sentence"].map(lambda x: re.sub(r'我想咨询"|"', '', x)).tolist()
    print(f"duplication_domain_file length: {len(sentence_list)}")
    model = BGEM3FlagModel(bge_model_path)
    embeddings_data = model.encode(sentence_list, batch_size=256, max_length=80)['dense_vecs']
    embeddings_data = embeddings_data.astype(np.float32)
    f = embeddings_data.shape[1]  # 向量维度
    t = AnnoyIndex(f, 'angular')  # 使用余弦距离
    for i, vec in enumerate(embeddings_data):
        t.add_item(i, vec)
    t.build(10)  # 构建 10 棵树

    query_sentences = QA_data["访客句"].tolist()
    print("query length:", len(query_sentences))
    query_embeddings = model.encode(query_sentences, batch_size=256, max_length=80)['dense_vecs']
    query_embeddings = query_embeddings.astype(np.float32)

    new_data = []
    for i, sentence_emb in tqdm(enumerate(query_embeddings), desc="construct rank data:", total=len(query_embeddings)):
        similarity_list = t.get_nns_by_vector(sentence_emb, 5, include_distances=False)
        for rank, idx in enumerate(similarity_list, start=1):
            similar_sentence = sentence_list[idx]
            new_data.append((query_sentences[i], similar_sentence, rank))

    new_data_df = pd.DataFrame(new_data, columns=["QA_sentence", "Online_sentence", "rank"])
    new_data_df.to_csv(save_file_path, index=False)



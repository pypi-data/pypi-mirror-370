import pandas as pd
from typing import Optional, List, Dict
from FlagEmbedding import BGEM3FlagModel
from sklearn.cluster import DBSCAN
from collections import Counter
import numpy as np
from tqdm import tqdm
from pathlib import Path
from openai import OpenAI
import re
import os
import random
import time
from functools import wraps
import torch


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
def use_cuml_DBSCAN(emb_data:list, eps:float):
    clf = DBSCAN(metric="cosine", eps=eps, min_samples=2)
    cluster_result = clf.fit_predict(emb_data)
    return cluster_result


def read_data(input_data_path:Optional[Path]):
    if "xlsx" in input_data_path:
        init_data = pd.read_excel(input_data_path)
    elif "csv" in input_data_path:
        init_data = pd.read_csv(input_data_path)
    else:
        raise f"no support this format {input_data_path}, only csv, xlsx"
    preprocess_data = []

    for i, line in init_data.iterrows():
        if "搜索词" in line.keys() and "答疑" in line.keys():
            preprocess_data.append({'搜索词': line["搜索词"],
                                    '答疑': line["答疑"]
                                    })
        else:
            preprocess_data.append({'搜索词': line["sentence"]})
    print(f"preprocess_data length:{len(preprocess_data)}")
    return preprocess_data

# 根据频度的高低 保存数据
def save_clustered_data_by_frequence(embeddings_data:Optional[List]=[],
                                     preprocess_data: Optional[List]=[],
                                     eps:Optional[float]=0.03):
    
    embeddings_data =  embeddings_data.astype(np.float32)
    whole_cluster_data = use_cuml_DBSCAN(embeddings_data, eps)
    whole_cluster_data_count = Counter(whole_cluster_data)
    no_repeat_data = []

    for cluster_id, nums in tqdm(whole_cluster_data_count.items(), total=len(whole_cluster_data_count), desc="聚类完毕，生成去重后搜索词"):
        if cluster_id != -1 and nums > 1:
            object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
            object_sentence = [preprocess_data[i] for i in object_idx]
            no_repeat_data.append(random.choices(object_sentence, k=1)[0])
        
        else:
            object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
            object_sentence = [preprocess_data[i] for i in object_idx]
            for sentence in object_sentence:
                no_repeat_data.append(sentence)
     
    return no_repeat_data



def duplication_search_text_loop(init_data:Optional[List[Dict]],
                                 bge_path:Optional[Path],
                                 n_samples_per_topic:Optional[int],
                                 eps:Optional[float]):
    search_text_data = []
    for line in init_data:
        search_text_data.append(line["搜索词"])

    model = BGEM3FlagModel(bge_path)

    embeddings_data = model.encode(search_text_data, 
                        batch_size=256, 
                        max_length=512)['dense_vecs']


    no_repeat_data = save_clustered_data_by_frequence(embeddings_data=embeddings_data,
                                                     preprocess_data = init_data,
                                                     eps=eps)
    print(f"{len(init_data)}->{len(no_repeat_data)}")
    end_data = pd.DataFrame(no_repeat_data)
    return end_data

def pipeline(file_path:Optional[Path],
             save_path:Optional[Path],
             use_bge_path:Optional[Path],
             n_samples_per_topic: Optional[int],
             eps:Optional[float]=0.05):
    if "xlsx" in file_path or "csv" in file_path:
        init_data = read_data(input_data_path=file_path)
    else:
        init_data = convert_res_data_to_excexl(file_path)
    
    data = duplication_search_text_loop(init_data, 
                                        bge_path=use_bge_path, 
                                        n_samples_per_topic=n_samples_per_topic,
                                        eps=eps)

    if "答疑" in data.keys():
        answer_list = data["答疑"].tolist()
    else:
        answer_list = []
    i = 0
    res_search_list = data["搜索词"].tolist()
    if  answer_list:
        end_data = pd.DataFrame({"搜索词": res_search_list, 
                                "答疑":answer_list}) 
        end_data.to_csv(save_path, index=False)
    else:
        end_data = pd.DataFrame({"sentence": res_search_list}) 
        end_data.to_excel(save_path, index=False) 
    print(f"最终生成数据长度:{len(end_data)}")


def print_info():
    father_path = "./datasets/去重后结果/"
    for file in os.listdir(father_path):
        file_path = os.path.join(father_path, file)
        file_data = pd.read_csv(file_path)
        print(f"{file}: {len(file_data)}")


"""
对访客的问句，或者搜索词进行去重。
执行命令 CUDA_VISIBLE_DEVICES=0 python duplication_query_pipeline.py

"""
def convert_res_data_to_excexl(file_path):
    end_data = []
    with open(file_path) as f:
        for line in f.readlines():
            line = eval(line)
            sentence = line["sentence"]
            llm_result = line["llm_result"].replace("答：", "").replace("答:", "")
            end_data.append({"搜索词": sentence, "答疑": llm_result})
    return end_data



def filter_new_qaData_on_templateQA(
    init_path: str,
    rewrite_path: str,
    model_path: str,
    output_path: str,
    threshold: float = 0.85,
    batch_size: int = 256,
    max_length: int = 512
):
    """
    使用 BGE-M3 模型对 QA 对进行去重过滤，保留与原始模板相似度低于阈值的新内容。
    
    参数:
        init_path: 原始模板文件路径 (Excel)
        rewrite_path: 改写后的内容文件路径 (Excel)
        model_path: 模型路径
        output_path: 输出结果保存路径 (Excel)
        threshold: 相似度阈值，低于此值视为不重复
        batch_size: 编码时的 batch size
        max_length: 最大序列长度
    """
    
    # 加载数据
    init_data = pd.read_excel(init_path, skiprows=1)
    rewrite_data = pd.read_excel(rewrite_path)

    old_sentence_list = []
    for i, line in init_data.iterrows():
        text = line["*模板名称"]
        if "-" in text:
            text = text.split("-")[1]
        old_sentence_list.append(text)
    new_sentence_list = [line["AI改写后的答疑"] for _, line in rewrite_data.iterrows()]
    new_query_list = [line["搜索词"] for _, line in rewrite_data.iterrows()]

    # 加载模型
    model = BGEM3FlagModel(model_path)

    # 编码句子
    old_embeddings = model.encode(old_sentence_list, batch_size=batch_size, max_length=max_length)['dense_vecs']
    new_embeddings = model.encode(new_sentence_list, batch_size=batch_size, max_length=max_length)['dense_vecs']

    # GPU加速计算余弦相似度
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    old_embeddings_tensor = torch.tensor(old_embeddings, dtype=torch.float32).to(device)
    new_embeddings_tensor = torch.tensor(new_embeddings, dtype=torch.float32).to(device)

    with torch.no_grad():
        similarities_matrix = torch.matmul(new_embeddings_tensor, old_embeddings_tensor.T).cpu().numpy()

    # 过滤相似度低于阈值的句子
    filtered_new_sentences = []
    for i in tqdm(range(len(new_sentence_list)), desc="Filtering"):
        if np.max(similarities_matrix[i]) < threshold:
            filtered_new_sentences.append([new_query_list[i], new_sentence_list[i]])

    # 输出结果
    output_df = pd.DataFrame(filtered_new_sentences, columns=["搜索词", "答疑"])
    print(f"初始数据量: {len(new_sentence_list)}")
    print(f"去重后数据量: {len(filtered_new_sentences)}")
    output_df.to_excel(output_path, index=False)

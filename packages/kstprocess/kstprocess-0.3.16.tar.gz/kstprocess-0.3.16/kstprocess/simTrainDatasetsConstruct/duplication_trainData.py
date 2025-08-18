import pandas as pd
from typing import Optional, List, Dict
from FlagEmbedding import BGEM3FlagModel
from sklearn.cluster import DBSCAN
from collections import Counter
import numpy as np
from tqdm import tqdm
from pathlib import Path
import random
import time
from functools import wraps


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


def read_data(input_data_path:Optional[Path]):
    # 读取数据
    if "xlsx" in str(input_data_path):
        init_data = pd.read_excel(input_data_path)
    elif "csv" in str(input_data_path):
        init_data = pd.read_csv(input_data_path)
    else:
        raise ValueError(f"no support this format {input_data_path}, only csv, xlsx")

    # 动态判断列名
    required_columns = ["text1", "text2"]
    if not all(col in init_data.columns for col in required_columns):
        raise ValueError(f"Input data must contain {required_columns} columns")

    # 判断是否有 label 列
    has_label = "label" in init_data.columns

    # 预处理数据
    preprocess_data = []
    init_data = init_data[required_columns + (["label"] if has_label else [])]
    init_data = init_data.dropna()

    for i, line in init_data.iterrows():
        data_item = {
            "text1": line["text1"],
            "text2": line["text2"]
        }
        if has_label:
            data_item["label"] = line["label"]
        preprocess_data.append(data_item)

    print(f"preprocess_data length: {len(preprocess_data)}")
    return preprocess_data, has_label


# 根据频度的高低保存数据
def save_clustered_data(embeddings_data: Optional[List] = [],
                        preprocess_data: Optional[List] = [],
                        eps: Optional[float] = 0.1,
                        has_label: Optional[bool] = False):
    
    embeddings_data = embeddings_data.astype(np.float32)
    whole_cluster_data = use_sklearn_DBSCAN(embeddings_data, eps)
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


def duplication_search_text_loop(init_data: Optional[List[Dict]],
                                 bge_path: Optional[Path],
                                 eps: Optional[float]):
    search_text_data = []
    for line in init_data:
        search_text_data.append(str(line["text1"]) + " " + str(line["text2"]))

    model = BGEM3FlagModel(bge_path)

    embeddings_data = model.encode(search_text_data, 
                                  batch_size=256, 
                                  max_length=64)['dense_vecs']

    data = save_clustered_data(embeddings_data=embeddings_data,
                               preprocess_data=init_data,
                               eps=eps,
                               has_label="label" in init_data[0] if init_data else False)
    return data


def duplication_trainData_pipeline(file_path: Optional[Path],
                                    save_path: Optional[Path],
                                    use_bge_path: Optional[Path],
                                    eps: Optional[float] = 0.02):
    # 读取数据并判断是否有 label 列
    init_data, has_label = read_data(input_data_path=file_path)

    # 去重处理
    data = duplication_search_text_loop(init_data, 
                                        bge_path=use_bge_path, 
                                        eps=eps)

    # 保存结果
    columns = ["text1", "text2"]
    if has_label:
        columns.append("label")
    data = pd.DataFrame(data, columns=columns)

    print(f"{len(init_data)} --> {len(data)}")
    data.to_excel(save_path, index=False)


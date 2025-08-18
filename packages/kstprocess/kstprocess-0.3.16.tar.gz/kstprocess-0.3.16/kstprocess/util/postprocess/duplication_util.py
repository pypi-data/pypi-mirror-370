import random
import json
from tqdm import tqdm
from typing import Optional, List, Dict
from pathlib import Path
from collections import Counter
from FlagEmbedding import BGEM3FlagModel
import numpy as np
from promcse import PromCSE
import logging
import logging
from sklearn.cluster import DBSCAN
import numpy as np
from collections import Counter
from tqdm import tqdm
from sklearn.cluster import DBSCAN
import random
# 获取根日志记录器
root_logger = logging.getLogger()

# 设置根日志记录器的级别为 CRITICAL，这样只有严重错误会被记录
root_logger.setLevel(logging.CRITICAL)

# 移除所有现有的处理器以防止日志输出
if root_logger.hasHandlers():
    root_logger.handlers.clear()


class DuplicationProcesser():
    def __init__(
        self,
        model_type: str = "BGE-M3",
        model_path: str = '/data/public/bge-m3',
        start_idx: int = 1,
        end_idx: int = 12,
        eps: float = 0.03,
        min_samples: int = 2
    ) -> None:
        """
        初始化去重处理器

        Args:
            model_type (str): 使用的模型类型，支持 "PromCSE" 或 "BGE-M3"
            model_path (str): 模型本地路径
            start_idx (int): 对话中开始提取的部分索引
            end_idx (int): 对话中结束提取的部分索引
            eps (float): DBSCAN 聚类算法中的距离阈值
            min_samples (int): DBSCAN 中每个聚类的最小样本数
        """
        self.model_type = model_type
        self.model_path = model_path
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.eps = eps
        self.min_samples = min_samples

    def use_cuml_DBSCAN(self, emb_data: list):
        """
        使用 DBSCAN 算法对嵌入向量进行聚类

        Args:
            emb_data (list): 嵌入向量数据

        Returns:
            cluster_result: 聚类结果数组，-1 表示噪声点
        """
        clf = DBSCAN(metric="cosine", eps=self.eps, min_samples=self.min_samples)
        cluster_result = clf.fit_predict(emb_data)
        return cluster_result

    def save_clustered_data(self, 
                            embeddings_data: Optional[List] = [],
                            preprocess_data: Optional[List] = []):
        """
        根据聚类结果保留唯一数据

        Args:
            embeddings_data (Optional[List]): 嵌入向量数据
            preprocess_data (Optional[List]): 原始预处理后的对话数据

        Returns:
            no_repeat_data: 去重后的数据列表
        """
        embeddings_data = embeddings_data.astype(np.float32)
        whole_cluster_data = self.use_cuml_DBSCAN(embeddings_data)
        whole_cluster_data_count = Counter(whole_cluster_data)

        no_repeat_data = []
        for cluster_id, nums in tqdm(whole_cluster_data_count.items(), total=len(whole_cluster_data_count), desc="根据聚类结果查找数据:"):
            if cluster_id != -1 and nums > 1:
                object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
                object_sentence = [preprocess_data[i] for i in object_idx]
                no_repeat_data.extend(random.choices(object_sentence, k=1))
            else:
                object_idx = [idx for idx, j in enumerate(whole_cluster_data) if j == cluster_id]
                object_sentence = [preprocess_data[i] for i in object_idx]
                for sentence in object_sentence:
                    no_repeat_data.append(sentence)
        return no_repeat_data

    def duplication_sft_data_loop(self, key, preprocess_data: Optional[List[Dict]]):
        """
        处理 SFT 数据格式并进行去重

        Args:
            preprocess_data (Optional[List[Dict]]): 预处理后的对话数据列表

        Returns:
            no_repeat_data: 去重后的 SFT 数据
        """
        if self.model_type == "PromCSE":
            model = PromCSE(self.model_path, "cls", 10)
        elif self.model_type == "BGE-M3":
            model = BGEM3FlagModel(self.model_path)
        else:
            raise ValueError("no this model type")

        preprocess_dialog_data = []
        for item in preprocess_data:
            msg = item[key]
            new_msg = []
            if key != "history":
                for i, line in enumerate(msg):
                    if i < self.start_idx:
                        continue
                    if line["role"] == "user":
                        new_msg.append(f"user:{line['content']}")
                    else:
                        if "prompt" in line["content"]:
                            new_msg.append(f"assistant:{line['content'].split('prompt')[1]}")
                        else:
                            new_msg.append(f"assistant:{line['content']}")
                    if i == self.end_idx:
                        break
            else:
                new_msg = msg
            new_msg_str = "\n".join(new_msg)
            preprocess_dialog_data.append(new_msg_str)

        if self.model_type == "PromCSE":
            embeddings_data = model.encode(preprocess_dialog_data, device="cuda:3", batch_size=256, return_numpy=True)
        elif self.model_type == "BGE-M3":
            embeddings_data = model.encode(preprocess_dialog_data,
                                            batch_size=256,
                                            max_length=512)['dense_vecs']
        else:
            raise ValueError("no this model type")

        no_repeat_data = self.save_clustered_data(embeddings_data=embeddings_data,
                                                  preprocess_data=preprocess_data)
        print(f"sft duplication {len(preprocess_data)} -> {len(no_repeat_data)}")
        return no_repeat_data

    def convert_qwen_to_str(self, msg):
        """
        将 Qwen 格式转换为字符串格式用于编码

        Args:
            msg: 消息列表

        Returns:
            history_str: 转换后的字符串
        """
        history_list = []
        if "sentence" in msg[0].keys():
            flag = "sentence"
        elif "content" in msg[0].keys():
            flag = "content"
        else:
            return

        for i, item in enumerate(msg):
            if i == 0:
                history_list.append(f"(搜索词){item['role']}:{item[flag]}")
                continue
            elif i == 1:
                history_list.append(f"(引导语){item['role']}:{item[flag]}")
                continue
            if item["role"] == "SERVER" or item["role"] == "assistant":
                utter = item[flag]
                history_list.append("sever:" + utter)
            else:
                history_list.append("client:" + item[flag])
        return "\n".join(history_list)

    def get_encode_data(self, init_data: Optional[List[Dict]]):
        """
        提取 DPO/奖励模型数据中的历史、正例和负例文本

        Args:
            init_data: 输入数据列表

        Returns:
            history_data, chosen_data, rejected_data: 三部分数据
        """
        history_data = []
        chosen_data = []
        rejected_data = []
        for line in init_data:
            if "content" in line["chosen"][-1] and "prompt" not in line.keys():
                history = self.convert_qwen_to_str(line["chosen"][:-1])
                chosen_data.append(line["chosen"][-1]["content"])
                if "reject" in line.keys():
                    rejected_data.append(line["reject"][-1]["content"])
                elif "rejected" in line.keys():
                    rejected_data.append(line["rejected"][-1]["content"])
                else:
                    return
            elif "content" in line["chosen"][-1] and "prompt" in line.keys():
                history = self.convert_qwen_to_str(line["prompt"])
                chosen_data.append(line["chosen"][-1]["content"])
                rejected_data.append(line["rejected"][-1]["content"])
            else:
                history = self.convert_qwen_to_str(line["chosen"][:-1])
                chosen_data.append(line["chosen"][-1]["sentence"])
                if "reject" in line.keys():
                    rejected_data.append(line["reject"][-1]["content"])
                elif "rejected" in line.keys():
                    rejected_data.append(line["rejected"][-1]["content"])
                else:
                    return
            history_data.append(history)
        return history_data, chosen_data, rejected_data

    def get_sample_cluster_res(self, whole_cluster_data, preprocess_data):
        """
        根据聚类结果生成最终数据

        Args:
            whole_cluster_data: 聚类结果
            preprocess_data: 原始数据

        Returns:
            no_repeat_data: 去重后的数据
        """
        whole_cluster_data_count = Counter(whole_cluster_data)
        no_repeat_data = []
        for cluster_id, nums in tqdm(whole_cluster_data_count.items(), total=len(whole_cluster_data_count), desc="already cluster and construct ..."):
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

    def duplication_for_dpo_or_reward_data(self, init_data: Optional[List[Dict]]):
        """
        对 DPO 或 Reward 数据进行去重

        Args:
            init_data: 输入数据

        Returns:
            end_data: 去重后的数据
        """
        model = BGEM3FlagModel(self.model_path)
        history_data, chosen_data, rejected_data = self.get_encode_data(init_data)
        history_embeddings_data = model.encode(history_data,
                                               batch_size=256,
                                               max_length=1204)['dense_vecs']
        chosen_embeddings_data = model.encode(chosen_data,
                                             batch_size=256,
                                             max_length=256)['dense_vecs']
        rejected_embeddings_data = model.encode(rejected_data,
                                               batch_size=256,
                                               max_length=256)['dense_vecs']
        embeddings_data = chosen_embeddings_data + rejected_embeddings_data + history_embeddings_data
        embeddings_data = embeddings_data.astype(np.float32)
        print("clutering...")
        whole_cluster_data = self.use_cuml_DBSCAN(embeddings_data)
        end_data = self.get_sample_cluster_res(whole_cluster_data, init_data)
        print(f"dpo bge去重:{len(init_data)}->{len(end_data)}")
        return end_data

    def dupication_for_data(self, init_data: Optional[List[Dict]]):
        """
        自动识别数据格式并调用对应去重方法

        Args:
            init_data: 输入数据

        Returns:
            end_data: 去重后的数据
        """
        if "chosen" in init_data[0].keys():
            data_type = "dpo"
        elif "messages" in init_data[0].keys():
            data_type = "sft"
        elif "prompt" in init_data[0].keys() and "prompt_info" in init_data[0].keys():
            data_type = "log"
        else:
            raise ValueError("format can't open")
        if data_type == "dpo":
            end_data = self.duplication_for_dpo_or_reward_data(init_data)
        elif data_type == "sft":
            end_data = self.duplication_sft_data_loop("messages", init_data)
        elif data_type == "log":
            end_data = self.duplication_sft_data_loop("prompt", init_data)
        return end_data

    def remove_similar_candidates(self, init_data, threshold=0.85):
        """
        对候选回复进行去重

        Args:
            init_data: 包含 candidates 字段的数据
            threshold: 相似度阈值

        Returns:
            new_data: 去重后的数据
        """
        model = BGEM3FlagModel(self.model_path)
        new_data = []
        for line in tqdm(init_data, total=len(init_data), desc="infer"):
            candidates = line["candidates"]
            embeddings_data = model.encode(
                candidates,
                batch_size=5,
                max_length=256
            )['dense_vecs']
            similarity_matrix = np.dot(embeddings_data, embeddings_data.T)
            norms = np.linalg.norm(embeddings_data, axis=1, keepdims=True)
            cosine_similarity_matrix = similarity_matrix / (norms @ norms.T + 1e-8)

            unique_candidates = []
            used_indices = set()
            for i in range(len(candidates)):
                if i not in used_indices:
                    unique_candidates.append(candidates[i])
                    similar_indices = np.where(cosine_similarity_matrix[i] > threshold)[0]
                    used_indices.update(similar_indices)
            if len(unique_candidates) > 1:
                line["candidates"] = unique_candidates
                new_data.append(line)
        print(f"remove {len(init_data)}-->{len(new_data)}")
        return new_data
    
    def deduplicate_candidates(self, candidates, threshold=0.80, batch_size=5, max_length=256):
        model = BGEM3FlagModel(self.model_path)
        embeddings = model.encode(
            candidates,
            batch_size=batch_size,
            max_length=max_length,
        )['dense_vecs'] 
        similarity_matrix = np.dot(embeddings, embeddings.T)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        cosine_similarity_matrix = similarity_matrix / (norms * norms.T + 1e-8)
        unique_candidates = []
        used_indices = set()
        for i in range(len(candidates)):
            if i not in used_indices:
                unique_candidates.append(candidates[i])
                similar_indices = np.where(cosine_similarity_matrix[i] > threshold)[0]
                # 句子i相似的所有句子被记录，这些句子后续不会被加入unique_candidates
                used_indices.update(similar_indices)
        return unique_candidates
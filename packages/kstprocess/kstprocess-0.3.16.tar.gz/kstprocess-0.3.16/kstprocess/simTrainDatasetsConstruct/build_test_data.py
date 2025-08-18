import os
import logging
import pandas as pd
from tqdm import tqdm
import requests
from typing import List, Tuple, Set
from elasticsearch import Elasticsearch
from typing import Optional
from pathlib import Path
# 获取根日志记录器
root_logger = logging.getLogger()
logging.getLogger().setLevel(logging.CRITICAL)  # 只记录严重错误
logging.disable(logging.CRITICAL)  #
# 设置根日志记录器的级别为 CRITICAL，这样只有严重错误会被记录
root_logger.setLevel(logging.CRITICAL)

# 移除所有现有的处理器以防止日志输出
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 常量配置
# THRESHOLD = 0.97  # 相似度阈值
# MODEL_URL = "http://10.14.250.11:30318/text_sim_dermatology"  # 模型服务 URL 一般是要优化之前的线上使用的版本
# ONLINE_DATA_PATH = "./datasets/皮肤科/去重搜索词和问句合并.csv"  # 线上访客数据路径
# TRAIN_DATA_FOLDER = "./datasets/皮肤科/train_datasets/"  # 已经存在的训练数据文件夹
# SAVE_FILE_PATH = "./datasets/皮肤科生产环境模拟测试集.xlsx"  # 结果保存路径
# KNOWLEDGE_BASE_PATH = "./datasets/皮肤科/皮肤科QA.xlsx"  # 知识库数据路径


class ESToolkit:
    def __init__(self):
        es_host = os.getenv("ES_HOSTS", "192.168.1.16:9200")
        self.es = Elasticsearch(
            hosts=[{"host": es_host.split(":")[0], "port": int(es_host.split(":")[1]), "scheme": "http"}],
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        self.index_name = "sentence_index"
        self.doc_type = "doc"
        self.create_index()

    def create_index(self):
        """创建 Elasticsearch 索引"""
        mapping = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1
            },
            "mappings": {
                "properties": {
                    "sentence": {
                        "type": "text"
                    }
                }
            }
        }

        if not self.es.indices.exists(index=self.index_name):
            try:
                self.es.indices.create(index=self.index_name, body=mapping)
                logging.info(f"Index '{self.index_name}' created successfully.")
            except Exception as e:
                logging.error(f"Failed to create index '{self.index_name}': {e}")
        else:
            logging.info(f"Index '{self.index_name}' already exists.")

    def delete_index(self):
        """删除 Elasticsearch 索引"""
        if self.es.indices.exists(index=self.index_name):
            try:
                self.es.indices.delete(index=self.index_name)
                logging.info(f"Index '{self.index_name}' deleted successfully.")
            except Exception as e:
                logging.error(f"Failed to delete index '{self.index_name}': {e}")
        else:
            logging.info(f"Index '{self.index_name}' does not exist.")

    def add_sentences(self, sentences: List[str]):
        """将句子添加到 Elasticsearch 索引中"""
        for idx, sentence in enumerate(tqdm(sentences, desc="Adding sentences to ES")):
            doc = {"sentence": sentence}
            try:
                self.es.index(index=self.index_name, doc_type=self.doc_type, body=doc, id=idx)
            except Exception as e:
                logging.error(f"Failed to add sentence: {sentence}. Error: {e}")

    def search_similar_sentences(self, query_sentence: str, num_results: int = 5) -> List[dict]:
        """在 Elasticsearch 中搜索相似的句子"""
        query = {
            "query": {
                "match": {
                    "sentence": query_sentence
                }
            },
            "size": num_results
        }
        try:
            res = self.es.search(index=self.index_name, body=query)
            total = res["hits"]["total"]["value"] if isinstance(res["hits"]["total"], dict) else res["hits"]["total"]
            if total == 0:
                logging.warning(f"No matching sentences found for query: {query_sentence}")
                return []

            results = [{"id": doc["_id"], "sentence": doc["_source"]["sentence"]}
                       for doc in res["hits"]["hits"]]
            return results
        except Exception as e:
            logging.error(f"Error occurred during search for query '{query_sentence}': {e}")
            return []


def load_train_sentences(train_data_folder: str) -> Set[str]:
    """加载训练数据文件夹下的所有文件，并提取所有唯一的句子"""
    train_sentences = set()

    for file_name in os.listdir(train_data_folder):
        file_path = os.path.join(train_data_folder, file_name)
        if file_name.endswith(".csv"):
            data = pd.read_csv(file_path)
        elif file_name.endswith(".xlsx"):
            data = pd.read_excel(file_path)
        else:
            continue  # 跳过不支持的文件格式

        if "text1" in data.columns and "text2" in data.columns:
            sentences = set(data["text1"].tolist() + data["text2"].tolist())
            train_sentences.update(sentences)

    logging.info(f"Total unique sentences in training data: {len(train_sentences)}")
    return train_sentences


def reset_knowledge_base(es_toolkit: ESToolkit, knowledge_base_path: Optional[Path]):
    """重置知识库：删除旧索引并添加新的知识库数据"""
    es_toolkit.delete_index()
    es_toolkit.create_index()

    # 加载知识库数据
    knowledge_base_data = pd.read_excel(knowledge_base_path)
    query_pool = knowledge_base_data["搜索词"].tolist()
    logging.info(f"Knowledge base has {len(query_pool)} sentences.")

    # 将知识库数据添加到 Elasticsearch
    es_toolkit.add_sentences(query_pool)


def build_online_testData_pipeline(train_data_folder:Optional[Path],
                       online_data_path: Optional[Path],
                       model_url: Optional[str],
                       threshold: Optional[float],
                       save_file_path: Optional[Path],
                       knowledge_base_path: Optional[Path],
                       is_reset_knowledge_base:Optional[bool]=False):
    """模拟线上环境，生成不在训练集中的测试数据"""
    # 加载训练数据
    train_sentences = load_train_sentences(train_data_folder)

    # 加载线上数据
    online_data = pd.read_csv(online_data_path)
    online_sentences = online_data["sentence"].tolist()

    # 过滤出不在训练集中的句子
    test_sentences = [sentence for sentence in online_sentences if sentence not in train_sentences]
    logging.info(f"Total online sentences: {len(online_sentences)}")
    logging.info(f"Sentences not in training set: {len(test_sentences)}")

    # 初始化 Elasticsearch 工具
    es_toolkit = ESToolkit()

    # 重置知识库（如果需要）
    if is_reset_knowledge_base:  # 如果需要重置知识库，将此条件改为 True
        reset_knowledge_base(es_toolkit, knowledge_base_path=knowledge_base_path)

    # 对过滤后的句子进行测试
    test_data = []
    k = 0 
    for query in tqdm(test_sentences, total=len(test_sentences), desc="Processing queries"):
        results = es_toolkit.search_similar_sentences(query, num_results=10)
        text_b_list = [item["sentence"] for item in results]
        try:
            res = requests.post(f"{model_url}?question={query}？&body={text_b_list}")
            res.raise_for_status()  # 检查 HTTP 请求是否成功
            score_list = eval(eval(res.text)["data"]["score"])
            max_score_index = score_list.index(max(score_list))
            max_score = score_list[max_score_index]
            # 过滤掉相似度低于阈值的结果
            if max_score >= threshold:
                max_score_str = text_b_list[max_score_index]
                k += 1
                print(query, max_score_str, max_score)
                print(k, len(test_data))
                test_data.append((query, max_score_str, max_score))
                if len(test_data) >= 4000:  # 当 test_data 达到 4000 条时跳出循环
                    logging.info("Reached 4000 test data entries. Stopping processing.")
                    break
        except Exception as e:
            logging.error(f"Error occurred during model inference for query '{query}': {e}")

    # 保存结果
    test_data = pd.DataFrame(test_data, columns=["text1", "text2", "label"])
    test_data.to_excel(save_file_path, index=False)
    logging.info(f"Test data saved to {save_file_path}")

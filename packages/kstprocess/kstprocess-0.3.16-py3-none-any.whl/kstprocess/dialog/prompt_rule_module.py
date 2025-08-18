"""
问诊库方案

"""

from sentence_transformers import SentenceTransformer, util
import torch
import requests



class PromptRuleService(object):
    def __init__(self, model_path: str, threshold:float, llm_url):
        self.model = SentenceTransformer(model_path)
        self.threshold = float(threshold) 
        self.llm_url = llm_url


    def req_nativete_lm_model(self, history, candidates, domain):
        json_msg = {"history": history,
                    "candidates":candidates,
                    "domain": domain
                    }
        res = requests.post(url=self.llm_url, json=json_msg)
        try:
            response = eval(res.text)["response"]
        except :
            return {c:0 for c in candidates}
        return response

    def deduplicate(self, dialog: list, medical_database: list):
        if not dialog:
            return medical_database
        if not medical_database:
            return []
        dialog_embeddings = self.model.encode(dialog, convert_to_tensor=True)
        db_embeddings = self.model.encode(medical_database, convert_to_tensor=True)
        cosine_scores = util.cos_sim(db_embeddings, dialog_embeddings)
        max_similarities = torch.max(cosine_scores, dim=1).values
        filtered_database = [
            sent for sent, sim in zip(medical_database, max_similarities) if sim < self.threshold
        ]
        return filtered_database

    def self_deduplicate(self, candidates: list):
        if not candidates:
            return []
        embeddings = self.model.encode(candidates, convert_to_tensor=True)
        cosine_scores = util.cos_sim(embeddings, embeddings)
        to_remove = set()
        n = len(candidates)
        for i in range(n):
            for j in range(i + 1, n):
                if cosine_scores[i][j] > self.threshold:
                    to_remove.add(j)
        filtered_candidates = [
            sent for idx, sent in enumerate(candidates) if idx not in to_remove
        ]
        return filtered_candidates

    def get_best_match_prompt_rule(self, prompt_rule, qwen_format_history):
        try:
            history = [h["content"] for h in qwen_format_history]
            prompt_rule = prompt_rule[0].replace("话术库\n", "")
            candidates = prompt_rule.split("\n")
            ### 打分之前先 进行语义去重
            dialog_response = [
                item.strip() 
                for h in qwen_format_history 
                if h["role"] == "assistant" 
                for item in h["content"].split("<sep>") 
                if item.strip()
            ]
            candidates = self.deduplicate(dialog=dialog_response,
                            medical_database=candidates)
            domain = "paediastrics"
            scores = self.req_nativete_lm_model(history, candidates, domain)
            max_key = max(scores, key=lambda k: scores[k])
            return max_key
        except :
            return ""

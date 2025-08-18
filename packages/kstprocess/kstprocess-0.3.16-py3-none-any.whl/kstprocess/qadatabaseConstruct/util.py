from multiprocessing import Process, Lock
import os
import json
from typing import Optional, Dict, List
from pathlib import Path
from transformers import AutoTokenizer
from vllm import SamplingParams, LLM
import ast
from tqdm import tqdm
from transformers import AutoTokenizer
from vllm import SamplingParams, LLM


def convert_qwen_to_str(data: Optional[List[Dict]])->Optional[List[str]]:
    new_data = []
    for msg in data:
        history_str = []
        for i, item in enumerate(msg["messages"]):
            if i == 0:
                history_str.append(f"(搜索词){item['role']}:{item['content']}") 
                continue
            elif i == 1:
                history_str.append(f"(引导语){item['role']}:{item['content']}") 
                continue
            round_id = i // 2
            if item["role"] == "assistant":
                if "\t||\t" in item["content"]:
                    utter = item["content"].split("\t||\t")[1]
                elif "(" in item["content"]:
                    utter = item["content"].split(")")[1]
                else:
                    utter = item["content"]
                history_str.append(f"(round {round_id}){item['role']}:{utter}") 
            else:
                history_str.append(f"(round {round_id}){item['role']}:{item['content']}")
        new_data.append("\n".join(history_str))
    return new_data

# 读取日志形式的数据
def convert_log_format_to_str(data: Optional[List[Dict]])->Optional[List[str]]:
    new_data = []
    for msg in data:
        history_str = []
        for i, item in enumerate(msg["history"]):
            if i == 0:
                history_str.append(f"(搜索词){item['role']}:{item['content']}") 
                continue
            elif i == 1:
                history_str.append(f"(引导语){item['role']}:{item['content']}") 
                continue
            round_id = i // 2
            if item["role"] == "assistant":
                if "\t||\t" in item["content"]:
                    utter = item["content"].split("\t||\t")[1]
                elif "(" in item["content"]:
                    utter = item["content"].split(")")[1]
                else:
                    utter = item["content"]
                history_str.append(f"(round {round_id}){item['role']}:{utter}") 
            else:
                history_str.append(f"(round {round_id}){item['role']}:{item['content']}")
        new_data.append(("\n".join(history_str), msg["candidates"]))
    return new_data


# 转换qwen2格式到str
def convert_qwen_format_to_str(msg: Optional[List[Dict]]):
    history_str = []
    for i, item in enumerate(msg):
        if i == 0:
            history_str.append(f"(搜索词){item['role']}:{item['content']}") 
            continue
        elif i == 1:
            history_str.append(f"(引导语){item['role']}:{item['content']}") 
            continue
        round_id = i // 2
        if item["role"] == "assistant":
            if "\t||\t" in item["content"]:
                utter = item["content"].split("\t||\t")[1]
            elif "(" in item["content"]:
                utter = item["content"].split(")")[1]
            else:
                utter = item["content"]
            history_str.append(f"(round {round_id}){item['role']}:{utter}") 
        else:
            history_str.append(f"(round {round_id}){item['role']}:{item['content']}")
    return "\n".join(history_str)


class VllmQwenModel():
    def __init__(self, model_path: Optional[Path]) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.sampling_params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=256)
        self.vllm_model = LLM(model=model_path, tensor_parallel_size=1)  

    def generate(self, system_info:str, prompt_info:str):
        messages = [
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt_info}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        outputs = self.vllm_model.generate([text], self.sampling_params, use_tqdm=False)
        generated_text_list = []
        for output in outputs:
            prompt = output.prompt
            generated_text = output.outputs[0].text
            generated_text_list.append(generated_text)
        return  generated_text_list[0]
    
    



class MultiProcessLLm():
    def __init__(self) -> None:
        self.file_lock = Lock()
        self.system_prompt = "you are an assistant"
    
    def __process_dialog_format_on_gpu(self,
                                       position:Optional[int], 
                                       gpu_id:Optional[int], 
                                       data_chunk:Optional[List[Dict]], 
                                       output_file:Optional[Path],
                                       use_prompt:Optional[str], 
                                       llm_model_path:Optional[Path],
                                       task_type: Optional[str]="sft"):
        
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id) 
        self.llm = VllmQwenModel(model_path=llm_model_path)
        chunk_size = len(data_chunk)

        for i in tqdm(range(chunk_size), position=position, total=chunk_size, desc=f"construct_{task_type}Data_{gpu_id}"):
            if task_type == "sft":
                dialogure_history = convert_qwen_format_to_str(data_chunk[i]["messages"])
                cur_prompt =  use_prompt.replace("history", dialogure_history)
                llm_result = self.llm.generate(system_info=self.system_prompt,
                                                prompt_info=cur_prompt)
                line = data_chunk[i] 
                line["from_gpu"] = gpu_id
                line["llm_result"] = llm_result
            elif task_type == "reward":
                dialogure_history = convert_qwen_format_to_str(data_chunk[i]["history"])
                cur_prompt =  use_prompt.replace("chat_history", dialogure_history).replace("candidates", str(data_chunk[i]['candidates']))
                llm_result = self.llm.generate(system_info=self.system_prompt,
                                                prompt_info=cur_prompt)
                line = data_chunk[i] 
                line["from_gpu"] = gpu_id
                line["llm_result"] = llm_result
            ### 增加支持 主题和搜索词的 数据构造 topic, search_text
            elif task_type == "topic_qa":
                cur_prompt =  use_prompt.replace("sentence", str(data_chunk[i]['sentence']))
                llm_result = self.llm.generate(system_info=self.system_prompt,
                                                prompt_info=cur_prompt)
                llm_result = llm_result.replace("答: ", "")
                line = data_chunk[i] 
                line["from_gpu"] = gpu_id
                line["llm_result"] = llm_result
            else:
                return

          
            with self.file_lock:
                with open(output_file, 'a') as f:
                    f.write(json.dumps(line, ensure_ascii=False) + '\n')

            

    def __split_data(self, data, num_chunks):
        chunk_size = len(data) // num_chunks
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def multi_gpu_processing(self,
                             init_data:Optional[List[Dict]], 
                             save_path:Optional[Path],
                             use_prompt:Optional[str],
                             set_gpus_list:Optional[int],
                             llm_model_path:Optional[Path]='/data/yuzj/modelhub/Qwen2-72B-Instruct-GPTQ-Int4',
                             task_type: Optional[str]="sft"):
        num_gpus = len(set_gpus_list)
        data_chunks = self.__split_data(data=init_data, 
                                     num_chunks=num_gpus)
        
        processes = []
        for i in range(num_gpus):
            p  = Process(target=self.__process_dialog_format_on_gpu, args=(i, set_gpus_list[i], data_chunks[i], save_path, use_prompt, llm_model_path, task_type))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()


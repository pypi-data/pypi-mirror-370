import pandas as pd
from tqdm import tqdm
from transformers import AutoTokenizer
import os
from vllm import LLM, SamplingParams
from typing import Optional
from pathlib import Path


def load_data(file_path):
    """加载Excel文件"""
    return pd.read_excel(file_path)

def prepare_data(dataframe):
    """准备数据"""
    return [[row["搜索词"], row["答疑"]] for _, row in dataframe.iterrows()]

def save_intermediate_results(results, file_path):
    """保存中间结果"""
    df = pd.DataFrame(results, columns=["搜索词", "答疑", "AI改写后的答疑"])
    df.to_excel(file_path, index=False)

def load_intermediate_results(file_path):
    """加载中间结果"""
    if os.path.exists(file_path):
        return pd.read_excel(file_path).values.tolist()
    else:
        return []

def generate_responses(model, tokenizer, data, sampling_params, temp_save_path, batch_size=64):
    """生成响应"""
    new_data = []
    for start_idx in tqdm(range(0, len(data), batch_size), desc="inference:"):
        batch = data[start_idx:start_idx + batch_size]
        text_list = [tokenizer.apply_chat_template([{"role": "user", "content": item[1]}], 
                                                   tokenize=False,
                                                   add_generation_prompt=True) for item in batch]
        
        outputs = model.generate(text_list, sampling_params, use_tqdm=False)
        
        for (search_term, original_answer), output in zip(batch, outputs):
            generated_text = output.outputs[0].text
            new_data.append([search_term, original_answer, generated_text])
            
        # 实时保存每一批次的结果
        save_intermediate_results(new_data, temp_save_path)
    
    return new_data

def main(init_file_path:Optional[Path]="./性病科new.xlsx",
         final_save_path:Optional[Path]="./性病科改写.xlsx",
         temp_save_path:Optional[Path]="./性病科改写_临时.xlsx",
         rewrite_model_path:Optional[Path]="/data/yuzj/vscodeWorkSpace/RewriteProject/saved_model/rewrite_model_7b"
         ):

    # 加载数据
    init_data = load_data(init_file_path)
    
    # 初始化模型和tokenizer
    tokenizer = AutoTokenizer.from_pretrained(rewrite_model_path)
    model = LLM(model=rewrite_model_path, tensor_parallel_size=4, enforce_eager=True, gpu_memory_utilization=0.9)
    sampling_params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=512)
    
    try:
        # 检查是否有中间文件，如果有则加载
        intermediate_results = load_intermediate_results(temp_save_path)
        if intermediate_results:
            print(f"发现中间结果文件 {temp_save_path}, 将从中恢复.")
            completed_items = {tuple(item[:2]) for item in intermediate_results}
            remaining_data = [item for item in prepare_data(init_data) if tuple(item) not in completed_items]
        else:
            remaining_data = prepare_data(init_data)
        
        # 继续处理剩余的数据
        results = generate_responses(model, tokenizer, remaining_data, sampling_params, temp_save_path)
        
        # 合并已有的中间结果与新产生的结果
        all_results = intermediate_results + results
        
        # 最终保存所有结果
        save_intermediate_results(all_results, final_save_path)
        print("所有任务完成，最终结果已保存至:", final_save_path)
        
        # 删除临时文件
        if os.path.exists(temp_save_path):
            os.remove(temp_save_path)
            print(f"删除了临时文件 {temp_save_path}")
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"发生错误: {e}")


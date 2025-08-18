"""
unsloth_env_test_wjz718 - A minimal PyPI package example.

This package provides a single function `get_readme` that returns a simple tutorial.
"""
__version__ = "0.1.1"   # ← 必须要有

def get_readme() -> str:
    """
    Return a simple tutorial string.
    """
    return """
# readme.py
pip install "unsloth[cu124-torch260] @ git+https://github.com/unslothai/unsloth.git"
pip install "unsloth[cu124-torch260]"
pip install vllm==0.8.5.post1

# vllm_run_openai.py
CUDA_VISIBLE_DEVICES=1  python3 -m vllm.entrypoints.openai.api_server \
    --model /home/jovyan/work/models/Qwen/Qwen3-4B \
    --port 8000 \
    --max-model-len 2048 \
    --served-model-name  qwen3-4b \
    --enable-reasoning \
    --reasoning-parser deepseek-r1 \
    --gpu_memory_utilization 0.5 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes

# vllm_run_openai_test.py
import asyncio
import csv
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio

# 配置
INPUT_CSV = "test.csv"
OUTPUT_CSV = "output.csv"
CONCURRENT_TASKS = 4  # 并发数量
API_URL = "http://localhost:8000/v1"

client = AsyncOpenAI(base_url=API_URL, api_key="EMPTY")


# # 额外,定义json schema
# from pydantic import BaseModel
# from enum import Enum
# class CarType(str, Enum):
#     sedan = "sedan"
#     suv = "SUV"
#     truck = "Truck"
#     coupe = "Coupe"

# class CarDescription(BaseModel):
#     brand: str
#     model: str
#     car_type: CarType

# json_schema = CarDescription.model_json_schema()

# simplified_sql_grammar = \"\"\"
#     root ::= select_statement

#     select_statement ::= "SELECT " column " from " table " where " condition

#     column ::= "col_1 " | "col_2 "

#     table ::= "table_1 " | "table_2 "

#     condition ::= column "= " number

#     number ::= "1 " | "2 "
# \"\"\"


async def fetch_response(prompt: str):
    # 调用 vLLM/OpenAI 接口生成响应
    resp = await client.chat.completions.create(
        model="qwen3-4b",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=256,
        extra_body={
            "guided_choice": ["positive", "negative"],
            # "guided_regex": r"\w+@\w+\.com\n", "stop": ["\n"],
            # "guided_regex": r"\w+@\w+\.com\n", "stop": ["\n"],
            # "guided_grammar": simplified_sql_grammar,
            "chat_template_kwargs": {"enable_thinking": False}
            },
        # response_format = {
        # "type": "json_schema",
        # "json_schema": {
        #     "name": "car-description",
        #     "schema": CarDescription.model_json_schema()
        #     },
        # },
    )
    
    print("========")
    result = resp.choices[0].message.content
    print(result)
    print("========")
    return result

async def worker(semaphore, prompt, row_index, results):
    # 控制并发
    async with semaphore:
        try:
            output = await fetch_response(prompt)
            results[row_index] = output
        except Exception as e:
            print(e)
            results[row_index] = f"ERROR: {e}"

async def main():
    # 读取 CSV
    print("读取csv")
    prompts = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append(row["instruction"])
    prompts = prompts[0:1000]
    results = [None] * len(prompts)
    semaphore = asyncio.Semaphore(CONCURRENT_TASKS)
    
    tasks = [
        worker(semaphore, prompt, idx, results)
        for idx, prompt in enumerate(prompts)
    ]
    
    # 使用 tqdm_asyncio 包裹 asyncio.gather
    for f in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
        await f

    # 写入 CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["input", "output"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for inp, out in zip(prompts, results):
            writer.writerow({"input": inp, "output": out})


if __name__ == "__main__":
    asyncio.run(main())

# unsloth_run_train.py
# 导入必要的库  
from unsloth import FastLanguageModel  
import torch  
from trl import SFTTrainer, SFTConfig  
from datasets import load_dataset  
  
# 设置基本参数  
max_seq_length = 2048  
lora_rank = 16  
  
# 1. 加载Qwen3-4B模型  
model, tokenizer = FastLanguageModel.from_pretrained(  
    model_name="/workspace/AIprojects/models/Qwen3-0.6B",  # 或使用 "Qwen/Qwen3-4B"  
    max_seq_length=max_seq_length,  
    load_in_4bit=True,  # 4位量化以减少内存使用  
    # load_in_8bit=False,  
    # token="hf_...",  # 如果使用受限模型需要token  
)  
  
# 2. 配置LoRA参数  
model = FastLanguageModel.get_peft_model(  
    model,  
    r=lora_rank,  # LoRA秩，建议值：8, 16, 32, 64  
    target_modules=[  
        "q_proj", "k_proj", "v_proj", "o_proj",  
        "gate_proj", "up_proj", "down_proj",  
    ],  
    lora_alpha=lora_rank,  # LoRA缩放参数  
    lora_dropout=0,  # Dropout率，0是优化的  
    bias="none",  # 偏置设置，"none"是优化的  
    use_gradient_checkpointing="unsloth",  # 内存优化  
    random_state=3407,  
    use_rslora=False,  # 秩稳定LoRA  
    loftq_config=None,  # LoftQ配置  
)  
  
# 3. 准备数据集  
# 使用Alpaca数据集作为示例  
# url = "https://huggingface.co/datasets/laion/OIG/resolve/main/unified_chip2.jsonl"  
# dataset = load_dataset("json", data_files={"train": url}, split="train")  

dataset = load_dataset("csv", data_files="alpaca.csv")['train']
  
# 4. 配置训练参数  
trainer = SFTTrainer(  
    model=model,  
    train_dataset=dataset,  
    tokenizer=tokenizer,  
    args=SFTConfig(  
        max_seq_length=max_seq_length,  
        per_device_train_batch_size=16,  # 每设备批次大小  2 
        gradient_accumulation_steps=1,  # 梯度累积步数  4
        warmup_steps=10,  # 预热步数  
        max_steps=50000,  # 最大训练步数  
        learning_rate=2e-4,  # 学习率  
        logging_steps=1,  
        output_dir="outputs",  
        optim="adamw_8bit",  # 8位优化器  
        seed=3407,  
        save_strategy="steps",  # 按步保存
        save_steps=1000,        # 每1000步保存一次
        save_total_limit=3,     # 最多保留3个checkpoint
    ),  
)  
  
# 5. 开始训练  
trainer.train()  
  
# 6. 保存模型  
model.save_pretrained("qwen3-4b-lora")  
tokenizer.save_pretrained("qwen3-4b-lora")  
  
# # 7. 推理使用示例  
# # 切换到推理模式  
# FastLanguageModel.for_inference(model)  
  
# # 准备输入  
# inputs = tokenizer(  
#     [  
#         "你好，请介绍一下人工智能的发展历史。"  
#     ], return_tensors="pt").to("cuda")  
  
# # 生成回复  
# outputs = model.generate(**inputs, max_new_tokens=256, use_cache=True)  
# print(tokenizer.batch_decode(outputs))


# merge_model.py
from unsloth import FastLanguageModel

# 1. 加载基座 + LoRA
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "/workspace/AIprojects/models/Qwen3-0.6B",
    adapter_name = "/workspace/AIprojects/unsloth_learn/qwen3-4b-lora"
)

# 2. 合并权重（LoRA 融合到基座）
model.save_pretrained("/workspace/AIprojects/unsloth_learn/qwen3-4b-lora-merged")
tokenizer.save_pretrained("/workspace/AIprojects/unsloth_learn/qwen3-4b-lora-merged")
"""
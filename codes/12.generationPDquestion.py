# 循环脚本
import json
import math
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from typing import List, Optional

class Question(BaseModel):
    question: str = Field(description="基于文本生成的问题内容")
    answer1: str = Field(description="问题对应的答案1")
    answer2: str = Field(description="问题对应的答案2")

client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"
    ),
    mode=instructor.Mode.JSON
)

input_path = 'demo/output/chunksscore.json' 
output_path = 'demo/output/PDquestion.json'

domain = "##"
char = 200 # 每200个字符生成一道题

with open("prompts/prompt7.txt", 'r', encoding='utf-8') as f:
    prompt_template = f.read()

with open(input_path, 'r', encoding='utf-8') as f:
    data: List[dict] = json.load(f)

all_generated_questions = []

for item in data:
    text = item.get("text", "")
    item_id = item.get("id")
    source_file = item.get("source_file")
    
    # 1. 计算需要生成的题目数量 (扁平化逻辑)
    text_length = len(text.strip())
    num_questions = 0
    if text_length > 0:
        # 向上取整，确保不足 200 个字符也生成 1 题
        num_questions = math.ceil(text_length / char)

    print(f"\n--- 正在处理 ID={item_id} --- 长度: {text_length} 字符, 需生成题目数: {num_questions}")

    if num_questions == 0:
        continue

    # 2. 格式化 Prompt
    # 这里的 number 参数指导 LLM 一次性生成所需数量的题目
    prompt = prompt_template.format(
        number=num_questions, 
        domain=domain,
        text=text
    )

    try:
        # 3. LLM 调用
        # 请求返回一个包含 num_questions 个题目的列表
        result_list: List[Question] = client.chat.completions.create(
            model="#####",
            messages=[{"role": "user", "content": prompt}],
            response_model=List[Question], 
            temperature=0.0,
            seed=42
        )
        
        # 4. 数据整合
        for q_obj in result_list:
            question_data = q_obj.model_dump()
            question_data.update({
                "source_file": source_file,
                "id": item_id, 
                "text": text 
            })
            all_generated_questions.append(question_data)

        print(f"   - 成功生成 {len(result_list)} 道题目。")

    except Exception as e:
        print(f"   - 警告：处理 ID={item_id} 时 LLM 调用出错: {e}")

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_generated_questions, f, ensure_ascii=False, indent=2)

print(f"✅ 所有条目处理完成，共生成 {len(all_generated_questions)} 道题目。结果保存至: {output_path}")

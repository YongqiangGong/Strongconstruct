import json
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from typing import List

# 初始化 client（请确保 base_url 正确）
client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"  # 若报404，请确认此URL是否有效
    ),
    mode=instructor.Mode.JSON
)

class Recommendation(BaseModel):
    recommendation: str = Field(description="提取大模型的输出推荐")
    reason: str = Field(description="提取大模型的输出推荐理由")

# 读取提示词模板
with open('prompts/prompt9.txt', 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取输入的 JSON 文件（假设是题目列表）
input_file = "demo/output/PDquestionscore.json"  # 请替换为你的实际文件名
output_file = "demo/output/PDquestionrecommendation.json"

with open(input_file, 'r', encoding='utf-8') as f:
    items: List[dict] = json.load(f)

# 遍历每个题目，让模型从 answer1/2 中选出最优答案，并返回答案原文及推荐理由
for idx, item in enumerate(items):
    print(f"Processing item {idx + 1}/{len(items)}...")
    
    domain = "##"
    question = item["question"]
    answer1 = item["answer1"]
    answer2 = item["answer2"]

    try:
        prompt = prompt_template.format(
            domain=domain,
            question=question,
            answer1=answer1,
            answer2=answer2
        )

        result = client.chat.completions.create(
            model="#####",
            messages=[{"role": "user", "content": prompt}],
            response_model=Recommendation,  # ←←← 改为 Recommendation（不是 Score）
            max_retries=2
        )
        # 保存推荐答案和理由
        item["recommendation"] = result.recommendation
        item["reason"] = result.reason
        print(f"  Selected answer snippet: {result.recommendation[:50]}...")
        print(f"  Reason: {result.reason[:60]}...")
        
    except Exception as e:
        print(f"  Error on item {idx}: {e}")
        item["recommendation"] = ""
        item["reason"] = "Error during LLM evaluation"

# 保存结果
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\n✅ 推荐答案与理由生成完成！结果已保存至 {output_file}")

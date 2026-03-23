################################## 循环脚本
import json
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from typing import List

# 初始化 client
client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"
    ),
    mode=instructor.Mode.JSON
)

class Score(BaseModel):
    score: int = Field(description="提取大模型的输出得分")

with open('prompts/prompt1.txt', 'r', encoding='utf-8') as f:
    prompt_template = f.read()
domain = "##"

input_file = 'demo/output/chunksnumber.json'  # ← 替换为你的实际路径
output_file = 'demo/output/chunksscore.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data: List[dict] = json.load(f)

for item in data:
    text = item.get("text", "")
    if not text.strip():
        item["score"] = 1  # 空文本默认给1分
        continue
    
    prompt = prompt_template.format(domain=domain, text=text)

    try:
        result = client.chat.completions.create(
            model="Qwen3-30B-A3B-Instruct-2507",
            messages=[{"role": "user", "content": prompt}],
            response_model=Score
        )
        item["score"] = result.score
        print(f"已处理ID={item.get('id')}，得分: {result.score}")
    except Exception as e:
        print(f"处理 ID={item.get('id')} 时出错: {e}")
        item["score"] = 1  # 出错时默认给1分或跳过


# 保存结果（保留原格式 + 新增 score 字段）
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"✅ 所有条目已评分，结果保存至: {output_file}")

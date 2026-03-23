import json
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from typing import List

# 初始化 client（请确保 base_url 正确）
client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"
    ),
    mode=instructor.Mode.JSON
)

class Score(BaseModel):
    score: int = Field(description="提取大模型的输出得分", ge=1, le=5)

# 读取提示词模板
with open('prompts/prompt8.txt', 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取输入的 JSON 文件（假设是题目列表）
input_file = "demo/output/PDquestion.json"  # 请替换为你的实际文件名
output_file = "demo/output/PDquestionscore.json"

with open(input_file, 'r', encoding='utf-8') as f:
    items: List[dict] = json.load(f)

# 遍历每个题目进行评分
# 遍历每个题目，对【整道题 + 两个答案】做整体忠实度评分
for idx, item in enumerate(items):
    print(f"Processing item {idx + 1}/{len(items)}...")

    domain = "##"
    question = item["question"]
    answer1 = item["answer1"]
    answer2 = item["answer2"]
    text = item.get("text", "")

    try:
        # 注意：这里假设你的 prompt_template 接收 {domain}, {text}, {question}, {answer1}, {answer2}
        prompt = prompt_template.format(
            domain=domain,
            text=text,
            question=question,
            answer1=answer1,
            answer2=answer2
        )

        result = client.chat.completions.create(
            model="#####",
            messages=[{"role": "user", "content": prompt}],
            response_model=Score,
            max_retries=2
        )
        item["score"] = result.score  # 改用更明确的字段名
        print(f"Score: {result.score}")
    except Exception as e:
        print(f"  Error on item {idx}: {e}")
        item["score"] = -1  # 标记失败


def clean_null(obj):
    """
    递归移除字典中值为 None 的键（包括嵌套字典）
    """
    if isinstance(obj, dict):
        return {
            k: clean_null(v)
            for k, v in obj.items()
            if v is not None
        }
    elif isinstance(obj, list):
        return [clean_null(item) for item in obj]
    else:
        return obj

items = clean_null(items)

# 保存结果
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\n✅ 评分完成！结果已保存至 {output_file}")


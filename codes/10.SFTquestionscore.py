import json
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from typing import List
import re

# 初始化 client（请确保 base_url 正确）
client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"  # 若报404，请确认此URL是否有效
    ),
    mode=instructor.Mode.JSON
)

class Score(BaseModel):
    score: int = Field(description="提取大模型的输出得分", ge=1, le=5)

# 读取提示词模板
with open('prompts/prompt6.txt', 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取输入的 JSON 文件（假设是题目列表）
input_file = "demo/output/SFTquestion.json"  # 请替换为你的实际文件名
output_file = "demo/output/SFTquestionscore.json"

with open(input_file, 'r', encoding='utf-8') as f:
    items: List[dict] = json.load(f)

# 遍历每个题目进行评分
for idx, item in enumerate(items):
    print(f"Processing item {idx + 1}/{len(items)}...")

    domain = "##"
    question = item["question"]
    answer = item["answer"]
    text = item.get("text", "")
    options = item.get("options", None)

    # 构造 prompt
    if options is not None and isinstance(options, dict) and answer is not None:
        options_str = "\n".join([f"{k}: {v}" for k, v in options.items()])
        answer_str = str(answer) if not isinstance(answer, str) else answer
        letters = re.findall(r'[A-Z]', answer_str.upper())
        # 如果没提取到任何字母，就原样使用answer
        if not letters:
            full_answer = f"{answer}（无效答案）"
            print(f"  ⚠️ 警告：未识别到有效选项字母，原始答案: {answer}")
        else:
            # 逐个字母查找对应选项内容
            parts = []
            for letter in letters:
                if letter in options:
                    parts.append(f"{letter}（{options[letter]}）")
                else:
                    parts.append(f"{letter}（选项未定义）")
            full_answer = "、".join(parts)
        # 构造最终 prompt
        prompt = prompt_template.format(
            domain=domain,
            text=text,
            question=question,
            answer=full_answer,
            options=options_str
        )
    else:
        # 非选择题或 options 缺失的情况
        prompt = prompt_template.format(
            domain=domain,
            text=text,
            question=question,
            answer=str(answer) if answer is not None else "",
            options=""
        )

    try:
        result = client.chat.completions.create(
            model="#####",
            messages=[{"role": "user", "content": prompt}],
            response_model=Score,
            max_retries=2
        )
        item["score"] = result.score
        print(f"  Score: {result.score}")
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


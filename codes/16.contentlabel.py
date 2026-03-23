import json
from pydantic import BaseModel, Field
from enum import Enum
import instructor
from openai import OpenAI
from typing import List
import re
# 初始化 client
client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"
    ),
    mode=instructor.Mode.JSON
)

# 定义内容类型枚举（必须严格匹配输出要求）
class ContentType(str, Enum):
    content_type1 = "病因病理"
    content_type2 = "临床表现"
    content_type3= "诊断治疗"
    content_type4 = "文献指南"
    content_type5 = "其他"

class Content(BaseModel):
    content: ContentType = Field(description="题目所属的内容类型")

# 读取提示词模板
with open('prompts/prompt10.txt', 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 输入输出文件路径
input_file = "demo/output/SFTquestionscore.json"
output_file = "demo/output/contentlabel.json"

# 加载题目数据
with open(input_file, 'r', encoding='utf-8') as f:
    items: List[dict] = json.load(f)

# 遍历每个题目进行分类
for idx, item in enumerate(items):
    print(f"Processing item {idx + 1}/{len(items)}...")

    domain = "##"
    question = item["question"]
    answer = item["answer"]
    text = item.get("text", "")
    options = item.get("options", None)

    # 构造 options_block（保持与模板一致）
    if options is not None:
        # 构造选项字符串块（带“选项：”前缀）
        options_str = "\n".join([f"{k}: {v}" for k, v in options.items()])
        options_block = f"选项：\n{options_str}"
        answer_str = str(answer)  # 确保是字符串符
        letters = re.findall(r'[A-Z]', answer_str.upper())
        if not letters:
            # 如果没提取到任何字母，保留原始 answer 并标记
            full_answer = f"{answer}（无效答案）"
            print(f"  ⚠️ 警告：无法解析答案 '{answer}'，未找到有效选项字母")
        else:
            # 逐个字母查找对应内容
            parts = []
            for letter in letters:
                if letter in options:
                    parts.append(f"{letter}（{options[letter]}）")
                else:
                    parts.append(f"{letter}（选项未定义）")
            full_answer = "、".join(parts)
    else:
        options_block = ""
        full_answer = str(answer) if answer is not None else ""

    # 填充提示词
    prompt = prompt_template.format(
        domain=domain,
        text=text,
        question=question,
        answer=full_answer,
        options=options_block  # 注意：模板中应使用 {options}，此处传入的是带“选项：”前缀的字符串
    )

    try:
        result = client.chat.completions.create(
            model="#####",
            messages=[{"role": "user", "content": prompt}],
            response_model=Content,
            max_retries=2
        )
        item["content"] = result.content.value  # 存为字符串
        print(f"  Content type: {result.content.value}")
    except Exception as e:
        print(f"  Error on item {idx}: {e}")
        item["content"] = "其他"  # 或设为 None，根据需求

# 保存结果
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\n✅ 内容分类完成！结果已保存至 {output_file}")
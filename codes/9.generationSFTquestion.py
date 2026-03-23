import json
import math
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from typing import List, Type, Any
import importlib

# ==================== 配置区：在这里选择你要生成的题型 ====================
selected_question_type = "选择题"  # 可选: "选择题", "填空题", "判断题", "简答题"
# ======================================================================

# 题型配置：映射到模型文件和提示词文件
QUESTION_CONFIG = {
    "选择题": ("question1", "prompt2.txt"),
    "填空题": ("question2", "prompt3.txt"),
    "判断题": ("question3", "prompt4.txt"),
    "简答题": ("question4", "prompt5.txt"),
}

if selected_question_type not in QUESTION_CONFIG:
    raise ValueError(f"不支持的题型: {selected_question_type}。请选择: {list(QUESTION_CONFIG.keys())}")

module_name, prompt_file = QUESTION_CONFIG[selected_question_type]

# 初始化 OpenAI + Instructor 客户端
client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"
    ),
    mode=instructor.Mode.JSON
)

input_path = 'demo/output/chunksscore.json'
output_path = 'demo/output/SFTquestion.json'

domain = "#####"
char = 400  # 每200字符生成1题

# 加载提示词模板
with open(f"prompts/{prompt_file}", 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 动态导入对应的 Question 模型
QuestionModel: Type[BaseModel] = getattr(importlib.import_module(f"question_type.{module_name}"), "Question")

# 读取输入数据
with open(input_path, 'r', encoding='utf-8') as f:
    data: List[dict] = json.load(f)

all_generated_questions = []

for item in data:
    text = item.get("text", "").strip()
    item_id = item.get("id")
    source_file = item.get("source_file")

    if not text:
        continue

    text_length = len(text)
    num_questions = math.ceil(text_length / char)
    print(f"\n--- 处理 ID={item_id} --- 文本长度: {text_length}, 生成 {num_questions} 道 {selected_question_type}")

    try:
        prompt = prompt_template.format(
            number=num_questions,
            domain=domain,
            text=text
        )

        result_list: List[Any] = client.chat.completions.create(
            model="#####",
            messages=[{"role": "user", "content": prompt}],
            response_model=List[QuestionModel],
            # temperature=0.7,
            # seed=42
        )

        for q_obj in result_list:
            question_data = q_obj.model_dump()
            question_data.update({
                "source_file": source_file,
                "id": item_id,
                # "question_type": selected_question_type,
                "text": text
            })
            all_generated_questions.append(question_data)

        print(f"   ✅ 成功生成 {len(result_list)} 道题目。")

    except Exception as e:
        print(f"   ❌ 处理 ID={item_id} 时出错: {e}")

# 保存结果（文件名包含题型）
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_generated_questions, f, ensure_ascii=False, indent=2)

print(f"\n🎉 共生成 {len(all_generated_questions)} 道《{selected_question_type}》，结果已保存至:\n{output_path}")


#################### 读取contentlabel.json
with open("demo/output/contentlabel.json", "r", encoding="utf-8") as f:
    contentlabel = json.load(f)

##################### 进行相关人体系统注释（第一轮系统注释）
from enum import Enum
import json
from pathlib import Path
from pydantic import BaseModel, Field
from openai import OpenAI
import instructor
from enum import Enum

client = instructor.from_openai(
    OpenAI(
        api_key="#####",
        base_url="#####"
    ),
    mode=instructor.Mode.JSON
)

# 读取提示词模板
with open("prompts/prompt11.txt", 'r', encoding='utf-8') as f:
    prompt_template = f.read()

class MedicalSystem(str, Enum):
    System1="呼吸系统"
    System2="心血管系统"
    System3="消化系统"
    System4="泌尿系统"
    System5="血液系统"
    System6="内分泌系统"
    System7="风湿性疾病"
    System8="运动系统"
    System9="传染病、性病"
    System10="产科学"
    System11="妇科学"
    System12="儿科疾病"
    System13="神经内外科疾病"
    System14="精神病"
    System15="其他"

class System(BaseModel):
    system: MedicalSystem=Field(None,description="题目所属的相关人体系统")

systemlabel=[]
for entry in contentlabel:
    id=entry["id"]
    question=entry["question"]
    options = entry.get("options", None)
    answer=entry["answer"]
    content=entry["content"]
    #################### 构造 options 字符串（用于提示词）
    if options:
        options_str = "\n".join([f"{k}. {v}" for k, v in options.items() if v is not None])
    else:
        options_str = "（本题无选项，为非选择题）"
    #################### 构造 prompt
    prompt = prompt_template.format(question=question, options=options_str, answer=answer)
    #################### 调用 OpenAI API
    response = client.chat.completions.create(
        model="#####",
        messages=[{"role": "user", "content": prompt}],
        response_model=System,
        max_retries=2,
    )
    result = {
            "id": id,
            "question": question,
            "options": options,
            "answer": answer,
            "content": content,
            "system": response.system.value
        }
    systemlabel.append(result)
    print(f"  ✅ 题目 {question}: 系统 = '{response.system.value}'")

########################## 清洗null
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

systemlabel = clean_null(systemlabel)

with open("demo/output/systemlabel.json", "w", encoding="utf-8") as f:
    json.dump(systemlabel, f, ensure_ascii=False, indent=2)




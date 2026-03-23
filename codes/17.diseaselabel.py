#################### 读取systemlabel.json
with open("demo/output/systemlabel.json", "r", encoding="utf-8") as f:
    systemlabel = json.load(f)

##################### 
from enum import Enum
import json
from pathlib import Path
from pydantic import BaseModel, Field
from openai import OpenAI
import instructor
from enum import Enum
import importlib
import os

client = instructor.from_openai(
    OpenAI(
        api_key="####",
        base_url="#####"
    ),
    mode=instructor.Mode.JSON
)

# 读取提示词模板
with open("prompts/prompt12.txt", 'r', encoding='utf-8') as f:
    prompt_template = f.read()

disease_path= "disease"

diseaselabel=[]
for entry in systemlabel:
    id=entry["id"]
    question=entry["question"]
    options = entry.get("options", None)
    answer=entry["answer"]
    content=entry["content"]
    system=entry["system"]

    #################################### 动态加载system对应的disease标签
    file_path = os.path.join(disease_path, f"{system}.py")
    # 检查是否存在 
    if not os.path.exists(file_path):
        print(f"⚠️ 警告: 未找到系统 '{system}' 对应的枚举文件: {file_path}")
        entry["disease"] = None
        continue
    # 动态加载模块
    spec = importlib.util.spec_from_file_location(f"{system}_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # 获取 Disease 类
    if not hasattr(module, 'Disease'):
        print(f"❌ 错误: 文件 {file_path} 中未定义 'Disease' 类")
        entry["disease"] = None
        continue
    DiseaseEnum = module.Disease  # 直接拿到 Enum 类

    ######################################### 构造选项字符串
    if options:
        options_str = "\n".join([f"{k}. {v}" for k, v in options.items() if v is not None])
    else:
        options_str = "（本题无选项，为非选择题）"

    ######################################### 疾病列表字符串
    disease_list_str = "\n".join([f"- {item.value}" for item in DiseaseEnum])

    ######################################### 填充提示词
    prompt = prompt_template.format(
        disease_list=disease_list_str,
        question=question,
        options=options_str,
        answer=answer)

    # 动态创建 Pydantic 模型（使用刚加载的 DiseaseEnum）
    class DiseaseAnnotation(BaseModel):
        disease: DiseaseEnum = Field(..., description="题目所属条目")
    
    ######################################### 调用大模型进行注释
    try:
        response = client.chat.completions.create(
            model="#####",
            messages=[{"role": "user", "content": prompt}],
            response_model=DiseaseAnnotation,
            max_retries=2,
        )
        result = {
            "id": id,
            "question": question,
            "options": options,
            "answer": answer,
            "content": content,
            "system": system,
            "disease": response.disease.value
        }
        diseaselabel.append(result)
        print(f"✅ ID {id} ({system}) → {response.disease.value}")

    except Exception as e:
        print(f"❌ ID {id} 推理失败: {e}")
        entry["disease"] = None

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

diseaselabel = clean_null(diseaselabel)

with open("demo/output/diseaselabel.json", "w", encoding="utf-8") as f:
    json.dump(diseaselabel, f, ensure_ascii=False, indent=2)

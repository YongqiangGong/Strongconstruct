################################################################## TIGERUI
print("\n🤖 欢迎使用 Strongconstruct ！")

import threading
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import time

app = FastAPI()

# 挂载当前目录，自动服务所有 HTML/CSS/JS
app.mount("/", StaticFiles(directory="TIGER_UI", html=True), name="site")

def start_server():
    global server_started
    
    # 启动uvicorn服务（使用回调确保启动完成后标记状态）
    config = uvicorn.Config(app, host="0.0.0.0", port=6969, log_level="warning")
    server = uvicorn.Server(config)
    
    # 先打印启动提示（确保顺序）
    print("🌐 TIGER UI 已启动！访问 http://<服务器IP>:6969")
    # 启动服务（此方法会阻塞线程，直到服务停止）
    server.run()

def wait_for_server():
    """等待Web服务启动完成的辅助函数"""
    global server_started
    # 启动Web线程
    web_thread = threading.Thread(target=start_server, daemon=True)
    web_thread.start()
    
    # 短暂等待确保服务启动日志先输出（避免线程调度延迟）
    time.sleep(1)

# 先启动Web服务并等待其日志输出
wait_for_server()

################################################################## 配置信息

print("请依次提供以下配置信息：\n")

def safe_input(prompt: str) -> str:
    """安全输入：确保不为空"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("❌ 输入不能为空，请重新输入。")

input_path = safe_input("1️⃣ 请输入 PDF 文件路径（如 /home/user/pdfs）注意必须在pdfs目录下: ")
output_path = safe_input("2️⃣ 请输入输出目录路径（如 /home/user/output）: ")
model_api = safe_input("3️⃣ 请输入模型服务 API（如 https://dashscope.aliyuncs.com/compatible-mode/v1）: ")
model_name = safe_input("4️⃣ 请输入模型名称（如 qwen3-max）: ")
model_key = safe_input("5️⃣ 请输入模型密钥（如sk-2d7c12272772）: ")
domain = safe_input("6️⃣ 请输入领域（如 肝胆疾病）: ")

# 库、包、函数
print("正在加载依赖库，请稍候……")
import os
import sys
import shutil
import subprocess
import re
import math
from pathlib import Path
from enum import Enum
from typing import List, Optional, Type, Any
import json
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from chonkie import SlumberChunker
from chonkie.genie import OpenAIGenie
import importlib

#################################################################### mineru
print("开始进行文本转换，请稍后……")

mineru_output = os.path.join(output_path, "mineru")
os.makedirs(mineru_output, exist_ok=True)
try:
    result = subprocess.run(
        ["python", "codes/1.mineru.py", input_path, mineru_output],
        check=True,              # 如果子进程返回非0，抛出异常
        text=True,               # 以文本模式处理 stdout/stderr
        capture_output=False     # 直接让子进程输出打印到终端（不捕获）
    )
    print(f"\n✅ mineru 脚本执行成功！结果保存至: {mineru_output}")
except subprocess.CalledProcessError as e:
    print(f"\n❌ mineru 脚本执行失败！返回码: {e.returncode}")
    # 如果 capture_output=True，可以用 e.stdout/e.stderr 查看日志
except FileNotFoundError:
    print("\n❌ 找不到 'codes/1.mineru.py' 文件，请检查路径是否正确！")


################################################################### 提取md文档

#################################################################### 提取 Markdown 文件
print("开始进行 Markdown 文件提取，请稍后……")

def sanitize_filename(name, max_length=200):
    """
    清理文件名中的非法字符，并限制长度。
    """
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    name = name.strip(' .')
    if not name:
        name = "unnamed"
    if len(name) > max_length:
        root, ext = os.path.splitext(name)
        ext = ext[:max_length - 10] if len(ext) > max_length - 10 else ext
        root_max = max_length - len(ext)
        if root_max > 0:
            name = root[:root_max - 3] + "..." + ext
        else:
            name = "longname" + ext
    return name

def copy_all_markdown_files(source_root, target_dir):
    """
    从 source_root 下每个子目录的 auto/ 中复制 .md 文件到 target_dir。
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    for individual_dir in source_root.iterdir():
        if not individual_dir.is_dir():
            continue

        auto_dir = individual_dir / "auto"
        if not auto_dir.exists() or not auto_dir.is_dir():
            print(f"⚠️ 警告: {individual_dir.name} 下没有 auto 目录，跳过。")
            continue

        for md_file in auto_dir.glob("*.md"):
            if not md_file.is_file():
                continue

            safe_individual = sanitize_filename(individual_dir.name, max_length=80)
            safe_md_name = sanitize_filename(md_file.name, max_length=120)
            new_name = f"{safe_individual}__{safe_md_name}"
            new_name = sanitize_filename(new_name, max_length=255)

            target_path = target_dir / new_name

            if target_path.exists():
                print(f"ℹ️ 注意: {target_path.name} 已存在，将被覆盖。")

            try:
                shutil.copy2(md_file, target_path)
                print(f"✅ 已复制: {md_file} → {target_path}")
            except OSError as e:
                print(f"❌ 复制失败: {md_file} → {target_path}\n    错误: {e}")

# 使用前面用户输入的 output_path
source_root = Path(output_path) / "mineru"
target_dir = Path(output_path) / "md"

print("\n📂 正在从 mineru 结果中提取 Markdown 文件……")
if not source_root.exists():
    print(f"❌ 错误: 源目录不存在: {source_root}")
else:
    copy_all_markdown_files(source_root, target_dir)
    print(f"\n🎉 所有 Markdown 文件已保存至: {target_dir}")

################################################################## 开始进行文本分割
print("开始进行文本分割，请稍后……")

# 构建路径
input_dir = Path(output_path) / "md"
output_dir = Path(output_path) / "chunks"
output_dir.mkdir(parents=True, exist_ok=True)

# 检查输入目录是否存在
if not input_dir.exists() or not any(input_dir.glob("*.md")):
    print(f"⚠️ 警告: 输入目录 {input_dir} 不存在或没有 .md 文件，跳过文本分割。")
else:
    # 初始化 Genie（使用用户输入的模型配置）
    try:
        genie = OpenAIGenie(
            model=model_name,          # 来自 safe_input 第4项
            base_url=model_api,        # 来自 safe_input 第3项
            api_key=model_key,         # 来自 safe_input 第5项
        )
    except Exception as e:
        print(f"❌ 初始化 Genie 失败: {e}")
        exit(1)

    # 初始化 Chunker
    chunker = SlumberChunker(
        genie=genie,
        tokenizer="character",
        chunk_size=5000,
        candidate_size=5000,
        min_characters_per_chunk=25,
        verbose=True
    )

    # 遍历所有 .md 文件
    md_files = list(input_dir.glob("*.md"))
    if not md_files:
        print(f"⚠️ 警告: {input_dir} 中没有找到 .md 文件。")
    else:
        for md_file in md_files:
            print(f"Processing: {md_file.name}")
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    text = f.read()

                chunks = chunker.chunk(text)

                # 构建输出 JSON 文件路径
                json_file = output_dir / f"{md_file.stem}.json"

                # 转为可序列化的列表
                records = []
                for chunk in chunks:
                    record = {
                        "text": getattr(chunk, 'text', str(chunk))
                    }
                    records.append(record)

                # 写入 JSON
                with open(json_file, "w", encoding="utf-8") as out_f:
                    json.dump(records, out_f, ensure_ascii=False, indent=2)

                print(f"✅ Saved: {json_file}")

            except Exception as e:
                print(f"❌ Error processing {md_file}: {e}", file=sys.stderr)

    print(f"\n🎉 文本分割完成！结果已保存至: {output_dir}")


################################################################## 开始进行文本合并
print("开始合并所有分块文件为 chunksmerge.json，请稍后……")

# 构建路径
input_dir = Path(output_path) / "chunks"
output_dir = Path(output_path)  # 合并文件放在 output_path 根目录下
merged_file = output_dir / "chunksmerge.json"

# 检查输入目录是否存在
if not input_dir.is_dir() or not any(input_dir.glob("*.json")):
    print(f"⚠️ 警告: 输入目录 {input_dir} 不存在或没有 .json 文件，跳过合并。")
else:
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输入目录:  {input_dir}")
    print(f"📤 输出文件: {merged_file}")

    all_records = []

    # 按文件名排序处理（保证顺序可重现）
    for json_file in sorted(input_dir.glob("*.json")):
        book_name = json_file.stem
        print(f"  ➤ 正在处理: {book_name}")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"⚠️  跳过 {json_file.name}：不是 JSON 数组", file=sys.stderr)
                    continue
                for record in data:
                    if isinstance(record, dict):
                        new_record = record.copy()
                        new_record["source_file"] = book_name
                        all_records.append(new_record)
                    else:
                        print(f"⚠️  跳过无效条目（非字典） in {json_file.name}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  处理 {json_file.name} 时出错: {e}", file=sys.stderr)

    # 添加全局唯一 id（从 1 开始）
    for idx, record in enumerate(all_records, start=1):
        record["id"] = idx

    # 写入合并文件
    try:
        with open(merged_file, "w", encoding="utf-8") as out_f:
            json.dump(all_records, out_f, ensure_ascii=False, indent=2)
        print(f"\n✅ 合并成功！文件已保存至: {merged_file}")
        print(f"🔢 总共合并记录数: {len(all_records)}")
    except Exception as e:
        print(f"❌ 写入合并文件失败: {e}", file=sys.stderr)
        exit(1)

############################################################## 计算文本块字符数
print("正在为每个分块计算文本长度（字符数）……")
# 输入和输出文件路径
input_file = Path(output_path) / 'chunksmerge.json'
output_file = Path(output_path) / 'chunksnumber.json'

# 读取原始数据
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 为每个 item 添加 number 字段（text 的字符长度）
for item in data:
    text = item.get("text", "")
    item["number"] = len(text)  # 计算字符数（包括空格、换行符等）

# 保存回文件（保留缩进和中文）
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已为 {len(data)} 个条目添加 'number' 字段，结果保存至: {output_file}")

################################################################## 开始进行内容评分
print("正在对每个文本块进行质量评分，请稍候……")

# 初始化 client（使用用户输入的配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,      # ← 来自 safe_input 第5项
            base_url=model_api      # ← 来自第3项
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

# 定义响应模型
class Score(BaseModel):
    score: int = Field(description="提取大模型的输出得分", ge=1, le=5)  # 可选：限制范围

# 读取 prompt 模板
prompt_path = Path("prompts/prompt1.txt")
if not prompt_path.exists():
    print(f"❌ 错误: Prompt 模板文件不存在 → {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 构建输入/输出路径
input_file = Path(output_path) / "chunksnumber.json"
output_file = Path(output_path) / "chunksscore.json"

if not input_file.exists():
    print(f"❌ 错误: 输入文件不存在 → {input_file}")
    exit(1)

# 加载数据
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data: List[dict] = json.load(f)
    if not isinstance(data, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取输入文件失败: {e}")
    exit(1)

# 遍历每条记录进行评分
total = len(data)
processed = 0
for idx, item in enumerate(data, start=1):
    text = item.get("text", "")
    if not text or not text.strip():
        item["score"] = 1
        print(f"[{idx}/{total}] ID={item.get('id')} → 空文本，跳过评分，score=1")
        continue

    # 格式化 prompt（使用用户输入的 domain）
    try:
        prompt = prompt_template.format(domain=domain, text=text)
    except KeyError as e:
        print(f"⚠️ Prompt 模板缺少占位符 {e}，请检查 prompts/prompt1.txt")
        prompt = f"【领域】{domain}\n【文本】{text}\n请为上述文本质量打分（1-5分）："

    try:
        result = client.chat.completions.create(
            model=model_name,  # ← 来自 safe_input 第4项
            messages=[{"role": "user", "content": prompt}],
            response_model=Score,
            max_retries=2  # instructor 自动重试
        )
        item["score"] = result.score
        processed += 1
        print(f"[{idx}/{total}] ID={item.get('id')} → 得分: {result.score}")
    except Exception as e:
        print(f"[{idx}/{total}] ID={item.get('id')} → 评分失败，使用默认 score=1。错误: {e}")
        item["score"] = 1

# 保存结果
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 评分完成！共处理 {processed}/{total} 条有效文本，结果已保存至: {output_file}")
except Exception as e:
    print(f"❌ 保存结果失败: {e}")
    exit(1)

print("📊 评分已完成，请使用TIGERUI检查 chunksscore.json 后按 Enter 继续。")
input("按 Enter 继续...")
#########################################################  生成监督微调数据集
input_path = Path(output_path) / "chunksscore.json"
output_path_file = Path(output_path) / "SFTquestion.json"
# ==================== 题型选择交互 ====================
QUESTION_CONFIG = {
    "选择题": ("question1", "prompt2.txt"),
    "填空题": ("question2", "prompt3.txt"),
    "判断题": ("question3", "prompt4.txt"),
    "简答题": ("question4", "prompt5.txt"),
}

print("📚 请选择要生成的题目类型：")
for i, q_type in enumerate(QUESTION_CONFIG.keys(), start=1):
    print(f"  {i}. {q_type}")

while True:
    user_input = input("\n请输入题型名称 或 编号（如 '选择题' 或 '1'），然后按 Enter: ").strip()

    # 尝试解析为编号
    if user_input.isdigit():
        idx = int(user_input)
        if 1 <= idx <= len(QUESTION_CONFIG):
            selected_question_type = list(QUESTION_CONFIG.keys())[idx - 1]
            break
    # 尝试匹配题型名称（模糊：忽略大小写和空格）
    else:
        for q_type in QUESTION_CONFIG:
            if user_input.lower() == q_type.lower():
                selected_question_type = q_type
                break
        else:
            # 未匹配到
            print(f"❌ 无效输入 '{user_input}'，请重新选择。")
            continue
    break  # 如果是有效名称，也跳出

print(f"✅ 已选择题型: {selected_question_type}")
# 根据选择的题型获取模块名和提示词文件
module_name, prompt_file = QUESTION_CONFIG[selected_question_type]
# ==================== 用户自定义每题字符数 ====================
while True:
    char_input = input(
        f"\n📝 请输入每道题基于多少字符生成（默认 200，建议 200~1000）："
    ).strip()

    if not char_input:
        char = 200
        print(f"✅ 使用默认值: 每 {char} 字符生成 1 道题。")
        break

    if char_input.isdigit():
        char = int(char_input)
        if char > 0:
            print(f"✅ 已设置: 每 {char} 字符生成 1 道题。")
            break
        else:
            print("❌ 字符数必须大于 0，请重新输入。")
    else:
        print("❌ 请输入一个正整数（如 200），或直接按 Enter 使用默认值 200。")
# ===========================================================
domain = domain  # 来自主流程

# 加载提示词模板
prompt_path = Path("prompts") / prompt_file
if not prompt_path.exists():
    raise FileNotFoundError(f"提示词文件不存在: {prompt_path}")

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 动态导入 Question 模型
try:
    QuestionModel: Type[BaseModel] = getattr(
        importlib.import_module(f"question_type.{module_name}"), 
        "Question"
    )
except Exception as e:
    raise ImportError(f"无法加载题型模型 {module_name}.Question: {e}")

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
    num_questions = max(1, math.ceil(text_length / char))  # 至少1题
    print(f"\n--- 处理 ID={item_id} --- 文本长度: {text_length}, 生成 {num_questions} 道 {selected_question_type}")

    try:
        prompt = prompt_template.format(
            number=num_questions,
            domain=domain,
            text=text
        )

        result_list: List[Any] = client.chat.completions.create(
            model=model_name,  # ← 来自 safe_input 第4项
            messages=[{"role": "user", "content": prompt}],
            response_model=List[QuestionModel],
            max_retries=2
        )

        for q_obj in result_list:
            question_data = q_obj.model_dump()
            question_data.update({
                "source_file": source_file,
                "id": item_id,
                "text": text,
                "question_type": selected_question_type
            })
            all_generated_questions.append(question_data)

        print(f"   ✅ 成功生成 {len(result_list)} 道题目。")

    except Exception as e:
        print(f"   ❌ 处理 ID={item_id} 时出错: {e}")

# 保存结果
with open(output_path_file, 'w', encoding='utf-8') as f:
    json.dump(all_generated_questions, f, ensure_ascii=False, indent=2)

print(f"\n🎉 共生成 {len(all_generated_questions)} 道《{selected_question_type}》，结果已保存至:\n{output_path_file}")

################################################################## 对生成的题目进行质量评分
print("正在对生成的题目进行质量评分（1-5分）……")

# 初始化 client（使用主流程中的配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,      # ← 来自 safe_input 第5项
            base_url=model_api      # ← 来自第3项
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

class Score(BaseModel):
    score: int = Field(description="题目质量得分", ge=1, le=5)

# 加载提示词模板
prompt_path = Path("prompts/prompt6.txt")
if not prompt_path.exists():
    print(f"❌ 错误: 评分提示词文件不存在 → {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 构建输入/输出路径
input_file = Path(output_path) / "SFTquestion.json"
output_file = Path(output_path) / "SFTquestionscore.json"

if not input_file.exists():
    print(f"❌ 错误: 题目文件不存在 → {input_file}")
    exit(1)

# 读取题目数据
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        items: List[dict] = json.load(f)
    if not isinstance(items, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取题目文件失败: {e}")
    exit(1)

# 辅助函数：清理 None 值
def clean_null(obj):
    if isinstance(obj, dict):
        return {k: clean_null(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [clean_null(item) for item in obj]
    else:
        return obj

# 遍历每个题目进行评分
total = len(items)
for idx, item in enumerate(items):
    print(f"[{idx+1}/{total}] 正在评分...")

    question = item.get("question", "")
    answer = item.get("answer")
    text = item.get("text", "")
    options = item.get("options")  # 可能是 dict 或 None
    domain_used = domain  # ← 来自 safe_input 第6项

    # 构造 answer 的可读形式（特别处理选择题）
    if options and isinstance(options, dict) and answer is not None:
        options_str = "\n".join([f"{k}: {v}" for k, v in options.items()])
        answer_str = str(answer) if answer is not None else ""
        letters = re.findall(r'[A-Z]', answer_str.upper())
        if not letters:
            full_answer = f"{answer}（无效答案）"
            print(f"  ⚠️ 警告：未识别到有效选项字母，原始答案: {answer}")
        else:
            parts = []
            for letter in letters:
                option_text = options.get(letter, "选项未定义")
                parts.append(f"{letter}（{option_text}）")
            full_answer = "、".join(parts)
    else:
        # 非选择题（填空、判断、简答）
        options_str = ""
        full_answer = str(answer) if answer is not None else ""

    # 格式化 prompt
    try:
        prompt = prompt_template.format(
            domain=domain_used,
            text=text,
            question=question,
            answer=full_answer,
            options=options_str
        )
    except KeyError as e:
        print(f"  ⚠️ Prompt 模板缺少字段 {e}，跳过此题。")
        item["score"] = -1
        continue

    # 调用模型评分
    try:
        result = client.chat.completions.create(
            model=model_name,  # ← 来自 safe_input 第4项
            messages=[{"role": "user", "content": prompt}],
            response_model=Score,
            max_retries=2
        )
        item["score"] = result.score
        print(f"  ✅ 得分: {result.score}")
    except Exception as e:
        print(f"  ❌ 评分失败: {e}")
        item["score"] = -1  # 标记异常

# 清理 None 值并保存
items_clean = clean_null(items)
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(items_clean, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 题目评分完成！共处理 {total} 道题，结果已保存至:\n{output_file}")
except Exception as e:
    print(f"❌ 保存评分结果失败: {e}")
    exit(1)
print("📊 监督微调数据集生成成功，请使用TIGERUI检查 SFTquestionscore.json 后按 Enter 继续。")
input("按 Enter 继续...")

################################################################## 生成偏好优化数据集（PDquestion）
print("正在生成偏好数据集 ……")

# 定义题目结构
class Question(BaseModel):
    question: str = Field(description="基于文本生成的问题内容")
    answer1: str = Field(description="问题对应的答案1")
    answer2: str = Field(description="问题对应的答案2")

# 初始化客户端（使用主流程配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,      # ← 来自 safe_input 第5项
            base_url=model_api      # ← 来自第3项
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

# 路径与参数
input_file = Path(output_path) / "chunksscore.json"
output_file = Path(output_path) / "PDquestion.json"
domain_used = domain  # ← 来自 safe_input 第6项
# ==================== 用户自定义双答案题的字符粒度 ====================
while True:
    char_input = input(
        "\n📝 请输入每道题目基于多少字符生成（默认 200，建议 150~800）："
    ).strip()

    if not char_input:
        char = 200
        print(f"✅ 使用默认值: 每 {char} 字符生成 1 道题目。")
        break

    if char_input.isdigit():
        char = int(char_input)
        if char > 0:
            print(f"✅ 已设置: 每 {char} 字符生成 1 道题目。")
            break
        else:
            print("❌ 字符数必须大于 0，请重新输入。")
    else:
        print("❌ 请输入一个正整数（如 200），或直接按 Enter 使用默认值 200。")
# ===================================================================

# 加载提示词
prompt_path = Path("prompts/prompt7.txt")
if not prompt_path.exists():
    print(f"❌ 提示词文件不存在: {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取输入数据
if not input_file.exists():
    print(f"❌ 输入文件不存在: {input_file}")
    exit(1)

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data: List[dict] = json.load(f)
    if not isinstance(data, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取输入文件失败: {e}")
    exit(1)

all_generated_questions = []

for item in data:
    text = item.get("text", "").strip()
    item_id = item.get("id")
    source_file = item.get("source_file")

    if not text:
        continue

    text_length = len(text)
    num_questions = max(1, math.ceil(text_length / char))  # 至少1题

    print(f"\n--- 处理 ID={item_id} --- 长度: {text_length} 字符, 生成 {num_questions} 道题目")

    try:
        prompt = prompt_template.format(
            number=num_questions,
            domain=domain_used,
            text=text
        )

        result_list: List[Question] = client.chat.completions.create(
            model=model_name,  # ← 来自 safe_input 第4项
            messages=[{"role": "user", "content": prompt}],
            response_model=List[Question],
            temperature=0.0,
            seed=42,
            max_retries=2
        )

        for q_obj in result_list:
            question_data = q_obj.model_dump()
            question_data.update({
                "source_file": source_file,
                "id": item_id,
                "text": text
            })
            all_generated_questions.append(question_data)

        print(f"   ✅ 成功生成 {len(result_list)} 道题目。")

    except Exception as e:
        print(f"   ❌ 处理 ID={item_id} 时出错: {e}")

# 保存结果
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_generated_questions, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 共生成 {len(all_generated_questions)} 道题目，结果已保存至:\n{output_file}")
except Exception as e:
    print(f"❌ 保存结果失败: {e}")
    exit(1)

################################################################## 对偏好优化数据集进行质量评分
print("正在对偏好数据集进行质量评分（1-5分）……")

# 初始化客户端（使用主流程配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,      # ← 来自 safe_input 第5项
            base_url=model_api      # ← 来自第3项
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

class QualityScore(BaseModel):
    score: int = Field(
        description="对整道题目的质量评分",
        ge=1,
        le=5)

# 路径配置
input_file = Path(output_path) / "PDquestion.json"
output_file = Path(output_path) / "PDquestionscore.json"

# 加载提示词模板
prompt_path = Path("prompts/prompt8.txt")
if not prompt_path.exists():
    print(f"❌ 提示词文件不存在: {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取偏好数据
if not input_file.exists():
    print(f"❌ 偏好数据文件不存在: {input_file}")
    exit(1)

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        items: List[dict] = json.load(f)
    if not isinstance(items, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取偏好数据失败: {e}")
    exit(1)

# 辅助函数：清理 None
def clean_null(obj):
    if isinstance(obj, dict):
        return {k: clean_null(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [clean_null(item) for item in obj]
    else:
        return obj

total = len(items)
for idx, item in enumerate(items):
    print(f"[{idx+1}/{total}] 评分中...")

    question = item.get("question", "")
    answer1 = item.get("answer1", "")
    answer2 = item.get("answer2", "")
    text = item.get("text", "")
    domain_used = domain  # ← 来自用户输入

    # 校验必要字段
    if not all([question, answer1, answer2]):
        print(f"  ⚠️ 缺失字段，跳过此条目")
        item["score"] = -1
        continue

    try:
        prompt = prompt_template.format(
            domain=domain_used,
            text=text,
            question=question,
            answer1=answer1,
            answer2=answer2
        )
    except KeyError as e:
        print(f"  ⚠️ Prompt 模板缺少字段 {e}，跳过。")
        item["score"] = -1
        continue

    try:
        result = client.chat.completions.create(
            model=model_name,  # ← 来自 safe_input 第4项
            messages=[{"role": "user", "content": prompt}],
            response_model=QualityScore,
            max_retries=2
        )
        item["score"] = result.score
        print(f"  ✅ 得分: {result.score}")
    except Exception as e:
        print(f"  ❌ 评分失败: {e}")
        item["score"] = -1

# 清理并保存
items_clean = clean_null(items)
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(items_clean, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 偏好数据评分完成！共处理 {total} 条，结果已保存至:\n{output_file}")
except Exception as e:
    print(f"❌ 保存失败: {e}")
    exit(1)

################################################################## 为偏好对生成推荐答案与理由（用于构建 chosen/rejected）
print("正在为偏好数据集生成专家推荐答案及理由……")

# 定义推荐结构
class Recommendation(BaseModel):
    recommendation: str = Field(description="被推荐的答案原文")
    reason: str = Field(description="推荐该答案的理由")

# 初始化客户端（使用主流程配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,      # ← 来自 safe_input 第5项
            base_url=model_api      # ← 来自第3项
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

# 路径配置
input_file = Path(output_path) / "PDquestionscore.json"
output_file = Path(output_path) / "PDquestionrecommendation.json"

# 加载提示词模板
prompt_path = Path("prompts/prompt9.txt")
if not prompt_path.exists():
    print(f"❌ 提示词文件不存在: {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取评分后的偏好数据
if not input_file.exists():
    print(f"❌ 输入文件不存在: {input_file}")
    exit(1)

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        items: List[dict] = json.load(f)
    if not isinstance(items, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取偏好数据失败: {e}")
    exit(1)

total = len(items)
for idx, item in enumerate(items):
    print(f"[{idx+1}/{total}] 生成推荐中...")

    question = item.get("question", "")
    answer1 = item.get("answer1", "")
    answer2 = item.get("answer2", "")
    domain_used = domain  # ← 来自用户输入

    # 跳过缺失字段的条目
    if not all([question, answer1, answer2]):
        print(f"  ⚠️ 缺失必要字段，跳过")
        item["recommendation"] = ""
        item["reason"] = "Missing question or answers"
        continue

    try:
        prompt = prompt_template.format(
            domain=domain_used,
            question=question,
            answer1=answer1,
            answer2=answer2
        )
    except KeyError as e:
        print(f"  ⚠️ Prompt 模板缺少字段 {e}")
        item["recommendation"] = ""
        item["reason"] = f"Prompt formatting error: {e}"
        continue

    try:
        result = client.chat.completions.create(
            model=model_name,  # ← 来自 safe_input 第4项
            messages=[{"role": "user", "content": prompt}],
            response_model=Recommendation,
            max_retries=2
        )

        # 🔍 安全校验：确保 recommendation 是 answer1 或 answer2 的精确匹配
        rec = result.recommendation.strip()
        a1 = answer1.strip()
        a2 = answer2.strip()

        if rec == a1 or rec == a2:
            item["recommendation"] = rec
        else:
            # 如果不匹配，尝试模糊匹配（防止多余空格/标点）
            if re.sub(r'\s+', '', rec) == re.sub(r'\s+', '', a1):
                item["recommendation"] = a1
            elif re.sub(r'\s+', '', rec) == re.sub(r'\s+', '', a2):
                item["recommendation"] = a2
            else:
                # 无法匹配 → 默认选 answer1 并标记异常
                item["recommendation"] = a1
                result.reason += " [⚠️ 推荐答案未严格匹配 answer1/2，已自动修正]"

        item["reason"] = result.reason
        print(f"  ✅ 推荐成功（长度: {len(rec)}）")

    except Exception as e:
        print(f"  ❌ 推荐生成失败: {e}")
        item["recommendation"] = answer1  # fallback
        item["reason"] = f"LLM evaluation error: {str(e)}"

# 保存结果
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 推荐完成！共处理 {total} 条，结果已保存至:\n{output_file}")
except Exception as e:
    print(f"❌ 保存失败: {e}")
    exit(1)

print("📊 偏好数据集生成成功，请使用TIGERUI人工确定 PDquestionrecommendation.json 中偏好答案后按 Enter 继续。")
input("按 Enter 继续进行标签注释...")

################################################################## 对题目进行医学内容类型分类
print("正在对题目进行内容类型分类……")

# 定义内容类型枚举（严格限定输出）
class ContentType(str, Enum):
    content_type1 = "病因病理"
    content_type2 = "临床表现"
    content_type3 = "诊断治疗"
    content_type4 = "文献指南"
    content_type5 = "其他"

class ContentLabel(BaseModel):
    content: ContentType = Field(description="题目所属的医学内容类型")

# 初始化客户端（使用主流程配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,      # ← 来自 safe_input 第5项
            base_url=model_api      # ← 来自第3项
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

# 路径配置
# ==================== 用户选择输入文件 ====================
while True:
    user_input_path = input(
        "\n📁 请输入要进行内容分类的题目文件路径（例如：output/SFTquestionscore.json）："
    ).strip()

    if not user_input_path:
        print("❌ 路径不能为空，请重新输入。")
        continue

    input_file = Path(user_input_path)

    if not input_file.exists():
        print(f"❌ 文件不存在：{input_file.resolve()}")
        retry = input("是否重新输入？(y/n，默认 y)：").strip().lower()
        if retry in ('n', 'no'):
            print("🛑 用户取消操作。")
            exit(0)
        else:
            continue
    else:
        print(f"✅ 将对以下文件进行内容分类：\n{input_file.resolve()}")
        break
# =========================================================
output_file = Path(output_path) / "contentlabel.json"

# 加载提示词模板
prompt_path = Path("prompts/prompt10.txt")
if not prompt_path.exists():
    print(f"❌ 提示词文件不存在: {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取 SFT 题目数据
if not input_file.exists():
    print(f"❌ 输入文件不存在: {input_file}")
    exit(1)

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        items: List[dict] = json.load(f)
    if not isinstance(items, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取 SFT 题目失败: {e}")
    exit(1)

total = len(items)
for idx, item in enumerate(items):
    print(f"[{idx+1}/{total}] 分类中...")

    question = item.get("question", "")
    answer = item.get("answer", "")
    text = item.get("text", "")
    options = item.get("options")  # 可能为 None 或 dict
    domain_used = domain  # ← 来自用户输入

    # 构建带选项的答案展示（用于上下文理解）
    if options and isinstance(options, dict):
        options_str = "\n".join([f"{k}: {v}" for k, v in options.items()])
        options_block = f"选项：\n{options_str}"

        # 解析 answer 中的字母（支持多选如 "AB"）
        answer_str = str(answer).strip().upper()
        letters = re.findall(r'[A-Z]', answer_str)
        if letters:
            resolved_parts = []
            for letter in letters:
                option_text = options.get(letter, "（选项未定义）")
                resolved_parts.append(f"{letter}（{option_text}）")
            full_answer = "、".join(resolved_parts)
        else:
            full_answer = f"{answer}（无法解析选项）"
    else:
        options_block = ""
        full_answer = str(answer) if answer is not None else ""

    try:
        prompt = prompt_template.format(
            domain=domain_used,
            text=text,
            question=question,
            answer=full_answer,
            options=options_block
        )
    except KeyError as e:
        print(f"  ⚠️ Prompt 模板缺少字段 {e}")
        item["content"] = "其他"
        continue

    try:
        result = client.chat.completions.create(
            model=model_name,  # ← 来自 safe_input 第4项
            messages=[{"role": "user", "content": prompt}],
            response_model=ContentLabel,
            max_retries=2
        )
        item["content"] = result.content.value
        print(f"  ✅ 分类结果: {result.content.value}")
    except Exception as e:
        print(f"  ❌ 分类失败: {e}")
        item["content"] = "其他"  # 默认回退

# 保存结果
items = clean_null(items)

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 内容分类完成！共处理 {total} 道题，结果已保存至:\n{output_file}")
except Exception as e:
    print(f"❌ 保存失败: {e}")
    exit(1)

################################################################## 第一轮人体系统注释（基于 contentlabel.json）
print("正在对题目进行人体系统分类（呼吸/心血管/消化等）……")

# ==================== 修复命名冲突 ====================
class MedicalSystem(str, Enum):
    System1 = "呼吸系统"
    System2 = "心血管系统"
    System3 = "消化系统"
    System4 = "泌尿系统"
    System5 = "血液系统"
    System6 = "内分泌系统"
    System7 = "风湿性疾病"
    System8 = "运动系统"
    System9 = "传染病、性病"
    System10 = "产科学"
    System11 = "妇科学"
    System12 = "儿科疾病"
    System13 = "神经内外科疾病"
    System14 = "精神病"
    System15 = "其他"

class SystemLabel(BaseModel):
    system: MedicalSystem = Field(description="题目所属的人体系统类别")
# ===================================================

# 初始化客户端（使用主流程配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,
            base_url=model_api
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

# 固定输入输出路径（基于 output_path）
input_file = Path(output_path) / "contentlabel.json"
output_file = Path(output_path) / "systemlabel.json"

# 检查输入文件是否存在
if not input_file.exists():
    print(f"❌ 输入文件不存在: {input_file}")
    exit(1)

# 加载提示词模板
prompt_path = Path("prompts/prompt11.txt")
if not prompt_path.exists():
    print(f"❌ 提示词文件缺失: {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取 contentlabel 数据
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        contentlabel: List[dict] = json.load(f)
    if not isinstance(contentlabel, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取 contentlabel.json 失败: {e}")
    exit(1)

# 处理每道题
systemlabel = []
total = len(contentlabel)

for idx, entry in enumerate(contentlabel):
    print(f"[{idx+1}/{total}] 标注人体系统中...")

    try:
        id_val = entry.get("id", idx)
        question = entry.get("question", "")
        options = entry.get("options")
        answer = entry.get("answer", "")
        content = entry.get("content", "")

        # 构造选项字符串
        if options and isinstance(options, dict):
            options_str = "\n".join([f"{k}. {v}" for k, v in options.items() if v is not None])
        else:
            options_str = "（本题无选项，为非选择题）"

        # 填充提示词
        prompt = prompt_template.format(
            question=question,
            options=options_str,
            answer=answer
        )

        # 调用模型
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_model=SystemLabel,
            max_retries=2
        )

        result = {
            "id": id_val,
            "question": question,
            "options": options,
            "answer": answer,
            "content": content,
            "system": response.system.value
        }
        systemlabel.append(result)
        print(f"  ✅ 系统: {response.system.value}")

    except Exception as e:
        print(f"  ❌ 题目 {id_val} 处理失败: {e}")
        systemlabel.append({
            **entry,
            "system": "其他"
        })

# 清洗 None 值
def clean_null(obj):
    if isinstance(obj, dict):
        return {k: clean_null(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [clean_null(item) for item in obj]
    else:
        return obj

systemlabel_clean = clean_null(systemlabel)

# 保存结果
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(systemlabel_clean, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 人体系统标注完成！结果已保存至:\n{output_file}")
except Exception as e:
    print(f"❌ 保存 systemlabel.json 失败: {e}")
    exit(1)


################################################################## 疾病注释（基于 systemlabel.json）
print("正在对题目进行疾病注释（如肺炎、心梗、糖尿病等）……")

# 初始化客户端（使用主流程配置）
try:
    client = instructor.from_openai(
        OpenAI(
            api_key=model_key,
            base_url=model_api
        ),
        mode=instructor.Mode.JSON
    )
except Exception as e:
    print(f"❌ 初始化 OpenAI 客户端失败: {e}")
    exit(1)

# 固定输入输出路径（基于 output_path）
input_file = Path(output_path) / "systemlabel.json"
output_file = Path(output_path) / "diseaselabel.json"

# 检查输入文件是否存在
if not input_file.exists():
    print(f"❌ 输入文件不存在: {input_file}")
    exit(1)

# 加载提示词模板
prompt_path = Path("prompts/prompt12.txt")
if not prompt_path.exists():
    print(f"❌ 提示词文件缺失: {prompt_path.resolve()}")
    exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# 读取 systemlabel 数据
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        systemlabel: List[dict] = json.load(f)
    if not isinstance(systemlabel, list):
        raise ValueError("输入文件不是 JSON 数组")
except Exception as e:
    print(f"❌ 读取 systemlabel.json 失败: {e}")
    exit(1)

# 处理每道题
diseaselabel = []
total = len(systemlabel)

for idx, entry in enumerate(systemlabel):
    id_val = entry.get("id", idx)
    question = entry.get("question", "")
    options = entry.get("options")
    answer = entry.get("answer", "")
    content = entry.get("content", "")
    system = entry.get("system", "其他")

    print(f"[{idx+1}/{total}] 标注疾病中... ({system})")

    try:
        # ==================== 动态加载对应系统的 Disease 枚举 ====================
        disease_dir = "disease"
        file_path = os.path.join(disease_dir, f"{system}.py")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"未找到系统 '{system}' 对应的枚举文件: {file_path}")

        spec = importlib.util.spec_from_file_location(f"{system}_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, 'Disease'):
            raise AttributeError(f"文件 {file_path} 中未定义 'Disease' 类")

        DiseaseEnum = module.Disease
        # ===============================================================

        # 构造选项字符串
        if options and isinstance(options, dict):
            options_str = "\n".join([f"{k}. {v}" for k, v in options.items() if v is not None])
        else:
            options_str = "（本题无选项，为非选择题）"

        # 构造疾病候选列表
        disease_list_str = "\n".join([f"- {item.value}" for item in DiseaseEnum])

        # 填充提示词
        prompt = prompt_template.format(
            disease_list=disease_list_str,
            question=question,
            options=options_str,
            answer=answer
        )

        # 动态创建 Pydantic 模型（绑定当前 DiseaseEnum）
        class DiseaseAnnotation(BaseModel):
            disease: DiseaseEnum = Field(..., description="题目所属疾病条目")

        # 调用模型
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_model=DiseaseAnnotation,
            max_retries=2
        )

        result = {
            "id": id_val,
            "question": question,
            "options": options,
            "answer": answer,
            "content": content,
            "system": system,
            "disease": response.disease.value
        }
        diseaselabel.append(result)
        print(f"  ✅ 疾病: {response.disease.value}")

    except Exception as e:
        print(f"  ❌ 题目 {id_val} 处理失败: {e}")
        diseaselabel.append({
            **entry,
            "disease": None  # 后续会被 clean_null 移除或保留为 null（根据需求）
        })

# 清洗 None 值
def clean_null(obj):
    if isinstance(obj, dict):
        return {k: clean_null(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [clean_null(item) for item in obj]
    else:
        return obj

diseaselabel_clean = clean_null(diseaselabel)

# 保存结果
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(diseaselabel_clean, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 疾病细粒度标注完成！结果已保存至:\n{output_file}")
except Exception as e:
    print(f"❌ 保存 diseaselabel.json 失败: {e}")
    exit(1)

################################### 结束

print("所有任务完成！请使用TIGERUI对标注结果进行检查和完善。")
input("🔚 所有流程已完成！按 Enter 键退出程序(退出后TIGER UI将终止访问)……")
print("\n欢迎您下次使用Strongconstruct")
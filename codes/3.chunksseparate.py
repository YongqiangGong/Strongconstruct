import json
import os
import sys
from pathlib import Path
from chonkie import SlumberChunker
from chonkie.genie import OpenAIGenie
print("开始进行文本分割，请稍后……")

# 构建路径
input_dir = Path('demo/output/md') 
output_dir = Path('demo/output/chunks') 
output_dir.mkdir(parents=True, exist_ok=True)

model_api = "#####"   # ← 替换为你的值
model_name = "#####"            # ← 替换为你的值
model_key = "#####"              # ← 替换为你的值

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
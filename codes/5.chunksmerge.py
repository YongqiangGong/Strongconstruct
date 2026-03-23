# 导入
import json
import os
import sys
from pathlib import Path

print("开始合并所有分块文件为 chunksmerge.json，请稍后……")

# 构建路径
input_dir = Path("demo/output/chunks") 
output_dir = Path('demo/output')  # 合并文件放在 output_path 根目录下
merged_file = Path("demo/output/chunksmerge.json") 

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
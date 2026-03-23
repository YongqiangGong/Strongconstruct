import json

# 输入和输出文件路径
input_file = 'demo/output/chunksmerge.json'
output_file = 'demo/output/chunksnumber.json'

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

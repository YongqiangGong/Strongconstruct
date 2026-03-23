import json
from pathlib import Path
from chonkie import SlumberChunker
from chonkie.genie import OpenAIGenie
import argparse
import sys

def process_directory(input_dir: str, output_dir: str = None):
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)

    genie = OpenAIGenie(
        model="#####",
        base_url="#####",
        api_key="123",
    )

    chunker = SlumberChunker(
        genie=genie,
        tokenizer="character",
        chunk_size=5000,
        candidate_size=5000,
        min_characters_per_chunk=25,
        verbose=True
    )

    # 遍历所有 .txt 文件
    for txt_file in input_path.glob("*.txt"):
        print(f"Processing: {txt_file.name}")
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = chunker.chunk(text)

            # 构建输出路径：xxx.txt → xxx.json
            json_file = output_path / f"{txt_file.stem}.json"

            # 收集所有 chunk 为 list of dict
            records = []
            for chunk in chunks:
                record = {
                    "text": chunk.text if hasattr(chunk, 'text') else str(chunk),
                }
                records.append(record)

            # 一次性写入整个 JSON 数组（带缩进，便于阅读）
            with open(json_file, "w", encoding="utf-8") as out_f:
                json.dump(records, out_f, ensure_ascii=False, indent=2)

            print(f"Saved: {json_file}")

        except Exception as e:
            print(f"Error processing {txt_file}: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chunk all .txt files into .json arrays using SlumberChunker.")
    parser.add_argument("input_dir", help="Directory containing .txt files")
    parser.add_argument("output_dir", nargs='?', default=None, help="Output directory for .json files (optional)")
    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir)
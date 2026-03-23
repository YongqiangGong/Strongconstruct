from pathlib import Path
import shutil
import re
import os



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
source_root = Path('mineru')
target_dir = Path('demo/output/md')

print("\n📂 正在从 mineru 结果中提取 Markdown 文件……")
if not source_root.exists():
    print(f"❌ 错误: 源目录不存在: {source_root}")
else:
    copy_all_markdown_files(source_root, target_dir)
    print(f"\n🎉 所有 Markdown 文件已保存至: {target_dir}")
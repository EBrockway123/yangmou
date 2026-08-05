# -*- coding: utf-8 -*-
"""v2 提取全卷元注: 把每章末尾的【伏笔】/【钩子】/【附注】块移到独立元数据文件

这是结构性修复 - 元注本应在独立文件, 不应混在正文末尾污染文笔.
"""
import re
import os
import shutil

DIRS = ['03_第一幕_入局', '04_第二幕_小试牛刀', '05_第三幕_连环阳谋']
OUT_DIR = '02_审查与修复/元注备份_v2'


def count_dashes(text):
    zh = len(re.findall(r'[\u4e00-\u9fff]', text))
    return zh, text.count('——')


def find_meta_start(lines):
    """找元注起始行 (伏笔/钩子/附注块)"""
    for i, line in enumerate(lines):
        s = line.strip()
        # 元注起始标记
        if re.match(r'^>\s*\*\s*【', s) or re.match(r'^>\s*【', s):
            return i
        # 也可能是普通段落里的 "**【伏笔】**" 单独行
        if re.match(r'^>\s*\*?\*?【伏笔】', s) or re.match(r'^>\s*\*?\*?【钩子】', s):
            return i
    return -1


def extract_meta(text):
    """提取末尾的元注区"""
    lines = text.split('\n')
    meta_start = find_meta_start(lines)
    if meta_start < 0:
        return text, None, -1

    # 找元注结束 (下一个"---"或文末)
    meta_end = len(lines)
    for j in range(meta_start, len(lines)):
        s = lines[j].strip()
        if s == '---' and j > meta_start:
            meta_end = j
            break

    # 正文 = 0..meta_start
    body_lines = lines[:meta_start]
    # 删除正文末尾的空行
    while body_lines and body_lines[-1].strip() == '':
        body_lines.pop()
    body = '\n'.join(body_lines) + '\n'

    # 元注
    meta_lines = lines[meta_start:meta_end]
    meta = '\n'.join(meta_lines)

    return body, meta, meta_start


def process_chapter(path, out_dir):
    basename = os.path.basename(path)
    name_no_ext = os.path.basename(path).replace('.md', '')

    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    body, meta, meta_start = extract_meta(text)
    if meta is None:
        return None

    # 写正文
    with open(path, 'w', encoding='utf-8') as f:
        f.write(body)

    # 写元注
    out_path = os.path.join(out_dir, name_no_ext + '_元注.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"# {name_no_ext} · 元注\n\n")
        f.write(f"> 提取自: `{path}`\n")
        f.write(f"> 提取时间: 2026-08-04\n\n")
        f.write("---\n\n")
        f.write(meta)
        f.write('\n')

    return {
        'path': path,
        'meta_chars': len(re.findall(r'[\u4e00-\u9fff]', meta)),
        'body_chars': len(re.findall(r'[\u4e00-\u9fff]', body)),
    }


def find_all_chapters():
    files = []
    for d in DIRS:
        for f in sorted(os.listdir(d)):
            if f.endswith('.md') and f[0:2].isdigit() and not f.startswith('00'):
                files.append(os.path.join(d, f))
    return files


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)

    # 备份所有元注
    print("=== 提取元注 ===")
    chapters = find_all_chapters()
    extracted = 0
    skipped = 0
    for path in chapters:
        r = process_chapter(path, OUT_DIR)
        if r is None:
            skipped += 1
        else:
            extracted += 1
            if extracted <= 5:
                print(f"  ✓ {os.path.basename(path)}: 正文 {r['body_chars']} 字, 元注 {r['meta_chars']} 字")

    print(f"\n  总计: 提取 {extracted}, 跳过 {skipped} (无元注)")
    print(f"  输出目录: {OUT_DIR}/")

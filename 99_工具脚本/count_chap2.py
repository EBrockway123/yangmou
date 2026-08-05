# -*- coding: utf-8 -*-
import re

with open(r'F:\tess小说\03_第一幕_入局\02_第02章_策论.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. 全文(标题、附注、钩子、伏笔)总中文字数
total_zh = len(re.findall(r'[\u4e00-\u9fff]', text))
print(f"全文(含附注)中文: {total_zh}")

# 2. 仅正文(去掉 > 引注、* 伏笔、--- 分隔、空行)
# 按行处理
lines = text.splitlines()
narrative_lines = []
in_note = False
for line in lines:
    s = line.strip()
    if s.startswith('>') or s.startswith('*') or s == '' or s == '---':
        continue
    narrative_lines.append(line)

narrative_text = '\n'.join(narrative_lines)
narrative_zh = len(re.findall(r'[\u4e00-\u9fff]', narrative_text))
print(f"正文(不含附注)中文: {narrative_zh}")

# 3. 显示正文的每一段
print("\n--- 正文段落 ---")
for i, line in enumerate(narrative_lines):
    if line.strip():
        print(f"{i+1}: {line}")

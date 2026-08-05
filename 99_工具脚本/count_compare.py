# -*- coding: utf-8 -*-
import re

for chap, fname in [('第1章', r'F:\tess小说\03_第一幕_入局\01_第01章_匿名信.md'),
                    ('第2章', r'F:\tess小说\03_第一幕_入局\02_第02章_策论.md')]:
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()
    # 仅正文
    lines = text.splitlines()
    narrative_lines = [l for l in lines if l.strip() and not l.strip().startswith('>') and not l.strip().startswith('*') and l.strip() != '---' and not l.strip().startswith('#')]
    narrative_text = '\n'.join(narrative_lines)
    narrative_zh = len(re.findall(r'[\u4e00-\u9fff]', narrative_text))
    total_zh = len(re.findall(r'[\u4e00-\u9fff]', text))
    print(f"{chap}: 正文={narrative_zh} 全文(含附注)={total_zh}")

# -*- coding: utf-8 -*-
"""
v2 全卷统计脚本
- 字数
- 破折号数量 + 密度
- 11 个常见重复措辞
- 阳谋直提
- 短句连续最长
"""
import re
import os
import json

# 章集合
chapters = []

# 第一幕
for i in range(1, 10):
    if i == 1:
        fname = f'03_第一幕_入局/01_第{i:02d}章_匿名信.md'
    else:
        fname = f'03_第一幕_入局/{i:02d}_第{i:02d}章_'
        # 不同章名,需要查表
    # 实际找文件
    for f in os.listdir('03_第一幕_入局'):
        if f.startswith(f'{i:02d}_第{i:02d}章') and f.endswith('.md'):
            fname = f'03_第一幕_入局/{f}'
            break
    chapters.append((f'第{i}章', fname))

# 第二幕
for i in range(10, 28):
    for f in os.listdir('04_第二幕_小试牛刀'):
        if f.startswith(f'{i}_第{i}章') and f.endswith('.md'):
            fname = f'04_第二幕_小试牛刀/{f}'
            break
    chapters.append((f'第{i}章', fname))

# 第三幕
for i in range(28, 59):
    for f in os.listdir('05_第三幕_连环阳谋'):
        if f.startswith(f'{i}_第{i}章') and f.endswith('.md'):
            fname = f'05_第三幕_连环阳谋/{f}'
            break
    chapters.append((f'第{i}章', fname))

# 重复措辞清单
REPEAT_LIST = [
    '端茶手停一拍', '端起案边凉茶', '指节发白', '坐了一会儿', '站了一会儿', '看了一会儿',
    '他想起', '良久', '他没说话', '他沉默', '沈彦沉默',
    '眸光微动', '眼神一凛', '眼底不笑', '微微颔首', '淡淡一笑', '轻轻颔首',
    '他没让自己多想', '是。', '良久之后',
    '接成线', '串了起来', '手按在',
    '吃了',
]

def analyze(text):
    # 字数(中文)
    zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 破折号
    dashes = text.count('——')
    dash_density = dashes / zh_chars * 100 if zh_chars > 0 else 0
    # 阳谋直提
    yang_count = len(re.findall(r'阳谋', text))
    # 重复措辞
    repeats = {}
    for r in REPEAT_LIST:
        c = text.count(r)
        if c > 0:
            repeats[r] = c
    # 短句连续(句号)
    # 找 4+ 个连续短句
    short_seq = 0
    max_short = 0
    sentences = re.split(r'[。\n]', text)
    cur_run = 0
    for s in sentences:
        s = s.strip()
        if 1 < len(s) < 15:  # 短句
            cur_run += 1
            max_short = max(max_short, cur_run)
        else:
            cur_run = 0
    return {
        'zh_chars': zh_chars,
        'dashes': dashes,
        'dash_density': round(dash_density, 2),
        'yang_count': yang_count,
        'repeats': repeats,
        'max_short': max_short,
    }

# 跑全卷
results = []
for label, fname in chapters:
    if not os.path.exists(fname):
        print(f"❌ MISSING: {fname}")
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()
    stats = analyze(text)
    stats['chap'] = label
    stats['fname'] = fname
    results.append(stats)

# 输出 JSON
with open('v2_统计报告.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 输出表格
print(f"\n{'章节':<8}{'字数':<8}{'破折号':<8}{'密度%':<8}{'阳谋':<6}{'短句最':<6}{'主要重复'}")
print("-" * 80)
total_dashes = 0
total_chars = 0
for r in results:
    top_repeat = ', '.join([f"{k}×{v}" for k, v in sorted(r['repeats'].items(), key=lambda x: -x[1])[:3]])
    print(f"{r['chap']:<8}{r['zh_chars']:<8}{r['dashes']:<8}{r['dash_density']:<8}{r['yang_count']:<6}{r['max_short']:<6}{top_repeat}")
    total_dashes += r['dashes']
    total_chars += r['zh_chars']

print("-" * 80)
print(f"{'合计':<8}{total_chars:<8}{total_dashes:<8}{round(total_dashes/total_chars*100, 2):<8}")

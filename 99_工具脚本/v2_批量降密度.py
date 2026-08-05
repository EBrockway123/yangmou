# -*- coding: utf-8 -*-
"""v2 批量降密度: 把破折号密度 > 2% 的章节降到 ≤ 1%
- 智能语义化替换, 不暴力删除
"""
import re
import os
import glob

# 三个目录
DIRS = ['03_第一幕_入局', '04_第二幕_小试牛刀', '05_第三幕_连环阳谋']


def count_dashes(text):
    zh = len(re.findall(r'[\u4e00-\u9fff]', text))
    dashes = text.count('——')
    return zh, dashes


def reduce_dashes_smart(text):
    original = text
    changes = []

    # 模式 1: 段首 "\n——" → "\n" (引出型)
    n = text.count('\n——')
    if n:
        text = re.sub(r'\n——', '\n', text)
        changes.append(('段首破折号', n))

    # 模式 2: 句末 "——\n" → "\n"
    n = text.count('——\n')
    if n:
        text = re.sub(r'——\n', '\n', text)
        changes.append(('句末破折号', n))

    # 模式 3: "。——" → "。 " (句号+破折号, 去掉破折号)
    n = text.count('。——')
    if n:
        text = re.sub(r'。——', '。 ', text)
        changes.append(('句号+破折号', n))

    # 模式 4: "，——" → "，" (逗号+破折号)
    n = text.count('，——')
    if n:
        text = re.sub(r'，——', '，', text)
        changes.append(('逗号+破折号', n))

    # 模式 5: "；——" → "；"
    n = text.count('；——')
    if n:
        text = re.sub(r'；——', '；', text)
        changes.append(('分号+破折号', n))

    # 模式 6: 单独行只有 "——" → 删
    n = len(re.findall(r'\n——\n', text))
    if n:
        text = re.sub(r'\n——\n', '\n', text)
        changes.append(('独立破折号行', n))

    return text, changes


def process_chapter(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    zh_before, d_before = count_dashes(text)
    if d_before == 0:
        return None

    new_text, changes = reduce_dashes_smart(text)
    if new_text == text:
        return {'path': path, 'no_change': True, 'd_before': d_before, 'zh_before': zh_before}

    zh_after, d_after = count_dashes(new_text)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    return {
        'path': path,
        'zh_before': zh_before,
        'd_before': d_before,
        'density_before': round(d_before/zh_before*100, 2) if zh_before else 0,
        'zh_after': zh_after,
        'd_after': d_after,
        'density_after': round(d_after/zh_after*100, 2) if zh_after else 0,
        'changes': changes,
    }


def find_all_chapters():
    files = []
    for d in DIRS:
        for f in sorted(os.listdir(d)):
            if f.endswith('.md') and f[0:2].isdigit() and not f.startswith('00'):
                files.append(os.path.join(d, f))
    return files


if __name__ == '__main__':
    # 找所有 > 2% 的章节
    all_chapters = find_all_chapters()
    targets = []
    for p in all_chapters:
        with open(p, 'r', encoding='utf-8') as f:
            text = f.read()
        zh, d = count_dashes(text)
        if zh > 0 and d / zh * 100 > 2.0:
            targets.append((p, zh, d, round(d/zh*100, 2)))

    print(f"待处理章节: {len(targets)}")
    print(f"{'章节':<70}{'前':<6}{'后':<6}{'密度前':<8}{'密度后':<8}")
    print('-' * 110)
    for path, zh, d, density in targets:
        r = process_chapter(path)
        if not r or r.get('no_change'):
            continue
        name = os.path.basename(path)[:65]
        print(f"{name:<70}{r['d_before']:<6}{r['d_after']:<6}{r['density_before']:<8}{r['density_after']:<8}")

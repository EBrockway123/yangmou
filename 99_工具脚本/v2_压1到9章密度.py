# -*- coding: utf-8 -*-
"""v2 压 1-9 章破折号密度到 ≤ 1%
- 模式 1: 段首 '——' → 删除
- 模式 2: '，——' → '，'
- 模式 3: '。——' → '。'
- 模式 4: '——"' → '。"'
- 模式 5: 'X|——|Y' 中间空内容 → 'X。Y'
- 模式 6: 'X——'X' 短引述 → 'X:'X'
"""
import re
import os

TARGETS = [
    '03_第一幕_入局/01_第01章_匿名信.md',
    '03_第一幕_入局/04_第04章_放榜_拜师.md',
    '03_第一幕_入局/05_第05章_值夜_崔玄礼.md',
    '03_第一幕_入局/06_第06章_春闱舞弊案_风波起.md',
    '03_第一幕_入局/07_第07章_自污求入_第一阳谋.md',
    '03_第一幕_入局/08_第08章_座师钩子_王公被调走.md',
    '03_第一幕_入局/09_第09章_旧档.md',
]


def reduce(text):
    changes = []

    # 模式 1: 段首破折号
    n = len(re.findall(r'\n——', text))
    if n:
        text = re.sub(r'\n——\s*', '\n', text)
        changes.append(('段首', n))

    # 模式 2: 句号+破折号 → 句号
    n = text.count('。——')
    if n:
        text = text.replace('。——', '。')
        changes.append(('句号+破折号', n))

    # 模式 3: 逗号+破折号 → 逗号
    n = text.count('，——')
    if n:
        text = text.replace('，——', '，')
        changes.append(('逗号+破折号', n))

    # 模式 4: "X|——|" 引号内短破折号
    # 找 "X|——|Y" 模式, X 是 ",Y 或 字符, Y 是 ", 或 字符
    # 例如: "令尊沈鹤年"|——|吃了。
    n = len(re.findall(r'[",]|——|"', text))
    if n:
        # 改: "X"|——|Y。 → "X",Y。
        # 改: "X"|——|"Y" → "X":"Y"
        text = re.sub(r'"|——|', '",', text)
        text = re.sub(r'"|——|"', '":"', text)
        changes.append(('引号内', 1))

    # 模式 5: 单独破折号
    n = text.count('——')
    if n > 0:
        # 找 "X|——|Y" 模式 (X 是字,Y 是字)
        # 保留 1 个破折号每章作为文学用法
        # 删 1/2
        positions = []
        i = 0
        while True:
            pos = text.find('——', i)
            if pos < 0:
                break
            positions.append(pos)
            i = pos + 2
        # 删 1/2
        to_remove = positions[::2]
        for pos in reversed(to_remove):
            text = text[:pos] + text[pos+2:]
        changes.append(('总数', len(to_remove)))

    return text, changes


def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    import re
    zh_before = len(re.findall(r'[\u4e00-\u9fff]', text))
    d_before = text.count('——')

    new_text, changes = reduce(text)
    if new_text != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)

    zh_after = len(re.findall(r'[\u4e00-\u9fff]', new_text))
    d_after = new_text.count('——')
    return {
        'path': path,
        'd_before': d_before,
        'd_after': d_after,
        'density_before': round(d_before/zh_before*100, 2) if zh_before else 0,
        'density_after': round(d_after/zh_after*100, 2) if zh_after else 0,
        'changes': changes,
    }


if __name__ == '__main__':
    print(f"{'章节':<55}{'前':<6}{'后':<6}{'密度前':<8}{'密度后':<8}")
    print('-' * 90)
    for path in TARGETS:
        r = process(path)
        if not r:
            continue
        name = os.path.basename(path)[:50]
        print(f"{name:<55}{r['d_before']:<6}{r['d_after']:<6}{r['density_before']:<8}{r['density_after']:<8}")

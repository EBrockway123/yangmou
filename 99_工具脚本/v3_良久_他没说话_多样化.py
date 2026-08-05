# -*- coding: utf-8 -*-
"""v3 多样化 '良久' 和 '他没说话'"""
import re
import os

DIRS = ['03_第一幕_入局', '04_第二幕_小试牛刀', '05_第三幕_连环阳谋']

LIANGHAO_VARIANTS = [
    '过了半晌', '他回过神', '他缓过神', '半晌之后', '许久', '他回过神来',
    '过了好一阵', '他终于回神', '过了好一会儿', '许久之后', '他才回神',
    '过了片刻', '他缓过一口气', '他怔了一怔',
]

TAIMEI_VARIANTS = [
    '沈彦没应', '沈彦没接话', '沈彦垂下眼', '沈彦点了点头', '沈彦没应声',
    '沈彦没开口', '沈彦把话咽了回去', '沈彦看着他',
    '沈彦只点了点头', '沈彦静了一下', '沈彦没出声',
]


def process_chapter(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    changes = {}

    # 良久 (替换为"过了半晌"等)
    if '良久' in text:
        # 找位置
        positions = []
        i = 0
        while True:
            pos = text.find('良久', i)
            if pos < 0:
                break
            positions.append(pos)
            i = pos + 2
        n = len(positions)
        # round-robin
        for idx, pos in enumerate(positions):
            variant = LIANGHAO_VARIANTS[idx % len(LIANGHAO_VARIANTS)]
            # 检查上下文, 选择合适 variant
            before = text[max(0,pos-15):pos]
            if '之后' in text[pos:pos+10]:
                variant = '许久之后'
            text = text[:pos] + variant + text[pos+2:]
        changes['良久'] = n

    # 他没说话 (多样化)
    if '他没说话' in text:
        positions = []
        i = 0
        while True:
            pos = text.find('他没说话', i)
            if pos < 0:
                break
            positions.append(pos)
            i = pos + 4
        n = len(positions)
        for idx, pos in enumerate(positions):
            variant = TAIMEI_VARIANTS[idx % len(TAIMEI_VARIANTS)]
            text = text[:pos] + variant + text[pos+4:]
        changes['他没说话'] = n

    if changes:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    return changes


def find_all_chapters():
    files = []
    for d in DIRS:
        for f in sorted(os.listdir(d)):
            if f.endswith('.md') and f[0:2].isdigit() and not f.startswith('00'):
                files.append(os.path.join(d, f))
    return files


if __name__ == '__main__':
    chapters = find_all_chapters()
    total = {}
    for path in chapters:
        c = process_chapter(path)
        if c:
            for k, v in c.items():
                total[k] = total.get(k, 0) + v
                name = os.path.basename(path)[:30]
                print(f'  {name}: {k} × {v}')
    print(f'\n总计: {total}')

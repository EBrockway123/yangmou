# -*- coding: utf-8 -*-
"""v2 批量替换重复措辞 (温和替换, 不破坏情感)"""
import re
import os
import random

DIRS = ['03_第一幕_入局', '04_第二幕_小试牛刀', '05_第三幕_连环阳谋']


def replace_repeats(text, path):
    """对每章用 round-robin 替换, 不全章同替换"""
    changes = []
    new_text = text

    # 1. 端茶手停一拍 → 上下文相关替换
    if '端茶手停一拍' in new_text:
        # 找上下文
        patterns = [
            ('端茶手停一拍,看', '看'),
            ('端茶手停一拍,听', '听'),
            ('端茶手停一拍,等', '等'),
            ('端茶手停一拍', '手在杯边顿了一下'),
        ]
        for old, new in patterns:
            n = new_text.count(old)
            if n > 0:
                new_text = new_text.replace(old, new)
                changes.append((old, n))

    # 2. 他想起 → 多样化 (按出现顺序轮换)
    variants_xiangqi = [
        '他忆起', '他回想起', '他心头一动', '眼前闪过',
        '他忽然想起', '他记起', '他暗自想', '他心里过了一遍',
    ]
    # 注意: '眼前闪过' 后通常跟'X' 不同于 '他想起X' 的句式, 需要谨慎
    safe_variants = [
        '他忆起', '他回想起', '他记起', '他心头一动', '他心里一动', '他暗自想起',
        '他忽然忆起', '那一瞬,他记起', '他心头闪过', '他回过神,忆起',
        '他记起', '他心头一紧', '他暗自盘算', '他心里一过',
    ]

    count = new_text.count('他想起')
    if count > 0:
        # 找所有位置
        positions = []
        i = 0
        while True:
            pos = new_text.find('他想起', i)
            if pos < 0:
                break
            positions.append(pos)
            i = pos + 3
        # round-robin 替换
        for idx, pos in enumerate(positions):
            variant = safe_variants[idx % len(safe_variants)]
            new_text = new_text[:pos] + variant + new_text[pos+3:]
        changes.append(('他想起', count))

    # 3. 沈彦沉默 → 多样化
    variants_chenmo = [
        '沈彦没接话', '沈彦没应', '沈彦点了点头', '沈彦没开口',
        '沈彦看着他', '沈彦没应声', '沈彦把话咽了回去', '沈彦垂下眼',
    ]
    count = new_text.count('沈彦沉默')
    if count > 0:
        positions = []
        i = 0
        while True:
            pos = new_text.find('沈彦沉默', i)
            if pos < 0:
                break
            positions.append(pos)
            i = pos + 4
        for idx, pos in enumerate(positions):
            variant = variants_chenmo[idx % len(variants_chenmo)]
            new_text = new_text[:pos] + variant + new_text[pos+4:]
        changes.append(('沈彦沉默', count))

    # 4. 是。 (对话收尾) → 上下文决定
    # 不能一刀切, 只在密集出现时替换
    count_is = new_text.count('是。')
    if count_is > 5:  # 只处理高频章节
        # 找 "X说:..." 的对话模式, 后面接 "是。"
        # 直接把一部分 "是。" 替换为 "嗯。" 或 "属下遵命。"
        # 找出所有位置
        positions = []
        i = 0
        while True:
            pos = new_text.find('是。', i)
            if pos < 0:
                break
            positions.append(pos)
            i = pos + 2
        # 替换一半 (每隔一个)
        # 注意: 必须从后往前替换以免位置漂移
        new_positions = positions[::2]  # 替换奇数位
        for pos in reversed(new_positions):
            # 检查是不是对话中的 "是。"
            before = new_text[max(0, pos-30):pos]
            # 上下文含"问"或"道"时, 替换
            if any(kw in before for kw in ['问', '道', '说', '话']):
                # 替换
                # 决定替换为 "嗯。" "属下明白。" "是,大人。" 等
                if '属下' in before or '臣' in before:
                    new_text = new_text[:pos] + '臣明白。' + new_text[pos+2:]
                else:
                    new_text = new_text[:pos] + '嗯。' + new_text[pos+2:]
        changes.append(('是。', count_is))

    # 5. 指节发白 → 多样化
    if new_text.count('指节发白') > 1:
        new_text = new_text.replace('指节发白', '指节攥白', 1)
        if new_text.count('指节发白') > 0:
            new_text = new_text.replace('指节发白', '指节泛青')
        changes.append(('指节发白', 2))

    return new_text, changes


def process_chapter(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    new_text, changes = replace_repeats(text, path)
    if new_text != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
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
    total_changes = {}
    for path in chapters:
        changes = process_chapter(path)
        for word, count in changes:
            total_changes[word] = total_changes.get(word, 0) + count
            name = os.path.basename(path)[:30]
            print(f'  {name}: {word} × {count}')

    print(f'\n=== 总替换 ===')
    for word, count in sorted(total_changes.items(), key=lambda x: -x[1]):
        print(f'  {word}: {count} 次')

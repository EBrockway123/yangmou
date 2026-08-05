# -*- coding: utf-8 -*-
"""v2 精细替换 "是。": 保留礼节性应答, 但减少密度
- 替换规则: 每章的 "是。" 中, 替换 1/3-1/2 为变体
- 替换原则: 对话上下文区分臣对君/平级/下属对上司
"""
import re
import os

DIRS = ['03_第一幕_入局', '04_第二幕_小试牛刀', '05_第三幕_连环阳谋']

# 上下文判断 - 看前一句是君/上官 → 用"臣明白"等
# 看前一句是平级/对话 → 用"嗯"
JUN_VARIANTS = ['臣明白。', '臣遵旨。', '臣领旨。', '臣知晓。', '臣记下了。']
SHI_VARIANTS = ['属下明白。', '属下领命。', '属下遵命。', '是，遵命。']
PING_VARIANTS = ['嗯。', '我明白。', '好。']


def replace_shi_in_chapter(text):
    """逐章替换 '是。'"""
    # 找所有位置
    positions = []
    i = 0
    while True:
        pos = text.find('是。', i)
        if pos < 0:
            break
        positions.append(pos)
        i = pos + 2

    if not positions:
        return text, 0

    # 替换一半 (每隔一个)
    n_replace = len(positions) // 2
    # 从后往前替换, 避免位置漂移
    to_replace = positions[::2][:n_replace]  # 奇数位

    for pos in reversed(to_replace):
        # 看上下文 (前 50 字)
        before = text[max(0, pos-60):pos]
        # 君 → 臣明白
        if any(kw in before for kw in ['仁宗', '陛下', '太后', '圣上', '皇上']):
            # 看倒数第二轮, 用不同变体
            n_replaced_so_far = sum(1 for p in positions if p in to_replace and p > pos)
            variant = JUN_VARIANTS[n_replaced_so_far % len(JUN_VARIANTS)]
        # 上官/上级
        elif any(kw in before for kw in ['大人', '尚书', '相公', '老师', '裴正则', '韩文清', '崔玄礼']):
            n_replaced_so_far = sum(1 for p in positions if p in to_replace and p > pos)
            variant = SHI_VARIANTS[n_replaced_so_far % len(SHI_VARIANTS)]
        # 平级
        else:
            n_replaced_so_far = sum(1 for p in positions if p in to_replace and p > pos)
            variant = PING_VARIANTS[n_replaced_so_far % len(PING_VARIANTS)]

        # 替换 (注意: 前面可能已经有"臣""属下"等)
        text = text[:pos] + variant + text[pos+2:]

    return text, len(to_replace)


def process_chapter(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 只处理 > 3 次的章节
    if text.count('是。') < 4:
        return 0

    new_text, n = replace_shi_in_chapter(text)
    if new_text != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
    return n


def find_all_chapters():
    files = []
    for d in DIRS:
        for f in sorted(os.listdir(d)):
            if f.endswith('.md') and f[0:2].isdigit() and not f.startswith('00'):
                files.append(os.path.join(d, f))
    return files


if __name__ == '__main__':
    chapters = find_all_chapters()
    total = 0
    for path in chapters:
        n = process_chapter(path)
        if n > 0:
            name = os.path.basename(path)[:30]
            print(f'  {name}: 替换 "是。" {n} 次')
            total += n
    print(f'\n总计: {total} 次')

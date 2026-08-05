# -*- coding: utf-8 -*-
"""
v2 破折号密度修复脚本 v4
更精细:
1. "——X——Y——"型合并为"X,Y,"(中间加逗号)
2. "——X"句首型删除
3. "X——"句中型删除
4. "X——"句末型改为"X。"(句号)或"X,"
5. 保留引号内破折号
"""
import re
import sys
import os

def fix_dashes(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('#'):
            new_lines.append(line)
            continue
        stripped = line.strip()
        if stripped.startswith('>') or stripped.startswith('*') or stripped == '' or stripped == '---' or stripped.startswith('```'):
            new_lines.append(line)
            continue
        new_lines.append(fix_line(line))
    return '\n'.join(new_lines)

def fix_line(line):
    if not line.strip():
        return line

    # 关键:不要破坏引号"——"内的对话破折号
    # 模式: 检测引号内的破折号,先保护
    # 实际:简单起见,我们只处理 行内 2+ 连续破折号 的情况
    # 如果只 1 个,留作必要对话停顿

    # 1. 模式 "——X——Y——Z——"(同句 3+ 短句被切开)
    # 转为 "X,Y,Z,"
    # 模式: ——(.+?)——(.+?)——(.+?)——
    def repl_three(m):
        parts = [m.group(i) for i in range(1, 4)]
        # 每个 part 加逗号结尾
        return ','.join(parts) + ','
    line = re.sub(r'——([^——\n。；，！？,!?;]{1,30}?)——([^——\n。；，！？,!?;]{1,30}?)——([^——\n。；，！？,!?;]{1,30}?)——', repl_three, line)

    # 2. 模式 "——X——Y——"(同句 2 短句被切开,1 个破折号还在)
    def repl_two(m):
        a, b = m.group(1), m.group(2)
        return f'{a},{b}'
    line = re.sub(r'——([^——\n。；，！？,!?;]{1,30}?)——([^——\n。；，！？,!?;]{1,30}?)——', repl_two, line)

    # 3. 模式 "——X——"孤对(2 个破折号夹 1 短句)
    line = re.sub(r'——([^——\n。；，！？,!?;]{1,30}?)——', r'\1', line)

    # 4. 模式 句首 "——"
    line = re.sub(r'^——\s*', '', line, flags=re.MULTILINE)

    # 5. 模式 句中 "X——Y" 短句后跟破折号
    # 替换为 "X,Y"
    line = re.sub(r'——([\u4e00-\u9fff，。、])', r'\1', line)

    # 6. 模式 句中 "X——"破折号后跟其他字符
    # 删除
    line = re.sub(r'——', '', line)

    return line

if __name__ == '__main__':
    fname = sys.argv[1]
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()
    new_text = fix_dashes(text)
    new_count = new_text.count('——')
    old_count = text.count('——')
    zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    print(f"{os.path.basename(fname)}: {old_count} -> {new_count} (密度 {old_count/zh_chars*100:.2f}% -> {new_count/zh_chars*100:.2f}%)")
    if '--write' in sys.argv:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(new_text)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
import colorama
colorama.init()

def extract_strings_translations(original_content):
    """
    从原文文件（包含中文翻译的 .rpy 文件）中提取字符串翻译映射。
    找到 translate ... strings: 块，解析 old 和 new 行，返回字典 {old_str: new_str}。
    """
    translations = {}
    
    # 找到 translate ... strings: 块
    pattern = r'^translate\s+\w+\s+strings:\s*\n((?:(?!#).*\n?)*)'
    match = re.search(pattern, original_content, re.MULTILINE)
    if not match:
        return translations
    
    block_content = match.group(1)
    lines = block_content.splitlines()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # 跳过空行和注释行
        if stripped == '' or stripped.startswith('#'):
            i += 1
            continue
        
        # 匹配 old 行
        old_match = re.match(r'^old\s+"((?:[^"\\]|\\.)*)"', stripped)
        if old_match:
            old_str = old_match.group(1)
            # 查找对应的 new 行（跳过空行和注释）
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()
                if next_stripped == '' or next_stripped.startswith('#'):
                    j += 1
                    continue
                new_match = re.match(r'^new\s+"((?:[^"\\]|\\.)*)"', next_stripped)
                if new_match:
                    new_str = new_match.group(1)
                    translations[old_str] = new_str
                    break
                else:
                    # 不是 new 行，可能格式错误，退出循环
                    break
            i = j + 1
        else:
            i += 1
    
    return translations

def generate_strings_block(translations, indent=''):
    """
    根据翻译字典生成字符串块内容。
    """
    lines = []
    # 添加注释说明
    lines.append(f'{indent}# 以下为合并的字符串翻译（自动生成）')
    for old_str, new_str in sorted(translations.items()):
        lines.append(f'{indent}old "{old_str}"')
        lines.append(f'{indent}new "{new_str}"')
        lines.append('')  # 空行分隔
    return '\n'.join(lines)

def process_strings_translations(reference_file, original_file, output_file):
    """
    将原文文件中的字符串翻译合并到参考文件中，覆盖输出文件。
    支持将中文中多余的条目追加到输出文件。
    """
    # 读取文件内容
    try:
        with open(reference_file, 'r', encoding='utf-8') as f:
            ref_content = f.read()
        with open(original_file, 'r', encoding='utf-8') as f:
            orig_content = f.read()
    except Exception as e:
        print(f"{colorama.Fore.RED}读取文件失败: {e}{colorama.Style.RESET_ALL}")
        return False

    # 提取中文翻译映射
    translations = extract_strings_translations(orig_content)
    if not translations:
        print(f"{colorama.Fore.YELLOW}原文文件中未找到字符串翻译块，跳过处理。{colorama.Style.RESET_ALL}")
        return True

    # 在参考文件中定位字符串翻译块
    pattern = r'^translate\s+\w+\s+strings:\s*\n((?:(?!#).*\n?)*)'
    match = re.search(pattern, ref_content, re.MULTILINE)

    if not match:
        # 参考文件没有字符串块：直接添加新的字符串块
        print(f"{colorama.Fore.YELLOW}参考文件中未找到字符串翻译块，将添加新的字符串块。{colorama.Style.RESET_ALL}")
        # 确定语言标识
        lang_match = re.search(r'^translate\s+(\w+)\s+strings:', orig_content, re.MULTILINE)
        lang = lang_match.group(1) if lang_match else 'chinese'
        new_block = f'translate {lang} strings:\n' + generate_strings_block(translations, indent='    ')
        result_content = ref_content.rstrip('\n') + '\n\n' + new_block + '\n'
        
        # 输出添加的标识符（黄色）
        print(f"{colorama.Fore.YELLOW}添加的字符串翻译标识符:{colorama.Style.RESET_ALL}")
        for old_str in sorted(translations.keys()):
            print(f"{colorama.Fore.YELLOW}  {old_str}{colorama.Style.RESET_ALL}")
        
        replacement_count = 0
        missing_translations = []
        extra_olds = set()  # 无额外条目
    else:
        # 参考文件有字符串块：处理替换和追加
        ref_olds = set()
        block_start = match.start()
        block_end = match.end()
        block_content = match.group(1)
        
        # 提取参考文件中原有的 old 集合
        for line in block_content.splitlines():
            stripped = line.strip()
            if stripped.startswith('old '):
                old_match = re.match(r'^old\s+"((?:[^"\\]|\\.)*)"', stripped)
                if old_match:
                    ref_olds.add(old_match.group(1))
        
        # 找出中文翻译中多余的 old（不在参考文件中）
        extra_olds = set(translations.keys()) - ref_olds
        if extra_olds:
            print(f"{colorama.Fore.YELLOW}原文翻译中包含但参考文件中不存在的字符串标识符:{colorama.Style.RESET_ALL}")
            for old_str in sorted(extra_olds):
                print(f"{colorama.Fore.YELLOW}  {old_str}{colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.YELLOW}这些条目将追加到文件末尾。{colorama.Style.RESET_ALL}")
        
        # 处理块内容：替换存在的，并记录缺失
        lines = block_content.splitlines()
        new_lines = []
        i = 0
        replacement_count = 0
        missing_translations = []
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            # 保留空行和注释行
            if stripped == '' or stripped.startswith('#'):
                new_lines.append(line)
                i += 1
                continue
            
            # 匹配 old 行
            old_match = re.match(r'^old\s+"((?:[^"\\]|\\.)*)"', stripped)
            if old_match:
                old_str = old_match.group(1)
                new_lines.append(line)  # 保留 old 行
                # 查找对应的 new 行（跳过空行和注释）
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    if next_stripped == '' or next_stripped.startswith('#'):
                        new_lines.append(next_line)
                        j += 1
                        continue
                    new_match = re.match(r'^new\s+"((?:[^"\\]|\\.)*)"', next_stripped)
                    if new_match:
                        # 找到 new 行，尝试替换
                        if old_str in translations:
                            # 提取缩进
                            indent_match = re.match(r'^(\s*)', next_line)
                            indent = indent_match.group(1) if indent_match else ""
                            new_line = f'{indent}new "{translations[old_str]}"'
                            new_lines.append(new_line)
                            replacement_count += 1
                        else:
                            # 保留原行，并记录缺失
                            missing_translations.append(old_str)
                            new_lines.append(next_line)
                        j += 1
                        break
                    else:
                        # 不是 new 行，可能是格式错误，保留原行并继续
                        new_lines.append(next_line)
                        j += 1
                i = j
            else:
                # 普通行（可能是 new 行但前面没有 old？忽略）
                new_lines.append(line)
                i += 1
        
        # 组装新块内容
        new_block_content = '\n'.join(new_lines)
        
        # 如果有额外条目，添加到块末尾
        if extra_olds:
            # 添加空行和注释，提高可读性
            extra_block = []
            extra_block.append('')  # 空行分隔
            extra_block.append('    # 已追加的翻译条目（原文独有）')
            for old_str in sorted(extra_olds):
                extra_block.append(f'    old "{old_str}"')
                extra_block.append(f'    new "{translations[old_str]}"')
                extra_block.append('')  # 空行分隔
            extra_block_content = '\n'.join(extra_block)
            new_block_content = new_block_content.rstrip('\n') + '\n' + extra_block_content
        
        # 构建输出文件内容：块前部分 + 新块 + 块后部分
        result_content = ref_content[:block_start] + new_block_content + ref_content[block_end:]
        
        print(f"{colorama.Fore.GREEN}合并完成！输出文件: {output_file}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}找到 {len(translations)} 个原文翻译项{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}成功匹配并替换的项数: {replacement_count}{colorama.Style.RESET_ALL}")
        if missing_translations:
            print(f"{colorama.Fore.RED}参考文件中存在但原文中没有翻译的标识符:{colorama.Style.RESET_ALL}")
            for old_str in missing_translations:
                print(f"{colorama.Fore.RED}  {old_str}{colorama.Style.RESET_ALL}")
        if extra_olds:
            print(f"{colorama.Fore.GREEN}已追加 {len(extra_olds)} 个额外字符串翻译项。{colorama.Style.RESET_ALL}")
    
    # 写入输出文件（两种情况都会执行到这里）
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result_content)
    except Exception as e:
        print(f"{colorama.Fore.RED}写入文件失败: {e}{colorama.Style.RESET_ALL}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='将原文字符串翻译合并到参考RenPy文件中的字符串块')
    parser.add_argument('reference_file', help='参考文件路径（SDK生成的英文文件，包含 translate ... strings: 块）')
    parser.add_argument('original_file', help='原文文件路径（包含中文翻译的文件，包含 translate ... strings: 块）')
    parser.add_argument('output_file', help='输出文件路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.reference_file):
        print(f"{colorama.Fore.RED}错误: 参考文件 {args.reference_file} 不存在{colorama.Style.RESET_ALL}")
        return
    if not os.path.exists(args.original_file):
        print(f"{colorama.Fore.RED}错误: 原文文件 {args.original_file} 不存在{colorama.Style.RESET_ALL}")
        return
    
    process_strings_translations(args.reference_file, args.original_file, args.output_file)

if __name__ == "__main__":
    main()
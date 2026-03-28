#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse

def merge_translation_files(reference_file, original_file, output_file):
    """
    将原文翻译内容合并到参考RenPy文件中，通过唯一标识符精确匹配
    """
    # 读取参考文件内容
    with open(reference_file, 'r', encoding='utf-8') as f:
        reference_content = f.read()
    
    # 读取原文文件内容
    with open(original_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # 提取原文中的翻译内容，以唯一标识符为键
    original_translations = extract_original_translations_by_id(original_content)
    
    # 处理参考文件，将原文翻译内容填入
    result_content, replacement_count, missing_translations = process_reference_file_by_id(reference_content, original_translations)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result_content)
    
    print(f"合并完成！输出文件: {output_file}")
    print(f"找到 {len(original_translations)} 个原文翻译项")
    print(f"成功匹配并替换的项数: {replacement_count}")
    if missing_translations:
        print(f"未找到翻译的标识符: {missing_translations}")

def extract_original_translations_by_id(content):
    """
    从原文文件中提取翻译内容，以唯一标识符为键构建字典
    """
    translations = {}
    
    # 跳过 translate strings 块
    content_without_strings = re.sub(r'translate [^:]+ strings:.*?(?=^translate|\Z)', '', content, flags=re.DOTALL | re.MULTILINE)
    
    # 更精确的正则表达式，匹配完整的翻译块
    # 匹配 translate 行及其后的内容直到下一个 translate 块开始
    pattern = r'^translate [^:]+ ([^:\s]+):\s*\n((?:(?:\s*# [^\n]*\n)?\s*(?:".*?"|[^#\n\s].*?)(?:\s*#.*?\n?)*)+?)(?=\n\s*translate|\Z)'
    matches = re.finditer(pattern, content_without_strings, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        identifier = match.group(1)  # 唯一标识符，如 gym_lesson1outro_59225ee3
        block_content = match.group(2)
        
        # 提取翻译内容 - 寻找非注释行中的引号内容或普通文本
        lines = block_content.split('\n')
        translation_content = None
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#'):
                # 检查是否包含引号（处理 "文本" 或 角色名 "文本" 格式）
                quote_match = re.search(r'"([^"]*)"', line_stripped)
                if quote_match:
                    extracted_text = quote_match.group(1)
                    # 检查是否包含中文字符
                    if any('\u4e00' <= char <= '\u9fff' for char in extracted_text):
                        translation_content = f'"{extracted_text}"'
                        break
                    # 如果不包含中文字符，可能是英文原文，继续查找
        
        if translation_content:
            translations[identifier] = translation_content
            print(f"提取到原文翻译: {identifier} -> {translation_content}")
    
    # 处理没有行号注释的翻译块
    pattern2 = r'^translate [^:]+ ([^:\s]+):\s*\n((?:(?:\s*# [^\n]*\n)?\s*(?:".*?"|[^#\n\s].*?)(?:\s*#.*?\n?)*)+?)(?=\n\s*translate|\Z)'
    matches2 = re.finditer(pattern2, content_without_strings, re.MULTILINE | re.DOTALL)
    
    for match in matches2:
        identifier = match.group(1)
        block_content = match.group(2)
        
        # 提取翻译内容
        lines = block_content.split('\n')
        translation_content = None
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#'):
                # 检查是否包含引号（处理 "文本" 或 角色名 "文本" 格式）
                quote_match = re.search(r'"([^"]*)"', line_stripped)
                if quote_match:
                    extracted_text = quote_match.group(1)
                    # 检查是否包含中文字符
                    if any('\u4e00' <= char <= '\u9fff' for char in extracted_text):
                        translation_content = f'"{extracted_text}"'
                        break
                    # 如果不包含中文字符，可能是英文原文，继续查找
        
        if translation_content and identifier not in translations:
            translations[identifier] = translation_content
            print(f"提取到原文翻译: {identifier} -> {translation_content}")
    
    return translations

def process_reference_file_by_id(content, original_translations):
    """
    处理参考文件，通过唯一标识符精确匹配并替换空对话行
    """
    lines = content.splitlines()
    result_lines = []
    i = 0
    replacement_count = 0
    missing_translations = []
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        # 检查是否是行号注释行
        if stripped_line.startswith('# game/'):
            result_lines.append(line)
            i += 1
            continue
        
        # 检查是否是translate行，提取标识符
        translate_match = re.search(r'translate [^:]+ ([^:\s]+):', stripped_line)
        if translate_match:
            identifier = translate_match.group(1)  # 如 gym_lesson1outro_59225ee3
            
            result_lines.append(line)  # 添加translate行
            i += 1
            
            # 处理翻译块内容
            block_processed = False
            while i < len(lines):
                current_line = lines[i]
                current_stripped = current_line.strip()
                
                # 检查是否是下一个translate块或行号注释
                if current_stripped.startswith('translate') or (current_stripped.startswith('#') and 'game/' in current_stripped and ':' in current_stripped):
                    block_processed = True
                    break
                
                # 检查是否是空对话行（""）或包含空引号的内容
                if current_stripped == '""' or (current_stripped.startswith('"') and current_stripped.endswith('"') and len(current_stripped) <= 3):
                    # 查找是否有对应的原文翻译
                    if identifier in original_translations:
                        # 提取当前行的缩进
                        indent_match = re.match(r'^(\s*)', current_line)
                        indent = indent_match.group(1) if indent_match else ""
                        
                        # 替换为空行和翻译内容
                        result_lines.append(f'{indent}{original_translations[identifier]}')
                        print(f"匹配并替换: {identifier} -> {original_translations[identifier]}")
                        replacement_count += 1
                    else:
                        # 没有找到匹配的翻译，记录标识符
                        if identifier not in missing_translations:
                            missing_translations.append(identifier)
                        # 保留原样
                        result_lines.append(current_line)
                else:
                    # 检查是否包含空引号（如 Toord "" 或 Cassidy blush ""）
                    empty_quote_match = re.search(r'(\w+(?:\s+\w+)*)\s+""', current_stripped)
                    if empty_quote_match:
                        if identifier in original_translations:
                            # 提取前面的角色名和表情部分
                            indent_match = re.match(r'^(\s*)', current_line)
                            indent = indent_match.group(1) if indent_match else ""
                            
                            # 提取角色名和表情
                            char_expression = empty_quote_match.group(1)
                            result_lines.append(f'{indent}{char_expression} {original_translations[identifier]}')
                            print(f"匹配并替换: {identifier} -> {original_translations[identifier]}")
                            replacement_count += 1
                        else:
                            # 没有找到匹配的翻译，记录标识符
                            if identifier not in missing_translations:
                                missing_translations.append(identifier)
                            result_lines.append(current_line)
                    else:
                        # 普通行，保留原样
                        result_lines.append(current_line)
                
                i += 1
            
            if not block_processed:
                break
            continue
        
        result_lines.append(line)
        i += 1
    
    return '\n'.join(result_lines), replacement_count, missing_translations

def main():
    parser = argparse.ArgumentParser(description='将原文翻译内容合并到参考RenPy文件中（通过唯一标识符精确匹配）')
    parser.add_argument('reference_file', help='参考翻译文件路径（SDK输出的文件）')
    parser.add_argument('original_file', help='原文翻译文件路径（包含中文翻译的文件）')
    parser.add_argument('output_file', help='输出文件路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.reference_file):
        print(f"错误: 参考文件 {args.reference_file} 不存在")
        return
    
    if not os.path.exists(args.original_file):
        print(f"错误: 原文文件 {args.original_file} 不存在")
        return
    
    merge_translation_files(args.reference_file, args.original_file, args.output_file)

if __name__ == "__main__":
    main()
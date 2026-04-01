#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import argparse
import colorama
colorama.init()

def prepare_translation_files(chinese_dir, english_dir, output_dir):
    """
    准备翻译文件：复制并重命名chinese和english文件到指定目录
    对于中英文都有的文件 → xxxC.rpy / xxxE.rpy + 空 xxx.rpy
    对于只有中文或只有英文的文件 → 保留原文件名直接复制
    同时复制中文目录中所有非 .rpy/.rpyc 的文件和目录到输出目录
    """
    # 创建输出目录结构
    os.makedirs(output_dir, exist_ok=True)
    
    # 用于统计
    files_processed = 0
    single_chinese_copied = 0
    single_english_copied = 0
    non_translation_copied = 0
    
    # 首先，收集所有文件的相对路径
    chinese_files = {}
    english_files = {}
    
    # 收集chinese目录中的所有.rpy文件
    for root, dirs, files in os.walk(chinese_dir):
        for file in files:
            if file.endswith('.rpy'):
                rel_path = os.path.relpath(root, chinese_dir)
                if rel_path == '.':
                    rel_path = ''
                full_rel_path = os.path.join(rel_path, file) if rel_path else file
                chinese_files[full_rel_path] = os.path.join(root, file)
    
    # 收集english目录中的所有.rpy文件
    for root, dirs, files in os.walk(english_dir):
        for file in files:
            if file.endswith('.rpy'):
                rel_path = os.path.relpath(root, english_dir)
                if rel_path == '.':
                    rel_path = ''
                full_rel_path = os.path.join(rel_path, file) if rel_path else file
                english_files[full_rel_path] = os.path.join(root, file)
    
    # 找出所有共同的文件（中英文都有）
    common_files = set(chinese_files.keys()) & set(english_files.keys())
    
    # 找出只有中文没有英文的文件
    only_chinese_files = set(chinese_files.keys()) - set(english_files.keys())
    
    # 找出只有英文没有中文的文件
    only_english_files = set(english_files.keys()) - set(chinese_files.keys())
    
    # 处理共同的文件
    print(f"{colorama.Fore.BLUE}处理中英文都有的文件：{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.BLUE}{'-' * 80}{colorama.Style.RESET_ALL}")
    for file_rel_path in sorted(common_files):
        file = os.path.basename(file_rel_path)
        rel_path = os.path.dirname(file_rel_path) if os.path.dirname(file_rel_path) else ''
        
        # 获取源文件路径
        chinese_file = chinese_files[file_rel_path]
        english_file = english_files[file_rel_path]
        
        # 在输出目录中创建相同的目录结构
        output_subdir = os.path.join(output_dir, rel_path)
        os.makedirs(output_subdir, exist_ok=True)
        
        # 获取文件名（不含扩展名）
        filename_without_ext = os.path.splitext(file)[0]
        
        # 复制并重命名文件
        # chinese文件 -> xxxC.rpy
        chinese_output = os.path.join(output_subdir, f"{filename_without_ext}C.rpy")
        shutil.copy2(chinese_file, chinese_output)
        
        # english文件 -> xxxE.rpy  
        english_output = os.path.join(output_subdir, f"{filename_without_ext}E.rpy")
        shutil.copy2(english_file, english_output)
        
        # 创建空的合并文件 xxx.rpy
        merge_output = os.path.join(output_subdir, f"{filename_without_ext}.rpy")
        with open(merge_output, 'w', encoding='utf-8') as f:
            f.write("")
        
        if rel_path:
            print(f"{colorama.Fore.GREEN}处理: {rel_path}\\{file}{colorama.Style.RESET_ALL}")
        else:
            print(f"{colorama.Fore.GREEN}处理: {file}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}  已复制: {os.path.basename(chinese_output)}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}  已复制: {os.path.basename(english_output)}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}  已创建: {os.path.basename(merge_output)}{colorama.Style.RESET_ALL}")
        
        files_processed += 1
    
    print(f"\n{colorama.Fore.BLUE}共处理 {files_processed} 个文件对{colorama.Style.RESET_ALL}")
    
    # 处理只有中文没有英文的文件（直接复制，保留原文件名）
    if only_chinese_files:
        print(f"{colorama.Fore.YELLOW}\n处理只有中文的文件（直接复制，保留原文件名）:{colorama.Style.RESET_ALL}")
        for file_rel_path in sorted(only_chinese_files):
            file = os.path.basename(file_rel_path)
            rel_path = os.path.dirname(file_rel_path) if os.path.dirname(file_rel_path) else ''
            src_path = chinese_files[file_rel_path]
            
            output_subdir = os.path.join(output_dir, rel_path)
            os.makedirs(output_subdir, exist_ok=True)
            dst_path = os.path.join(output_subdir, file)
            shutil.copy2(src_path, dst_path)
            print(f"{colorama.Fore.YELLOW}  复制: {file_rel_path}{colorama.Style.RESET_ALL}")
            single_chinese_copied += 1
        print(f"{colorama.Fore.YELLOW}共复制 {single_chinese_copied} 个只有中文的文件{colorama.Style.RESET_ALL}")
    
    # 处理只有英文没有中文的文件（直接复制，保留原文件名）
    if only_english_files:
        print(f"{colorama.Fore.YELLOW}\n处理只有英文的文件（直接复制，保留原文件名）:{colorama.Style.RESET_ALL}")
        for file_rel_path in sorted(only_english_files):
            file = os.path.basename(file_rel_path)
            rel_path = os.path.dirname(file_rel_path) if os.path.dirname(file_rel_path) else ''
            src_path = english_files[file_rel_path]
            
            output_subdir = os.path.join(output_dir, rel_path)
            os.makedirs(output_subdir, exist_ok=True)
            dst_path = os.path.join(output_subdir, file)
            shutil.copy2(src_path, dst_path)
            print(f"{colorama.Fore.YELLOW}  复制: {file_rel_path}{colorama.Style.RESET_ALL}")
            single_english_copied += 1
        print(f"{colorama.Fore.YELLOW}共复制 {single_english_copied} 个只有英文的文件{colorama.Style.RESET_ALL}")
    
    # 处理非翻译文件（所有非 .rpy/.rpyc 的文件和目录）
    print(f"{colorama.Fore.CYAN}\n处理非rpy翻译文件（图片、字体、音频等）...{colorama.Style.RESET_ALL}")
    for root, dirs, files in os.walk(chinese_dir):
        rel_path = os.path.relpath(root, chinese_dir)
        if rel_path == '.':
            rel_path = ''
        
        for file in files:
            # 排除 .rpy 和 .rpyc 文件
            if file.endswith(('.rpy', '.rpyc')):
                continue
            
            src_path = os.path.join(root, file)
            dst_subdir = os.path.join(output_dir, rel_path) if rel_path else output_dir
            os.makedirs(dst_subdir, exist_ok=True)
            dst_path = os.path.join(dst_subdir, file)
            
            # 避免重复复制（如果目标文件已存在，根据修改时间决定是否覆盖）
            if not os.path.exists(dst_path) or os.path.getmtime(src_path) > os.path.getmtime(dst_path):
                shutil.copy2(src_path, dst_path)
                print(f"{colorama.Fore.CYAN}  复制: {os.path.join(rel_path, file) if rel_path else file}{colorama.Style.RESET_ALL}")
                non_translation_copied += 1
    
    # 输出警告信息（仅列出缺少对应语言的文件，但已复制）
    if only_chinese_files:
        print(f"{colorama.Fore.RED}\n警告: {len(only_chinese_files)} 个文件只有中文版本（缺少对应的英文版本）:{colorama.Style.RESET_ALL}")
        for i, file_rel_path in enumerate(sorted(only_chinese_files), 1):
            print(f"{colorama.Fore.RED}  {i:3d}. {file_rel_path}{colorama.Style.RESET_ALL}")
    
    if only_english_files:
        print(f"{colorama.Fore.RED}\n警告: {len(only_english_files)} 个文件只有英文版本（缺少对应的中文版本）:{colorama.Style.RESET_ALL}")
        for i, file_rel_path in enumerate(sorted(only_english_files), 1):
            print(f"{colorama.Fore.RED}  {i:3d}. {file_rel_path}{colorama.Style.RESET_ALL}")
    
    print(f"\n{colorama.Fore.BLUE}统计摘要:{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.BLUE}{'-' * 50}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.BLUE}中英文都有的文件: {len(common_files)} 个{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.RED}只有中文的文件: {len(only_chinese_files)} 个 (已复制原文件){colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.RED}只有英文的文件: {len(only_english_files)} 个 (已复制原文件，记得翻译哈){colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.BLUE}复制的非翻译文件: {non_translation_copied} 个{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.BLUE}总计中文文件: {len(chinese_files)} 个{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.BLUE}总计英文文件: {len(english_files)} 个{colorama.Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='准备翻译文件：复制并重命名chinese和english文件')
    parser.add_argument('chinese_dir', help='chinese目录路径')
    parser.add_argument('english_dir', help='english目录路径')
    parser.add_argument('output_dir', help='输出目录路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.chinese_dir):
        print(f"{colorama.Fore.RED}错误: chinese目录 {args.chinese_dir} 不存在{colorama.Style.RESET_ALL}")
        return
    
    if not os.path.exists(args.english_dir):
        print(f"{colorama.Fore.RED}错误: english目录 {args.english_dir} 不存在{colorama.Style.RESET_ALL}")
        return
    
    prepare_translation_files(args.chinese_dir, args.english_dir, args.output_dir)

if __name__ == "__main__":
    main()
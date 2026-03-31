#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import argparse
import colorama
colorama.init()

def prepare_translation_files(chinese_dir, english_dir, output_dir):
    """
    准备翻译文件：复制并重命名schinese和english文件到指定目录
    对于中英文都有的文件 → xxxC.rpy / xxxE.rpy + 空 xxx.rpy
    对于只有中文或只有英文的文件 → 保留原文件名直接复制
    """
    # 创建输出目录结构
    os.makedirs(output_dir, exist_ok=True)
    
    # 用于统计
    files_processed = 0
    single_chinese_copied = 0
    single_english_copied = 0
    missing_english_files = []   # 中文有，英文没有
    missing_chinese_files = []   # 英文有，中文没有
    
    # 首先，收集所有文件的相对路径
    schinese_files = {}
    english_files = {}
    
    # 收集schinese目录中的所有.rpy文件
    for root, dirs, files in os.walk(chinese_dir):
        for file in files:
            if file.endswith('.rpy'):
                rel_path = os.path.relpath(root, chinese_dir)
                if rel_path == '.':
                    rel_path = ''
                full_rel_path = os.path.join(rel_path, file) if rel_path else file
                schinese_files[full_rel_path] = os.path.join(root, file)
    
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
    common_files = set(schinese_files.keys()) & set(english_files.keys())
    
    # 找出只有中文没有英文的文件
    only_schinese_files = set(schinese_files.keys()) - set(english_files.keys())
    
    # 找出只有英文没有中文的文件
    only_english_files = set(english_files.keys()) - set(schinese_files.keys())
    
    # 处理共同的文件
    print("处理中英文都有的文件：")
    print("-" * 80)
    for file_rel_path in sorted(common_files):
        file = os.path.basename(file_rel_path)
        rel_path = os.path.dirname(file_rel_path) if os.path.dirname(file_rel_path) else ''
        
        # 获取源文件路径
        schinese_file = schinese_files[file_rel_path]
        english_file = english_files[file_rel_path]
        
        # 在输出目录中创建相同的目录结构
        output_subdir = os.path.join(output_dir, rel_path)
        os.makedirs(output_subdir, exist_ok=True)
        
        # 获取文件名（不含扩展名）
        filename_without_ext = os.path.splitext(file)[0]
        
        # 复制并重命名文件
        # schinese文件 -> xxxC.rpy
        schinese_output = os.path.join(output_subdir, f"{filename_without_ext}C.rpy")
        shutil.copy2(schinese_file, schinese_output)
        
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
        print(f"{colorama.Fore.GREEN}  已复制: {os.path.basename(schinese_output)}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}  已复制: {os.path.basename(english_output)}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}  已创建: {os.path.basename(merge_output)}{colorama.Style.RESET_ALL}")
        
        files_processed += 1
    
    print(f"\n共处理 {files_processed} 个文件对")
    
    # 处理只有中文没有英文的文件（直接复制，保留原文件名）
    if only_schinese_files:
        print(f"{colorama.Fore.YELLOW}\n处理只有中文的文件（直接复制，保留原文件名）:{colorama.Style.RESET_ALL}")
        for file_rel_path in sorted(only_schinese_files):
            file = os.path.basename(file_rel_path)
            rel_path = os.path.dirname(file_rel_path) if os.path.dirname(file_rel_path) else ''
            src_path = schinese_files[file_rel_path]
            
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
    
    # 输出警告信息（仅列出缺少对应语言的文件，但已复制）
    if only_schinese_files:
        print(f"{colorama.Fore.RED}\n警告: {len(only_schinese_files)} 个文件只有中文版本（缺少对应的英文版本）:{colorama.Style.RESET_ALL}")
        for i, file_rel_path in enumerate(sorted(only_schinese_files), 1):
            print(f"{colorama.Fore.RED}  {i:3d}. {file_rel_path}{colorama.Style.RESET_ALL}")
    
    if only_english_files:
        print(f"{colorama.Fore.RED}\n警告: {len(only_english_files)} 个文件只有英文版本（缺少对应的中文版本）:{colorama.Style.RESET_ALL}")
        for i, file_rel_path in enumerate(sorted(only_english_files), 1):
            print(f"{colorama.Fore.RED}  {i:3d}. {file_rel_path}{colorama.Style.RESET_ALL}")
    
    print(f"\n统计摘要:")
    print(f"-" * 50)
    print(f"中英文都有的文件: {len(common_files)} 个")
    print(f"{colorama.Fore.RED}只有中文的文件: {len(only_schinese_files)} 个 (已复制原文件){colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.RED}只有英文的文件: {len(only_english_files)} 个 (已复制原文件，记得翻译哈){colorama.Style.RESET_ALL}")
    print(f"总计中文文件: {len(schinese_files)} 个")
    print(f"总计英文文件: {len(english_files)} 个")

def main():
    parser = argparse.ArgumentParser(description='准备翻译文件：复制并重命名schinese和english文件')
    parser.add_argument('chinese_dir', help='schinese目录路径')
    parser.add_argument('english_dir', help='english目录路径')
    parser.add_argument('output_dir', help='输出目录路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.chinese_dir):
        print(f"错误: schinese目录 {args.chinese_dir} 不存在")
        return
    
    if not os.path.exists(args.english_dir):
        print(f"错误: english目录 {args.english_dir} 不存在")
        return
    
    prepare_translation_files(args.chinese_dir, args.english_dir, args.output_dir)

if __name__ == "__main__":
    main()
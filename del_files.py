#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import colorama
colorama.init()

def find_intermediate_files(directory):
    """
    查找目录中所有 xxxC.rpy 和 xxxE.rpy 文件对，返回要删除的文件路径列表
    """
    to_delete = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('C.rpy') or file.endswith('E.rpy'):
                base = file[:-5]  # 去掉最后5个字符 'C.rpy' 或 'E.rpy'
                merged_file = os.path.join(root, base + '.rpy')
                if os.path.exists(merged_file):
                    to_delete.append(os.path.join(root, file))
                else:
                    rel_file = os.path.relpath(os.path.join(root, file), directory) if directory != '.' else file
                    print(f"{colorama.Fore.YELLOW}警告: 文件 {rel_file} 没有对应的合并文件，将不会删除。{colorama.Style.RESET_ALL}")
    return to_delete

def delete_intermediate_files(directory, confirm=True):
    """
    删除指定目录下的所有中间文件（xxxC.rpy 和 xxxE.rpy），前提是存在对应的 xxx.rpy。
    
    Args:
        directory: 要扫描的目录
        confirm: 是否要求用户确认
    
    Returns:
        int: 删除的文件数量
    """
    if not os.path.exists(directory):
        print(f"{colorama.Fore.RED}错误: 目录 {directory} 不存在{colorama.Style.RESET_ALL}")
        return 0

    to_delete = find_intermediate_files(directory)
    if not to_delete:
        print(f"{colorama.Fore.BLUE}没有找到要删除的中间文件（C.rpy 或 E.rpy）。{colorama.Style.RESET_ALL}")
        return 0

    print(f"{colorama.Fore.BLUE}找到 {len(to_delete)} 个中间文件:{colorama.Style.RESET_ALL}")
    for f in to_delete:
        rel = os.path.relpath(f, directory) if directory != '.' else f
        print(f"  {colorama.Fore.CYAN}{rel}{colorama.Style.RESET_ALL}")

    if confirm:
        resp = input(f"{colorama.Fore.RED}确认删除以上 {len(to_delete)} 个文件？(y/N): {colorama.Style.RESET_ALL}").strip().lower()
        if resp != 'y':
            print(f"{colorama.Fore.BLUE}取消删除。{colorama.Style.RESET_ALL}")
            return 0

    deleted = 0
    for f in to_delete:
        try:
            os.remove(f)
            rel = os.path.relpath(f, directory) if directory != '.' else f
            print(f"{colorama.Fore.GREEN}已删除: {rel}{colorama.Style.RESET_ALL}")
            deleted += 1
        except Exception as e:
            rel = os.path.relpath(f, directory) if directory != '.' else f
            print(f"{colorama.Fore.RED}删除失败 {rel}: {e}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.GREEN}成功删除 {deleted}/{len(to_delete)} 个文件。{colorama.Style.RESET_ALL}")
    return deleted

def main():
    parser = argparse.ArgumentParser(description='删除 RenPy 翻译工作目录中的中间文件 (xxxC.rpy 和 xxxE.rpy)')
    parser.add_argument('directory', nargs='?', default='.', help='要扫描的目录路径（默认当前目录）')
    parser.add_argument('-y', '--yes', action='store_true', help='跳过确认提示')
    args = parser.parse_args()

    delete_intermediate_files(args.directory, confirm=not args.yes)

if __name__ == "__main__":
    main()
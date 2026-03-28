#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import argparse

def find_file_pairs(directory):
    """
    在指定目录中查找所有的文件对 (xxxC.rpy 和 xxxE.rpy)
    """
    file_pairs = []
    
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        # 查找所有以C.rpy结尾的文件
        c_files = [f for f in files if f.endswith('C.rpy')]
        
        for c_file in c_files:
            # 提取基础文件名 - 修正：去掉'C.rpy'而不是固定长度
            # 例如 commonC.rpy -> common
            base_name = c_file[:-5]  # 去掉最后5个字符'C.rpy'
            
            # 构建对应的E文件名
            e_file = f"{base_name}E.rpy"
            merge_file = f"{base_name}.rpy"
            
            # 检查对应的E文件是否存在
            e_file_path = os.path.join(root, e_file)
            if os.path.exists(e_file_path):
                # 获取相对路径
                rel_path = os.path.relpath(root, directory)
                if rel_path == '.':
                    rel_path = ''
                
                # 构建完整路径
                c_file_path = os.path.join(root, c_file)
                merge_file_path = os.path.join(root, merge_file)
                
                file_pairs.append({
                    'name': base_name,
                    'rel_path': rel_path,
                    'c_file': c_file_path,
                    'e_file': e_file_path,
                    'merge_file': merge_file_path
                })
    
    return file_pairs

def display_file_pairs(file_pairs):
    """
    显示可用的文件对供用户选择
    """
    if not file_pairs:
        print("未找到任何可处理的文件对！")
        return -1
    
    print(f"找到 {len(file_pairs)} 个文件对：")
    print("=" * 80)
    
    # 按目录分组显示
    grouped_pairs = {}
    for pair in file_pairs:
        dir_name = pair['rel_path'] if pair['rel_path'] else "根目录"
        if dir_name not in grouped_pairs:
            grouped_pairs[dir_name] = []
        grouped_pairs[dir_name].append(pair)
    
    # 计算文件名最大长度以便对齐
    max_name_length = max(len(pair['name']) for pair in file_pairs) if file_pairs else 0
    max_name_length = min(max_name_length, 40)  # 限制最大长度
    
    # 显示分组
    all_pairs = []
    current_index = 1
    
    for dir_name, pairs in sorted(grouped_pairs.items()):
        print(f"\n[{dir_name}]")
        print("-" * 60)
        
        for pair in sorted(pairs, key=lambda x: x['name']):
            display_name = pair['name']
            if len(display_name) > 35:
                display_name = display_name[:32] + "..."
            
            print(f"{current_index:3d}. {display_name:<35}")
            all_pairs.append(pair)
            current_index += 1
    
    print("=" * 80)
    return all_pairs

def format_single_pair(c_file, e_file, merge_file, format_script="format.py"):
    """
    使用format.py处理单个文件对，使用系统默认编码
    """
    print(f"\n正在处理: {os.path.basename(c_file)} -> {os.path.basename(merge_file)}")
    print(f"中文文件: {c_file}")
    print(f"英文文件: {e_file}")
    
    # 检查文件是否存在
    if not os.path.exists(c_file):
        print(f"错误: 文件不存在 {c_file}")
        return False
    
    if not os.path.exists(e_file):
        print(f"错误: 文件不存在 {e_file}")
        return False
    
    # 构建命令 - 确保使用正确的编码
    command = ["python", format_script, e_file, c_file, merge_file]
    
    try:
        # 使用系统默认编码执行命令
        result = subprocess.run(command, 
                               capture_output=True, 
                               text=True, 
                               encoding=sys.getdefaultencoding(),
                               errors='replace')
        
        # 打印简化输出（只显示重要信息）
        if result.stdout:
            # 过滤出关键信息
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("合并完成") or line.startswith("找到") or line.startswith("成功匹配") or "提取到原文翻译" in line or "匹配并替换" in line:
                    print(line)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✓ 处理完成: {merge_file}")
            return True
        else:
            print(f"✗ 处理失败: 返回码 {result.returncode}")
            return False
            
    except Exception as e:
        print(f"✗ 执行出错: {e}")
        return False

def format_single_pair_direct(c_file, e_file, merge_file):
    """
    直接调用format.py的函数，避免subprocess编码问题
    """
    print(f"\n正在处理: {os.path.basename(c_file)} -> {os.path.basename(merge_file)}")
    print(f"中文文件: {c_file}")
    print(f"英文文件: {e_file}")
    
    # 检查文件是否存在
    if not os.path.exists(c_file):
        print(f"错误: 文件不存在 {c_file}")
        return False
    
    if not os.path.exists(e_file):
        print(f"错误: 文件不存在 {e_file}")
        return False
    
    try:
        # 将当前目录添加到Python路径
        sys.path.insert(0, os.path.dirname(__file__))
        
        # 导入并直接调用format.py的函数
        from format import merge_translation_files
        merge_translation_files(e_file, c_file, merge_file)
        
        print(f"✓ 处理完成: {merge_file}")
        return True
    except ImportError as e:
        print(f"✗ 无法导入format.py: {e}")
        print("尝试使用subprocess方式...")
        # 回退到subprocess方式
        return format_single_pair_subprocess(c_file, e_file, merge_file, "format.py")
    except Exception as e:
        print(f"✗ 执行出错: {e}")
        return False

def format_single_pair_subprocess(c_file, e_file, merge_file, format_script="format.py"):
    """
    使用subprocess执行format.py，处理编码问题
    """
    # 构建命令
    command = ["python", format_script, e_file, c_file, merge_file]
    
    try:
        # 使用系统默认编码执行命令
        result = subprocess.run(command, 
                               capture_output=True, 
                               text=False,  # 不使用text模式，自己解码
                               encoding=None)  # 不指定编码
        
        # 解码输出
        stdout = result.stdout.decode(sys.getdefaultencoding(), errors='replace')
        stderr = result.stderr.decode(sys.getdefaultencoding(), errors='replace')
        
        # 打印简化输出
        if stdout:
            lines = stdout.split('\n')
            for line in lines:
                line = line.strip()
                if line and ("合并完成" in line or "找到" in line or "成功匹配" in line or "提取到原文翻译" in line or "匹配并替换" in line):
                    print(line)
        
        if stderr:
            print("错误:")
            print(stderr)
        
        if result.returncode == 0:
            print(f"✓ 处理完成: {merge_file}")
            return True
        else:
            print(f"✗ 处理失败: 返回码 {result.returncode}")
            return False
            
    except Exception as e:
        print(f"✗ 执行出错: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='交互式选择并合并翻译文件')
    parser.add_argument('directory', nargs='?', default='.', help='要扫描的目录路径（默认当前目录）')
    parser.add_argument('--format-script', default='format.py', help='format.py脚本路径（默认当前目录）')
    parser.add_argument('--mode', choices=['direct', 'subprocess'], default='direct',
                       help='执行模式：direct-直接调用函数，subprocess-使用子进程')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误: 目录 {args.directory} 不存在")
        return
    
    # 检查format.py是否存在（如果是subprocess模式）
    if args.mode == 'subprocess' and not os.path.exists(args.format_script):
        print(f"错误: format.py脚本 {args.format_script} 不存在")
        return
    
    # 查找文件对
    print(f"正在扫描目录: {args.directory}")
    file_pairs = find_file_pairs(args.directory)
    
    if not file_pairs:
        print("没有找到任何文件对！请确保已运行 prepare_files.py")
        return
    
    # 显示文件对
    all_pairs = display_file_pairs(file_pairs)
    if not all_pairs:
        return
    
    while True:
        try:
            print(f"\n当前模式: {args.mode}")
            print("请选择操作:")
            print("1. 处理单个文件对")
            print("2. 批量处理所有文件对")
            print("3. 按目录批量处理")
            print("4. 切换执行模式")
            print("5. 重新扫描")
            print("6. 退出")
            
            choice = input("请输入选项 (1-6): ").strip()
            
            if choice == '1':
                # 选择单个文件对
                try:
                    selection = input(f"请输入要处理的文件编号 (1-{len(all_pairs)}): ").strip()
                    if not selection:
                        continue
                    
                    index = int(selection) - 1
                    if 0 <= index < len(all_pairs):
                        pair = all_pairs[index]
                        
                        if args.mode == 'direct':
                            format_single_pair_direct(
                                pair['c_file'], 
                                pair['e_file'], 
                                pair['merge_file']
                            )
                        else:
                            format_single_pair_subprocess(
                                pair['c_file'], 
                                pair['e_file'], 
                                pair['merge_file'],
                                args.format_script
                            )
                    else:
                        print(f"错误: 编号必须在 1-{len(all_pairs)} 之间")
                except ValueError:
                    print("错误: 请输入有效的数字")
            
            elif choice == '2':
                # 批量处理所有文件对
                confirm = input(f"确定要批量处理所有 {len(all_pairs)} 个文件对吗？(y/n): ").strip().lower()
                if confirm == 'y':
                    success_count = 0
                    for i, pair in enumerate(all_pairs, 1):
                        print(f"\n[{i}/{len(all_pairs)}] ", end='')
                        
                        if args.mode == 'direct':
                            if format_single_pair_direct(
                                pair['c_file'], 
                                pair['e_file'], 
                                pair['merge_file']
                            ):
                                success_count += 1
                        else:
                            if format_single_pair_subprocess(
                                pair['c_file'], 
                                pair['e_file'], 
                                pair['merge_file'],
                                args.format_script
                            ):
                                success_count += 1
                    
                    print(f"\n批量处理完成！")
                    print(f"成功: {success_count}/{len(all_pairs)}")
            
            elif choice == '3':
                # 按目录批量处理
                print("\n可用目录:")
                directories = sorted(set(pair['rel_path'] for pair in all_pairs))
                for i, dir_name in enumerate(directories, 1):
                    dir_display = dir_name if dir_name else "根目录"
                    print(f"{i}. {dir_display}")
                
                try:
                    dir_selection = input(f"请选择目录 (1-{len(directories)}): ").strip()
                    if dir_selection:
                        dir_index = int(dir_selection) - 1
                        if 0 <= dir_index < len(directories):
                            selected_dir = directories[dir_index]
                            dir_pairs = [p for p in all_pairs if p['rel_path'] == selected_dir]
                            
                            dir_display = selected_dir if selected_dir else "根目录"
                            confirm = input(f"确定要批量处理 {dir_display} 目录下的 {len(dir_pairs)} 个文件对吗？(y/n): ").strip().lower()
                            if confirm == 'y':
                                success_count = 0
                                for i, pair in enumerate(dir_pairs, 1):
                                    print(f"\n[{i}/{len(dir_pairs)}] ", end='')
                                    
                                    if args.mode == 'direct':
                                        if format_single_pair_direct(
                                            pair['c_file'], 
                                            pair['e_file'], 
                                            pair['merge_file']
                                        ):
                                            success_count += 1
                                    else:
                                        if format_single_pair_subprocess(
                                            pair['c_file'], 
                                            pair['e_file'], 
                                            pair['merge_file'],
                                            args.format_script
                                        ):
                                            success_count += 1
                                
                                print(f"\n目录 {dir_display} 处理完成！")
                                print(f"成功: {success_count}/{len(dir_pairs)}")
                        else:
                            print(f"错误: 目录编号必须在 1-{len(directories)} 之间")
                except ValueError:
                    print("错误: 请输入有效的数字")
            
            elif choice == '4':
                # 切换执行模式
                print("\n当前模式:", args.mode)
                print("1. direct - 直接调用函数（推荐）")
                print("2. subprocess - 使用子进程")
                mode_choice = input("请选择模式 (1-2): ").strip()
                if mode_choice == '1':
                    args.mode = 'direct'
                    print("已切换到 direct 模式")
                elif mode_choice == '2':
                    args.mode = 'subprocess'
                    print("已切换到 subprocess 模式")
                else:
                    print("无效选择，保持当前模式")
            
            elif choice == '5':
                # 重新扫描
                print("重新扫描目录...")
                file_pairs = find_file_pairs(args.directory)
                all_pairs = display_file_pairs(file_pairs)
                if not all_pairs:
                    return
            
            elif choice == '6':
                print("再见！")
                break
            
            else:
                print("错误: 请输入有效的选项 (1-6)")
        
        except KeyboardInterrupt:
            print("\n\n用户中断操作")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import argparse
import colorama
colorama.init()

# 将当前目录添加到 Python 路径，以便导入同目录下的 prepare_files 和 del_files
sys.path.insert(0, os.path.dirname(__file__))

try:
    import prepare_files
except ImportError:
    print(f"{colorama.Fore.RED}警告: 无法导入 prepare_files.py，准备文件功能将不可用。{colorama.Style.RESET_ALL}")
    prepare_files = None

try:
    import del_files
except ImportError:
    print(f"{colorama.Fore.RED}警告: 无法导入 del_files.py，删除中间文件功能将不可用。{colorama.Style.RESET_ALL}")
    del_files = None

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
    显示可用的文件对供用户选择，返回所有文件对的列表
    """
    if not file_pairs:
        print(f"{colorama.Fore.RED}未找到任何可处理的文件对！{colorama.Style.RESET_ALL}")
        return []  # 返回空列表

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
    """使用 subprocess 模式处理单个文件对"""
    print(f"\n正在处理: {os.path.basename(c_file)} -> {os.path.basename(merge_file)}")
    print(f"中文文件: {c_file}")
    print(f"英文文件: {e_file}")

    # 检查文件是否存在
    if not os.path.exists(c_file):
        print(f"{colorama.Fore.RED}错误: 文件不存在 {c_file}{colorama.Style.RESET_ALL}")
        return False

    if not os.path.exists(e_file):
        print(f"{colorama.Fore.RED}错误: 文件不存在 {e_file}{colorama.Style.RESET_ALL}")
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
            print(f"{colorama.Fore.RED}错误:{colorama.Style.RESET_ALL}")
            print(result.stderr)

        if result.returncode == 0:
            print(f"✓ 处理完成: {merge_file}")
            return True
        else:
            print(f"{colorama.Fore.RED}✗ 处理失败: 返回码 {result.returncode}{colorama.Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{colorama.Fore.RED}✗ 执行出错: {e}{colorama.Style.RESET_ALL}")
        return False

def format_single_pair_direct(c_file, e_file, merge_file):
    """直接调用 format.py 函数，避免子进程编码问题"""
    print(f"\n正在处理: {os.path.basename(c_file)} -> {os.path.basename(merge_file)}")
    print(f"中文文件: {c_file}")
    print(f"英文文件: {e_file}")

    # 检查文件是否存在
    if not os.path.exists(c_file):
        print(f"{colorama.Fore.RED}错误: 文件不存在 {c_file}{colorama.Style.RESET_ALL}")
        return False

    if not os.path.exists(e_file):
        print(f"{colorama.Fore.RED}错误: 文件不存在 {e_file}{colorama.Style.RESET_ALL}")
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
        print(f"{colorama.Fore.RED}✗ 无法导入format.py: {e}{colorama.Style.RESET_ALL}")
        print("尝试使用subprocess方式...")
        # 回退到subprocess方式
        return format_single_pair(c_file, e_file, merge_file, "format.py")
    except Exception as e:
        print(f"{colorama.Fore.RED}✗ 执行出错: {e}{colorama.Style.RESET_ALL}")
        return False

def perform_prepare():
    """交互式执行准备文件操作"""
    if prepare_files is None:
        print(f"{colorama.Fore.RED}错误: prepare_files 模块不可用，无法执行准备操作。{colorama.Style.RESET_ALL}")
        return

    print("\n===== 准备文件 =====")
    print("请输入以下目录路径：")
    chinese_dir = input("中文目录 (chinese): ").strip()
    if not chinese_dir:
        print("取消操作。")
        return

    english_dir = input("英文目录 (english): ").strip()
    if not english_dir:
        print("取消操作。")
        return

    output_dir = input("输出目录 (output): ").strip()
    if not output_dir:
        print("取消操作。")
        return

    # 检查目录是否存在
    if not os.path.exists(chinese_dir):
        print(f"{colorama.Fore.RED}错误: 中文目录 {chinese_dir} 不存在{colorama.Style.RESET_ALL}")
        return
    if not os.path.exists(english_dir):
        print(f"{colorama.Fore.RED}错误: 英文目录 {english_dir} 不存在{colorama.Style.RESET_ALL}")
        return

    try:
        prepare_files.prepare_translation_files(chinese_dir, english_dir, output_dir)
        print(f"\n准备完成！文件已输出到: {output_dir}")
        return output_dir
    except Exception as e:
        print(f"{colorama.Fore.RED}准备过程中出错: {e}{colorama.Style.RESET_ALL}")
        return

def run_interactive(directory, mode, format_script):
    """交互式处理主循环"""
    if not os.path.exists(directory):
        print(f"{colorama.Fore.RED}错误: 目录 {directory} 不存在{colorama.Style.RESET_ALL}")
        return

    if mode == 'subprocess' and not os.path.exists(format_script):
        print(f"{colorama.Fore.RED}错误: format.py脚本 {format_script} 不存在{colorama.Style.RESET_ALL}")
        return

    print(f"正在扫描目录: {directory}")
    file_pairs = find_file_pairs(directory)
    all_pairs = display_file_pairs(file_pairs)

    while True:
        # 显示当前状态
        if all_pairs:
            print(f"\n当前有 {len(all_pairs)} 个文件对可用。")
        else:
            print("\n当前没有文件对。请先使用选项0准备文件，然后选项5重新扫描。")

        print(f"当前工作目录: {directory}")
        print(f"当前模式: {mode}")
        print("请选择操作:")
        print("0. 准备文件（运行 prepare_files.py）")
        if all_pairs:
            print("1. 处理单个文件对")
            print("2. 批量处理所有文件对")
            print("3. 按目录批量处理")
        else:
            print("1. (不可用，无文件对)")
            print("2. (不可用，无文件对)")
            print("3. (不可用，无文件对)")
        print("4. 切换执行模式")
        print("5. 重新扫描/切换工作目录")
        print("6. 删除中间文件 (xxxC.rpy / xxxE.rpy)")
        print("7. 退出")

        choice = input("请输入选项 (0-7): ").strip()

        try:
            if choice == '0':
                new_dir = perform_prepare()
                if new_dir:
                    # 询问是否切换到输出目录
                    switch = input(f"是否将工作目录切换到 {new_dir}？(y/n): ").strip().lower()
                    if switch == 'y':
                        directory = new_dir
                        print(f"工作目录已切换到: {directory}")
                    else:
                        print("保持当前工作目录。")
                print("\n准备完成。如果需要处理新生成的文件，请使用选项5重新扫描。")
                continue

            elif choice == '1':
                if not all_pairs:
                    print("当前没有文件对，无法处理。请先执行选项0准备文件，然后选项5重新扫描。")
                    continue
                # 选择单个文件对
                try:
                    selection = input(f"请输入要处理的文件编号 (1-{len(all_pairs)}): ").strip()
                    if not selection:
                        continue

                    index = int(selection) - 1
                    if 0 <= index < len(all_pairs):
                        pair = all_pairs[index]
                        if mode == 'direct':
                            format_single_pair_direct(pair['c_file'], pair['e_file'], pair['merge_file'])
                        else:
                            format_single_pair(pair['c_file'], pair['e_file'], pair['merge_file'], format_script)
                    else:
                        print(f"错误: 编号必须在 1-{len(all_pairs)} 之间")
                except ValueError:
                    print("错误: 请输入有效的数字")

            elif choice == '2':
                if not all_pairs:
                    print("当前没有文件对，无法处理。请先执行选项0准备文件，然后选项5重新扫描。")
                    continue
                # 批量处理所有文件对
                confirm = input(f"确定要批量处理所有 {len(all_pairs)} 个文件对吗？(y/n): ").strip().lower()
                if confirm == 'y':
                    success_count = 0
                    for i, pair in enumerate(all_pairs, 1):
                        print(f"\n[{i}/{len(all_pairs)}] ", end='')
                        if mode == 'direct':
                            if format_single_pair_direct(pair['c_file'], pair['e_file'], pair['merge_file']):
                                success_count += 1
                        else:
                            if format_single_pair(pair['c_file'], pair['e_file'], pair['merge_file'], format_script):
                                success_count += 1
                    print(f"\n批量处理完成！成功: {success_count}/{len(all_pairs)}")

            elif choice == '3':
                if not all_pairs:
                    print("当前没有文件对，无法处理。请先执行选项0准备文件，然后选项5重新扫描。")
                    continue
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
                                    if mode == 'direct':
                                        if format_single_pair_direct(pair['c_file'], pair['e_file'], pair['merge_file']):
                                            success_count += 1
                                    else:
                                        if format_single_pair(pair['c_file'], pair['e_file'], pair['merge_file'], format_script):
                                            success_count += 1
                                print(f"\n目录 {dir_display} 处理完成！成功: {success_count}/{len(dir_pairs)}")
                        else:
                            print(f"错误: 目录编号必须在 1-{len(directories)} 之间")
                except ValueError:
                    print(f"{colorama.Fore.RED}错误: 请输入有效的数字{colorama.Style.RESET_ALL}")

            elif choice == '4':
                # 切换执行模式
                print("\n当前模式:", mode)
                print("1. direct - 直接调用函数（推荐）")
                print("2. subprocess - 使用子进程")
                mode_choice = input("请选择模式 (1-2): ").strip()
                if mode_choice == '1':
                    mode = 'direct'
                    print("已切换到 direct 模式")
                elif mode_choice == '2':
                    mode = 'subprocess'
                    print("已切换到 subprocess 模式")
                else:
                    print("无效选择，保持当前模式")

            elif choice == '5':
                # 重新扫描，并询问是否更改工作目录
                print("\n是否更改工作目录？当前目录: " + directory)
                change_dir = input("更改工作目录？(y/n): ").strip().lower()
                if change_dir == 'y':
                    new_dir = input("请输入新的工作目录路径: ").strip()
                    if os.path.exists(new_dir):
                        directory = new_dir
                        print(f"工作目录已切换到: {directory}")
                    else:
                        print(f"{colorama.Fore.RED}错误: 目录 {new_dir} 不存在，保持原目录。{colorama.Style.RESET_ALL}")
                # 重新扫描
                print("重新扫描目录...")
                file_pairs = find_file_pairs(directory)
                all_pairs = display_file_pairs(file_pairs)
                continue

            elif choice == '6':
                # 删除中间文件
                if del_files is None:
                    print(f"{colorama.Fore.RED}错误: del_files 模块不可用，无法执行删除操作。{colorama.Style.RESET_ALL}")
                    continue
                print("\n===== 删除中间文件 =====")
                deleted = del_files.delete_intermediate_files(directory, confirm=True)
                # 询问是否退出
                while True:
                    exit_choice = input("是否退出程序？(y/n, 默认y): ").strip().lower()
                    if exit_choice in ('y', 'yes', ''):
                        print("再见！")
                        return  # 退出函数，回到主程序结束
                    elif exit_choice in ('n', 'no'):
                        print("返回主菜单。")
                        break
                    else:
                        print("无效输入，请输入 y 或 n。")

            elif choice == '7':
                print("再见！")
                break

            else:
                print("错误: 请输入有效的选项 (0-7)")

        except KeyboardInterrupt:
            print("\n\n用户中断操作")
            break
        except Exception as e:
            print(f"{colorama.Fore.RED}发生错误: {e}{colorama.Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='交互式选择并合并翻译文件')
    parser.add_argument('directory', nargs='?', default='.', help='要扫描的目录路径（默认当前目录）')
    parser.add_argument('--format-script', default='format.py', help='format.py脚本路径（默认当前目录）')
    parser.add_argument('--mode', choices=['direct', 'subprocess'], default='direct',
                        help='执行模式：direct-直接调用函数，subprocess-使用子进程')
    parser.add_argument('--prepare', nargs=3, metavar=('CHINESE_DIR', 'ENGLISH_DIR', 'OUTPUT_DIR'),
                        help='直接执行准备文件操作，然后询问是否进入交互界面')
    parser.add_argument('--delete', nargs='?', const='.', default=None, metavar='DIRECTORY',
                        help='删除工作目录中的中间文件（xxxC.rpy 和 xxxE.rpy），可选指定目录（默认当前目录）')
    parser.add_argument('-y', '--yes', action='store_true', help='删除时跳过确认提示')

    args = parser.parse_args()

    # 处理 --delete 参数
    if args.delete is not None:
        target_dir = args.delete if args.delete != '.' else args.directory  # 如果指定了目录则使用，否则使用位置参数
        # 如果 --delete 未带参数且位置参数存在，则使用位置参数；否则使用当前目录
        if args.delete == '.' and args.directory != '.':
            target_dir = args.directory
        else:
            target_dir = args.delete
        if del_files is None:
            print(f"{colorama.Fore.RED}错误: del_files 模块不可用，无法执行删除操作。{colorama.Style.RESET_ALL}")
            return
        print(f"正在扫描目录: {target_dir}")
        deleted = del_files.delete_intermediate_files(target_dir, confirm=not args.yes)
        print(f"删除完成，共删除 {deleted} 个文件。")
        input("按任意键退出...")
        return

    # 处理 --prepare 参数
    if args.prepare:
        chinese_dir, english_dir, output_dir = args.prepare
        if not os.path.exists(chinese_dir):
            print(f"{colorama.Fore.RED}错误: 中文目录 {chinese_dir} 不存在{colorama.Style.RESET_ALL}")
            return
        if not os.path.exists(english_dir):
            print(f"{colorama.Fore.RED}错误: 英文目录 {english_dir} 不存在{colorama.Style.RESET_ALL}")
            return
        if prepare_files is None:
            print(f"{colorama.Fore.RED}错误: prepare_files 模块不可用，无法执行准备操作。{colorama.Style.RESET_ALL}")
            return

        print("正在准备文件...")
        try:
            prepare_files.prepare_translation_files(chinese_dir, english_dir, output_dir)
            print(f"准备完成！文件已输出到: {output_dir}")
        except Exception as e:
            print(f"{colorama.Fore.RED}准备过程中出错: {e}{colorama.Style.RESET_ALL}")
            return

        # 询问是否进入交互界面
        while True:
            choice = input("是否进入交互界面处理翻译文件？(y/n): ").strip().lower()
            if choice in ('y', 'yes'):
                # 使用输出目录作为新的工作目录，并进入交互
                run_interactive(output_dir, args.mode, args.format_script)
                break
            elif choice in ('n', 'no', ''):
                print("退出程序。")
                break
            else:
                print("无效输入，请输入 y 或 n。")
        return

    # 没有 --prepare 也没有 --delete，直接进入交互
    run_interactive(args.directory, args.mode, args.format_script)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import threading
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk

# ---------- 兼容 PyInstaller 打包 ----------
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容 PyInstaller 打包"""
    if hasattr(sys, '_MEIPASS'):
        # 运行在打包后的 exe 中
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # 运行在开发环境中
        return os.path.join(os.path.dirname(__file__), relative_path)

# 将资源目录添加到 sys.path，以便导入其他模块
sys.path.insert(0, get_resource_path('.'))

# ---------- 导入现有模块 ----------
try:
    from interactive_format import find_file_pairs
    from format import merge_translation_files
    from format_strings import process_strings_translations
    from prepare_files import prepare_translation_files
    from del_files import delete_intermediate_files
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

# ---------- 部署测试示例 ----------
def deploy_test_example(target_dir):
    """将内置的 test 目录复制到 target_dir"""
    src_test = get_resource_path('test')
    if not os.path.exists(src_test):
        return False, "内置测试文件不存在，请确保打包时包含了 test 目录"
    try:
        # 如果目标目录已存在，先删除
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(src_test, target_dir)
        return True, f"已部署测试示例到: {target_dir}"
    except Exception as e:
        return False, f"部署失败: {e}"

# ---------- 彩色输出重定向 ----------
class StdoutRedirector:
    """重定向 stdout 到 GUI 日志控件，并解析 ANSI 颜色代码，保留换行符"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        # 配置颜色标签
        text_widget.tag_configure("green", foreground="green")
        text_widget.tag_configure("red", foreground="red")
        text_widget.tag_configure("yellow", foreground="orange")
        text_widget.tag_configure("blue", foreground="blue")
        text_widget.tag_configure("cyan", foreground="cyan")
        text_widget.tag_configure("magenta", foreground="magenta")
        self.ansi_pattern = re.compile(r'\033\[[0-9;]*m')

    def write(self, message):
        if not message:
            return
        self.text_widget.after(0, lambda: self._append(message))

    def _append(self, message):
        self.text_widget.config(state='normal')
        pos = 0
        current_tag = None
        for match in self.ansi_pattern.finditer(message):
            start, end = match.span()
            if start > pos:
                text = message[pos:start]
                if current_tag:
                    self.text_widget.insert(tk.END, text, current_tag)
                else:
                    self.text_widget.insert(tk.END, text)
            code = match.group()
            if code == '\033[0m':
                current_tag = None
            elif code == '\033[32m':
                current_tag = 'green'
            elif code == '\033[31m':
                current_tag = 'red'
            elif code == '\033[33m':
                current_tag = 'yellow'
            elif code == '\033[34m':
                current_tag = 'blue'
            elif code == '\033[36m':
                current_tag = 'cyan'
            elif code == '\033[35m':
                current_tag = 'magenta'
            pos = end
        if pos < len(message):
            text = message[pos:]
            if current_tag:
                self.text_widget.insert(tk.END, text, current_tag)
            else:
                self.text_widget.insert(tk.END, text)
        self.text_widget.config(state='disabled')
        self.text_widget.see(tk.END)

    def flush(self):
        pass

# ---------- GUI 主程序 ----------
class RenpyTranslationGUI:
    def __init__(self, root):
        self.root = root
        root.title("RenPy 翻译工具集")
        root.geometry("900x700")
        root.resizable(True, True)

        self.work_dir = tk.StringVar(value=os.getcwd())
        self.mode = tk.StringVar(value="direct")
        self.file_pairs = []
        self.all_pairs = []
        self.current_mode = "direct"
        self.task_running = False

        self.create_widgets()
        self.refresh_file_list()

    def create_widgets(self):
        # 顶部：工作目录选择
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(top_frame, text="工作目录:").pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.work_dir, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="浏览", command=self.select_work_dir).pack(side=tk.LEFT)
        tk.Button(top_frame, text="重新扫描", command=self.refresh_file_list).pack(side=tk.LEFT, padx=5)

        # 模式选择
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(mode_frame, text="执行模式:").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="direct (推荐)", variable=self.mode, value="direct",
                       command=self.change_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="subprocess", variable=self.mode, value="subprocess",
                       command=self.change_mode).pack(side=tk.LEFT)

        # 文件对列表
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(list_frame, text="文件对列表（双击单个处理）").pack(anchor=tk.W)
        self.tree = ttk.Treeview(list_frame, columns=("name", "path"), show="tree headings")
        self.tree.heading("#0", text="索引")
        self.tree.heading("name", text="文件名")
        self.tree.heading("path", text="相对路径")
        self.tree.column("#0", width=50)
        self.tree.column("name", width=200)
        self.tree.column("path", width=300)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", self.on_double_click)

        # 按钮区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.buttons = []
        btn_texts = [
            ("准备文件", self.prepare_files),
            ("处理选中文件", self.process_selected),
            ("批量处理全部", self.process_all),
            ("按目录批量", self.process_by_dir),
            ("切换工作目录", self.change_work_dir),
            ("删除中间文件", self.delete_files),
            ("部署测试示例", self.deploy_test_example),
        ]
        for text, cmd in btn_texts:
            btn = tk.Button(btn_frame, text=text, command=cmd, width=15)
            btn.pack(side=tk.LEFT, padx=2)
            self.buttons.append(btn)

        # 日志区域
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(log_frame, text="运行日志:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state='disabled')

    def log(self, msg):
        """直接写入日志（无颜色）"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def select_work_dir(self):
        d = filedialog.askdirectory(initialdir=self.work_dir.get())
        if d:
            self.work_dir.set(d)
            self.refresh_file_list()

    def change_work_dir(self):
        new_dir = filedialog.askdirectory(initialdir=self.work_dir.get())
        if new_dir:
            self.work_dir.set(new_dir)
            self.refresh_file_list()
            self.log(f"工作目录已切换至: {new_dir}")

    def refresh_file_list(self):
        directory = self.work_dir.get()
        if not os.path.exists(directory):
            self.log(f"错误: 目录不存在 {directory}")
            return
        self.log(f"正在扫描目录: {directory}")
        self.file_pairs = find_file_pairs(directory)
        self.all_pairs = self.file_pairs
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not self.all_pairs:
            self.log("未找到任何文件对")
            return
        for idx, pair in enumerate(self.all_pairs, start=1):
            self.tree.insert("", tk.END, text=str(idx), values=(pair['name'], pair['rel_path'] if pair['rel_path'] else "根目录"))
        self.log(f"找到 {len(self.all_pairs)} 个文件对")

    def on_double_click(self, event):
        self.process_selected()

    def process_selected(self):
        selected = self.tree.selection()
        if not selected:
            self.log("请先选中一个文件对")
            return
        idx = int(self.tree.item(selected[0])['text']) - 1
        if 0 <= idx < len(self.all_pairs):
            pair = self.all_pairs[idx]
            self.log(f"开始处理: {pair['name']}")
            self.run_task(self._process_one, pair)

    def process_all(self):
        if not self.all_pairs:
            self.log("没有文件对可处理")
            return
        if messagebox.askyesno("确认", f"确定要批量处理全部 {len(self.all_pairs)} 个文件对吗？"):
            self.log(f"开始批量处理 {len(self.all_pairs)} 个文件...")
            self.run_task(self._process_all)

    def process_by_dir(self):
        if not self.all_pairs:
            self.log("没有文件对可处理")
            return
        dirs = sorted(set(p['rel_path'] for p in self.all_pairs))
        if not dirs:
            self.log("没有发现子目录")
            return
        dlg = tk.Toplevel(self.root)
        dlg.title("选择目录")
        dlg.geometry("350x300")
        dlg.grab_set()
        dlg.resizable(False, False)

        tk.Label(dlg, text="请选择目录（双击或点击确定）:").pack(pady=5)
        listbox = tk.Listbox(dlg, height=12)
        for d in dirs:
            listbox.insert(tk.END, d if d else "根目录")
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 双击处理
        def on_listbox_double_click(event):
            sel = listbox.curselection()
            if sel:
                selected_dir = dirs[sel[0]]
                dlg.destroy()
                dir_pairs = [p for p in self.all_pairs if p['rel_path'] == selected_dir]
                if messagebox.askyesno("确认", f"确定要批量处理目录 '{selected_dir if selected_dir else '根目录'}' 下的 {len(dir_pairs)} 个文件吗？"):
                    self.log(f"开始批量处理目录 {selected_dir if selected_dir else '根目录'}, 共 {len(dir_pairs)} 个文件")
                    self.run_task(self._process_list, dir_pairs)
        listbox.bind("<Double-1>", on_listbox_double_click)

        # 确定按钮
        def confirm():
            sel = listbox.curselection()
            if sel:
                selected_dir = dirs[sel[0]]
                dlg.destroy()
                dir_pairs = [p for p in self.all_pairs if p['rel_path'] == selected_dir]
                if messagebox.askyesno("确认", f"确定要批量处理目录 '{selected_dir if selected_dir else '根目录'}' 下的 {len(dir_pairs)} 个文件吗？"):
                    self.log(f"开始批量处理目录 {selected_dir if selected_dir else '根目录'}, 共 {len(dir_pairs)} 个文件")
                    self.run_task(self._process_list, dir_pairs)
            else:
                messagebox.showwarning("提示", "请先选择一个目录")

        btn_frame = tk.Frame(dlg)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="确定", command=confirm, width=10).pack(side=tk.LEFT, padx=5)

    def change_mode(self):
        new_mode = self.mode.get()
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            self.log(f"执行模式已切换至: {self.current_mode}")

    def prepare_files(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("准备文件")
        dlg.geometry("450x250")
        dlg.grab_set()
        tk.Label(dlg, text="原文目录:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        chinese_var = tk.StringVar()
        tk.Entry(dlg, textvariable=chinese_var, width=40).grid(row=0, column=1, padx=5)
        tk.Label(dlg, text="参考目录:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        english_var = tk.StringVar()
        tk.Entry(dlg, textvariable=english_var, width=40).grid(row=1, column=1)
        tk.Label(dlg, text="输出目录:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        output_var = tk.StringVar()
        tk.Entry(dlg, textvariable=output_var, width=40).grid(row=2, column=1)

        def browse(entry_var):
            d = filedialog.askdirectory()
            if d:
                entry_var.set(d)
                dlg.focus_set()   # 重新聚焦到 dlg
        tk.Button(dlg, text="浏览", command=lambda: browse(chinese_var)).grid(row=0, column=2)
        tk.Button(dlg, text="浏览", command=lambda: browse(english_var)).grid(row=1, column=2)
        tk.Button(dlg, text="浏览", command=lambda: browse(output_var)).grid(row=2, column=2)

        def do_prepare():
            ch = chinese_var.get()
            en = english_var.get()
            out = output_var.get()
            if not ch or not en or not out:
                messagebox.showerror("错误", "请填写所有目录")
                return
            if not os.path.exists(ch):
                messagebox.showerror("错误", f"原文目录不存在: {ch}")
                return
            if not os.path.exists(en):
                messagebox.showerror("错误", f"参考目录不存在: {en}")
                return
            dlg.destroy()
            self.log("开始准备文件...")
            self.run_task(self._prepare, ch, en, out)

        tk.Button(dlg, text="开始", command=do_prepare).grid(row=3, column=0, columnspan=3, pady=10)

    def delete_files(self):
        if not self.work_dir.get():
            self.log("请先设置工作目录")
            return
        if messagebox.askyesno("确认删除", f"确定要删除工作目录 '{self.work_dir.get()}' 下的所有中间文件 (xxxC.rpy / xxxE.rpy) 吗？\n注意：仅删除存在对应合并文件的中间文件。"):
            self.log("开始删除中间文件...")
            self.run_task(self._delete)

    def deploy_test_example(self):
        """部署测试示例文件"""
        target_base = filedialog.askdirectory(title="选择部署目标目录（将在其中创建 test_example 文件夹）")
        if not target_base:
            return
        target_dir = os.path.join(target_base, "test_example")
        success, msg = deploy_test_example(target_dir)
        messagebox.showinfo("部署结果", msg)
        if success:
            if messagebox.askyesno("切换工作目录", f"是否将工作目录切换到 {target_dir}？"):
                self.work_dir.set(target_dir)
                self.refresh_file_list()

    # ---------- 后台任务 ----------
    def set_buttons_state(self, state):
        for btn in self.buttons:
            btn.config(state=state)

    def run_task(self, func, *args):
        if self.task_running:
            self.log("已有任务正在运行，请稍后再试")
            return
        self.task_running = True
        self.set_buttons_state(tk.DISABLED)

        old_stdout = sys.stdout
        redirector = StdoutRedirector(self.log_text)
        sys.stdout = redirector

        def wrapper():
            try:
                func(*args)
            except Exception as e:
                print(f"任务执行出错: {e}")
            finally:
                sys.stdout = old_stdout
                self.task_running = False
                self.set_buttons_state(tk.NORMAL)
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()

    def _process_one(self, pair):
        c_file = pair['c_file']
        e_file = pair['e_file']
        merge_file = pair['merge_file']
        print(f"处理: {pair['name']}")
        if self.current_mode == 'direct':
            merge_translation_files(e_file, c_file, merge_file)
            process_strings_translations(merge_file, c_file, merge_file)
        else:
            # subprocess 模式：调用外部脚本，并捕获输出到当前 stdout（已重定向到 GUI）
            format_script = os.path.join(os.path.dirname(__file__), "format.py")
            strings_script = os.path.join(os.path.dirname(__file__), "format_strings.py")
            # 先运行 format.py
            result1 = subprocess.run(["python", format_script, e_file, c_file, merge_file],
                                     capture_output=True, text=True, encoding='utf-8')
            if result1.stdout:
                print(result1.stdout)
            if result1.stderr:
                print(result1.stderr, file=sys.stderr)
            # 再运行 format_strings.py
            result2 = subprocess.run(["python", strings_script, merge_file, c_file, merge_file],
                                     capture_output=True, text=True, encoding='utf-8')
            if result2.stdout:
                print(result2.stdout)
            if result2.stderr:
                print(result2.stderr, file=sys.stderr)
        print(f"完成: {merge_file}")

    def _process_all(self):
        for pair in self.all_pairs:
            self._process_one(pair)
        print("批量处理全部完成")

    def _process_list(self, pairs):
        for pair in pairs:
            self._process_one(pair)
        print("目录批量处理完成")

    def _prepare(self, chinese_dir, english_dir, output_dir):
        prepare_translation_files(chinese_dir, english_dir, output_dir)
        print(f"准备完成，输出目录: {output_dir}")
        if messagebox.askyesno("切换工作目录", f"是否将工作目录切换到 {output_dir}？"):
            self.work_dir.set(output_dir)
            self.refresh_file_list()

    def _delete(self):
        deleted = delete_intermediate_files(self.work_dir.get(), confirm=False)
        print(f"删除完成，共删除 {deleted} 个文件。")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenpyTranslationGUI(root)
    root.mainloop()
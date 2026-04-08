# RenPy 翻译工具集

---

**提示**：首次使用请先用内置的“部署测试示例”功能获取测试文件，确认无误后再处理真实项目。

---

## 📋 概述

本工具集用于自动化处理 RenPy 游戏翻译文件，通过唯一标识符精确匹配中文翻译内容，并将其合并到 SDK 生成的英文参考文件中。支持批量处理和交互式操作。现已集成文件准备、中间文件清理以及字符串翻译块处理功能，只需一个脚本即可完成从准备到合并再到清理的全流程。  

妈妈再也不用担心每次游戏作者更新后，我搞不清哪些文本变了、哪些汉化要重翻了！只需把旧版 `tl/chinese` 和新版 SDK 翻译往根目录一丢，so easy!  

PS: 本项目代码全部由 AI 生成。

---

## 📁 项目结构

```bash
renpy_translate_format/
├── format.py              # 核心合并脚本（普通翻译）
├── format_strings.py      # 字符串翻译合并脚本
├── prepare_files.py       # 准备文件
├── del_files.py           # 删除中间文件
├── interactive_format.py  # 命令行交互式主脚本
├── gui_tkinter.py         # GUI 图形界面主脚本
├── run.bat                # 命令行版一键启动脚本
├── run_gui.bat            # GUI 版一键启动脚本
├── requirements.txt       # Python 依赖列表
├── images/                # 截图（Options.webp, GUI.webp）
├── test/                  # 测试样例目录（源码版）
├── chinese/               # 你的中文翻译目录（需手动放置）
├── english/               # 你的 SDK 英文目录（需手动放置）
└── format/                # 工作目录（脚本生成）
```

---

## 🚀 快速开始

### 方式一：使用预编译的 exe（推荐普通用户）

1. 从 [Releases](https://github.com/Edward1949/renpy_translate_format/releases) 下载 `RenPyTranslateFormatGUI.exe`。
2. 双击运行，无需安装 Python。
3. 点击 **“部署测试示例”**，选择任意目录（如桌面），自动创建 `test_example` 文件夹。
4. 部署完成后，按提示**自动准备文件**，之后点击“重新扫描” → “批量处理全部” → 观察日志。
5. 处理完毕可点击“删除中间文件”清理。

> 详细操作请参考下方的 **完整翻译工作流** 章节。

### 方式二：源码运行

#### 1. 安装 Python
- **Windows**：从 [python.org](https://www.python.org/downloads/) 下载 Python 3.11+，**安装时勾选 “Add Python to PATH”**。
- **macOS / Linux**：使用包管理器安装（如 `brew install python` 或 `sudo apt install python3`）。

#### 2. 下载本工具
```bash
git clone https://github.com/Edward1949/renpy_translate_format.git
cd renpy_translate_format
```

#### 3. 准备你的翻译文件
- 将旧版汉化文件（如 `tl/chinese`）复制到根目录下的 `chinese/` 文件夹。
- 将新版 SDK 生成的英文翻译（如 `tl/english`）复制到根目录下的 `english/` 文件夹。

#### 4. 安装依赖（仅首次）
```bash
pip install -r requirements.txt
```

#### 5. 运行
- **命令行交互界面**：双击 `run.bat` 或执行 `python interactive_format.py`
- **图形界面**：双击 `run_gui.bat` 或执行 `python gui_tkinter.py`

---

## 🛠️ 脚本说明

| 脚本 | 功能 |
|------|------|
| `format.py` | 合并普通翻译（通过唯一标识符匹配） |
| `format_strings.py` | 合并字符串翻译块（`translate ... strings:`） |
| `prepare_files.py` | 复制中英文文件并重命名为 `xxxC.rpy` / `xxxE.rpy`，同时复制非翻译资源（图片、字体等） |
| `del_files.py` | 删除中间文件（`xxxC.rpy` / `xxxE.rpy`），前提是存在对应的 `xxx.rpy` |
| `interactive_format.py` | 命令行文本菜单，集成全部功能，支持 `direct` / `subprocess` 模式 |
| `gui_tkinter.py` | 图形界面（Tkinter），封装所有命令行功能，适合鼠标操作 |

**GUI 界面预览**：  
![GUI](https://raw.githubusercontent.com/Edward1949/renpy_translate_format/main/images/GUI.webp)

**命令行界面选项**：
```
0. 准备文件
1. 处理单个文件对
2. 批量处理所有文件对
3. 按目录批量处理
4. 切换执行模式
5. 重新扫描/切换工作目录
6. 删除中间文件
7. 退出
```

**命令行参数**（适用于 `interactive_format.py`）：
- `directory`：扫描目录（默认当前目录）
- `--mode direct/subprocess`：执行模式
- `--prepare CHN ENG OUT`：直接准备文件
- `--delete [DIR]`：直接删除中间文件
- `-y`：跳过确认

**界面预览**

![Options](https://raw.githubusercontent.com/Edward1949/renpy_translate_format/main/images/Options.webp)

---

## 🔧 工作原理

### 普通翻译块处理
- **匹配**：通过 `translate xxx 标识符:` 中的唯一标识符匹配中英文块。
- **提取**：从中文文件中提取包含中文字符的 `"文本"` 或 `角色名 "文本"`。
- **合并**：在英文参考文件中找到对应的空行（`""` 或 `角色名 ""`），填入中文翻译。

### 字符串翻译块处理
- **提取**：从中文文件的 `translate chinese strings:` 块中解析 `old "..."` 和 `new "..."` 对。
- **合并**：在英文参考文件的字符串块中，将匹配到的 `old` 对应的 `new` 行替换为中文翻译。
- **追加**：如果中文中存在英文参考中没有的 `old` 条目（黄色警告），会自动追加到输出文件末尾，不会丢失。
- **缺失提示**：如果英文参考中存在而中文没有的条目（红色警告），会保留空的 `new ""`，提醒译者补全。

### 颜色提示
- **绿色**：成功匹配并替换
- **黄色**：中文独有条目（已自动追加）
- **红色**：英文独有条目（需要手动补全翻译）
### 示例标识符
```renpy
# 普通标识符
translate xxxx sample_start_a1b2c3d4:
# 字符串翻译块
translate chinese strings:

    old "ABC"# 字符串标识符
    new ""

```
---

## 📝 完整翻译工作流（从旧版汉化到新版翻译）

以下流程适用于游戏更新后，将旧版汉化迁移到新版，并补全新增文本。

### 第一步：提取旧版汉化文件
- 找到旧版游戏的 `tl/chinese` 目录（或 `tl/schinese`），将其**复制**到本工具根目录下的 `chinese/` 文件夹。

### 第二步：使用 SDK 生成新版翻译文件
- 打开新版游戏，使用 RenPy SDK 的 **“生成翻译文件”**（Generate Translations）。
- **务必勾选** “为翻译生成空字符串”（Generate empty strings for translations）。
- 语言填写建议和旧版保持一致（也可填其他，但后续需替换语言标识）。
- 生成后得到 `tl/english` 目录，将其**复制**到本工具根目录下的 `english/` 文件夹。
- **PS:** **GUI 用户**可以不用复制，在准备文件输入路径即可。
![sdk](https://raw.githubusercontent.com/Edward1949/renpy_translate_format/main/images/RenPySDK.webp)

### 第三步：运行工具合并翻译
- **GUI 用户**：双击 exe → 点击“准备文件”，分别选择 `chinese`、`english`、`format` → 点击“重新扫描” → 点击“批量处理全部”。
![prepare](https://raw.githubusercontent.com/Edward1949/renpy_translate_format/main/images/prepare_log.webp)
- **命令行用户**：执行 `python interactive_format.py --prepare ./chinese ./english ./format`，然后 `python interactive_format.py format` 并选择 `2`。
- 观察日志中的**红色条目**（即新版新增的未翻译文本）。
![log](https://raw.githubusercontent.com/Edward1949/renpy_translate_format/main/images/formaat_log.webp)
### 第四步：在 VS Code 中补全红色标记的翻译
- 打开 VS Code，将 `format/` 文件夹添加到工作区。
- 根据日志中的红色标识符（如 `old "..."`），在对应的 `xxx.rpy` 文件中找到 `new ""` 行，参考上下文补全中文翻译。
- 可同时参考 `xxxC.rpy`（旧版翻译）和 `xxxE.rpy`（新版英文原文）。
![vscode](https://raw.githubusercontent.com/Edward1949/renpy_translate_format/main/images/vscode.webp)
### 第五步：处理语言标识符（如果需要）
- 如果 SDK 生成的语言不是 `chinese`（例如是 `english`），而游戏需要 `chinese`，请在 VS Code 中**全局替换**：
  - 搜索 `translate english` → 替换为 `translate chinese`
  - 搜索 `translate english strings:` → 替换为 `translate chinese strings:`

### 第六步：清理中间文件，得到最终汉化包
- 在工具中点击 **“删除中间文件”**（或执行 `python interactive_format.py format --delete --yes`）。
- 此时 `format/` 文件夹中仅剩 `xxx.rpy` 文件及复制的资源文件。
- 将此文件夹**重命名**为游戏识别的语言名（如 `tl/chinese`），放回游戏目录即可。

---

## 📊 文件命名规则（工作目录 `format/` 内）

| 文件类型 | 命名规则 | 说明 |
|---------|---------|------|
| 中文文件 | `xxxC.rpy` | 原始中文翻译 |
| 英文文件 | `xxxE.rpy` | SDK 生成的英文参考 |
| 合并文件 | `xxx.rpy` | 最终输出（包含普通翻译和字符串翻译） |

---

## ⚠️ 注意事项

1. **目录结构一致性**：`chinese/` 和 `english/` 内部目录结构必须完全相同。
2. **编码**：所有文件使用 UTF-8 编码。
3. **备份**：处理前建议备份原始文件。
4. **标识符匹配**：确保中英文文件的 `translate` 标识符完全一致。
5. **删除安全**：`del_files.py` 仅删除存在对应 `xxx.rpy` 的中间文件，不会误删未完成合并的文件。
6. **字符串块位置**：每个 `.rpy` 文件中最多只有一个 `translate ... strings:` 块，且建议位于文件末尾（符合 RenPy 官方生成规则）。

---

## 🔍 常见问题

### Q1: 如何处理只有中文或只有英文的文件？
**A:** `prepare_files.py` 会将其直接复制到工作目录（保留原文件名），便于手动处理。

### Q2: 为什么有些翻译没有成功合并？
**A:** 可能原因：标识符不匹配、翻译内容不含中文字符、参考文件中没有对应的空对话行、字符串块中的 `old` 未完全匹配。

### Q3: 如何切换执行模式？
**A:** 命令行界面选 `4`；GUI 中直接通过单选按钮切换。

### Q4: 处理过程中出现编码错误怎么办？
**A:** 确保所有文件为 UTF-8 编码；使用 `direct` 模式（默认）；检查系统默认编码。

### Q5: 删除中间文件有什么风险？
**A:** 脚本会检查是否存在对应的 `xxx.rpy`，不会误删未完成合并的文件。建议在确认合并无误后执行。

### Q6: 准备文件后为什么没有文件对？
**A:** 可能原因：未重新扫描、输出目录错误、只有单语言文件、目录结构不一致。请检查后重试。

---

## 🐛 已知 Bug

1. **控制台输出中的 `未找到翻译的标识符: ['strings']`**  
   - 原因：`format.py` 的正则匹配将整个 `translate ... strings:` 块误判为无翻译标识符。  
   - 影响：仅产生无关警告，不影响实际翻译。  
   - 状态：可忽略，后续版本可能修复。

2. **subprocess 模式下日志颜色丢失**  
   - 原因：子进程输出未通过 `colorama` 着色。  
   - 影响：GUI 日志区域无法显示颜色标记。  
   - 临时解决：使用默认的 `direct` 模式（颜色正常）。  
   - 状态：待修复。

---

**提示**：首次使用建议先用内置测试示例熟悉流程。如果觉得工具实用，欢迎给项目一个 ⭐ Star！

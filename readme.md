以下是修改后的 README，整合了命令行工具和 GUI 图形界面的说明，并补充了相关启动方式、界面特点等内容。

```markdown
# RenPy 翻译工具集

---

**提示**：首次使用先用 `test/` 目录中的示例文件进行测试，确认无误后再处理真实项目。

---

## 📋 概述

本工具集用于自动化处理 RenPy 游戏翻译文件，通过唯一标识符精确匹配中文翻译内容，并将其合并到 SDK 生成的英文参考文件中。支持批量处理和交互式操作。现已集成文件准备、中间文件清理以及字符串翻译块处理功能，只需一个脚本即可完成从准备到合并再到清理的全流程。  
妈妈再也不用担心每次游戏作者更新后，我搞不清哪些文本变了、哪些汉化要重翻了！只需把旧版 `tl/chinese` 和新版 SDK 翻译往根目录一丢，so easy!  
PS: 本项目代码全部由 AI 生成。

## 📁 项目结构

```bash
renpy_translate_format/
├── format.py              # 核心合并脚本
├── format_strings.py      # 字符串翻译合并脚本
├── prepare_files.py       # 准备文件
├── del_files.py           # 删除中间文件
├── interactive_format.py  # 命令行交互式处理主脚本
├── gui_tkinter.py         # GUI 图形界面主脚本
├── run.bat                # 命令行版一键启动脚本
├── run_gui.bat            # GUI 版一键启动脚本
├── requirements.txt       # Python 依赖列表
├── images/Optins.webp     # 图片（界面截图）
├── test/                  # 测试样例目录
│   ├── chinese/           # 示例中文翻译
│   │   └── scripts/
│   │       └── sample.rpy
│   └── english/           # 示例 SDK 英文文件
│       └── scripts/
│           └── sample.rpy
├── chinese/               # 你自己的中文翻译目录（需手动放置）
├── english/               # 你自己的 SDK 英文目录（需手动放置）
└── format/                # 工作目录
```

## 🚀 快速开始

### 1. 安装 Python
- **Windows 用户**：从 [python.org](https://www.python.org/downloads/) 下载 Python 3.11 或更高版本。  
  **安装时务必勾选 “Add Python to PATH”**。  
- **macOS / Linux 用户**：通常系统已自带 Python，若无则使用包管理器安装（如 `brew install python` 或 `sudo apt install python3`）。

### 2. 下载本工具
- 直接下载 ZIP 包并解压，或使用 Git 克隆：  
  ```bash
  git clone https://github.com/Edward1949/renpy_translate_format.git
  cd renpy_translate_format
  ```

### 3. 准备你的翻译文件
- 将旧版汉化文件（例如 `tl/chinese` 目录）整体复制到工具根目录下的 `chinese/` 文件夹中。  
- 将新版 SDK 生成的英文翻译（例如 `tl/english` 目录）整体复制到工具根目录下的 `english/` 文件夹中。  


### 4. 选择你喜欢的使用方式

#### 🖥️ 命令行交互式界面（适合习惯键盘操作的用户）
- 双击 `run.bat` 启动，或手动执行：
  ```bash
  python interactive_format.py
  ```
- 根据菜单提示输入数字选择操作（0~7），支持准备文件、批量合并、删除中间文件等。

#### 🎨 图形用户界面（GUI，适合鼠标操作，更直观）
- 双击 `run_gui.bat` 启动，或手动执行：
  ```bash
  python gui_tkinter.py
  ```
- 界面包含：
  - 工作目录选择与文件对列表（双击可直接处理单个文件）
  - 功能按钮（准备文件、处理选中、批量处理、按目录批量、切换工作目录、删除中间文件）
  - 实时彩色日志输出（保留控制台中的颜色信息）
  - 日志区域只读但可选中复制
- 所有操作均调用底层脚本，与命令行版本功能完全一致。

### 5. 手动运行（所有平台）
```bash
# 安装依赖（仅首次需要）
pip install -r requirements.txt

# 准备文件（可选，也可在交互界面或 GUI 中执行）
python interactive_format.py --prepare ./chinese ./english ./format

# 启动命令行交互界面
python interactive_format.py format

# 或启动 GUI 图形界面
python gui_tkinter.py
```

## 🛠️ 脚本说明

### 核心脚本（命令行与 GUI 共用）

#### format.py（核心合并脚本）
**功能**：将原文翻译内容合并到参考 RenPy 文件中，通过唯一标识符精确匹配。

**使用方式**：
```bash
python format.py <参考文件> <原文文件> <输出文件>
```

**参数说明**：
- `参考文件`：SDK 输出的英文参考文件（xxxE.rpy）
- `原文文件`：包含中文翻译的原始文件（xxxC.rpy）
- `输出文件`：合并后的输出文件（xxx.rpy）

**处理逻辑**：
1. 提取原文文件中的翻译内容（以唯一标识符为键）
2. 处理参考文件，将原文翻译内容填入空对话行
3. 支持角色名和表情标签的格式

#### format_strings.py（字符串翻译合并脚本）
**功能**：处理 RenPy 游戏中的字符串翻译块（`translate ... strings:`），将原文中的 `new` 行内容合并到 SDK 生成的参考文件中。

**使用方式**：
```bash
python format_strings.py <参考文件> <原文文件> <输出文件>
```

**处理逻辑**：
- 从原文文件中定位 `translate ... strings:` 块
- 提取 `old` → `new` 的映射
- 在参考文件的字符串块中查找对应的 `old` 行，并替换其后的 `new` 行
- 保留缩进、空行和注释，若找不到对应翻译则保留原 `new` 并记录缺失

**集成说明**：在 `interactive_format.py` 中，当完成普通翻译合并后，会自动调用此脚本处理字符串翻译，无需用户额外操作。

#### prepare_files.py（文件准备脚本，可选）
**功能**：复制并重命名 chinese 和 english 文件到工作目录，同时复制所有非翻译资源（图片、字体等）。

**处理规则**：
- 中英文都有的文件 → 分别复制为 `xxxC.rpy` 和 `xxxE.rpy`，并创建空的 `xxx.rpy`
- 只有中文或只有英文的文件 → 保留原文件名直接复制
- 所有非 `.rpy`、`.rpyc` 的文件（如图片、字体、音频）也会被复制到输出目录的对应位置

#### del_files.py（删除中间文件脚本，可选）
**功能**：删除工作目录中的中间文件（`xxxC.rpy` 和 `xxxE.rpy`），前提是存在对应的合并文件 `xxx.rpy`。

**使用方式**：
```bash
python del_files.py [目录] [-y]
```

**安全机制**：仅删除那些有对应 `xxx.rpy` 文件的中间文件，不会误删未完成合并的文件。
#### interactive_format.py（命令行交互式主脚本）
**功能**：提供文本菜单，集成全部功能。支持 `direct` 和 `subprocess` 两种执行模式。

#### gui_tkinter.py（图形界面主脚本）
**功能**：基于 Tkinter 的图形界面，封装了所有命令行功能，适合不熟悉命令行的用户。  
**界面预览**：  
![Options](https://raw.githubusercontent.com/Edward1949/renpy_translate_format/main/images/Options.webp)
```
0. 准备文件（运行 prepare_files.py）
1. 处理单个文件对
2. 批量处理所有文件对
3. 按目录批量处理
4. 切换执行模式
5. 重新扫描/切换工作目录
6. 删除中间文件 (xxxC.rpy / xxxE.rpy)
7. 退出
```
**命令行参数**：
- `directory`：要扫描的目录路径（默认当前目录）
- `--format-script`：指定 format.py 脚本路径（默认当前目录）
- `--mode`：执行模式，可选 `direct`（直接调用函数）或 `subprocess`（子进程），默认 `direct`
- `--prepare CHINESE_DIR ENGLISH_DIR OUTPUT_DIR`：直接执行文件准备操作，完成后可选择是否进入交互界面
- `--delete [DIRECTORY]`：直接执行删除中间文件操作，完成后退出。若未指定目录，则使用位置参数 `directory` 或当前目录
- `-y, --yes`：与 `--delete` 配合使用，跳过确认提示

**执行模式**：
- `direct` 模式：直接调用 format.py 和 format_strings.py 的函数（推荐）
- `subprocess` 模式：通过子进程调用

## 🔧 工作原理

### 普通翻译标识符匹配
工具通过 RenPy 的 `translate` 块中的唯一标识符进行精确匹配：

```renpy
# 示例标识符
translate xxxx sample_start_a1b2c3d4:
```

### 字符串翻译块处理
- **提取**：从中文文件中的 `translate chinese strings:` 块提取 `old` 和 `new` 对
- **合并**：在英文文件（参考文件）中找到相同 `old` 的行，将其对应的 `new` 内容替换为中文翻译
- **安全机制**：仅替换 `new` 行，保留其他格式；若缺少对应翻译则保持原样并输出警告

### 翻译提取（普通对话）
从原文文件提取包含中文字符的对话内容：
- 支持 `"中文文本"`
- 支持 `角色名 "中文文本"`
- 临时支持 `"..."` 和 `"…"`

### 合并过程（普通对话）
1. **查找空对话行**：在参考文件中找到 `""` 或 `角色名 ""` 的行
2. **标识符匹配**：通过当前 translate 块的标识符查找对应翻译
3. **内容填充**：用中文翻译替换空引号
4. **保留格式**：保持原有缩进和角色名格式

## 📊 文件命名规则

在工作目录 (`format/`) 中：
| 文件类型 | 命名规则 | 说明 |
|---------|---------|------|
| 中文文件 | `xxxC.rpy` | 原始中文翻译 |
| 英文文件 | `xxxE.rpy` | SDK生成的英文参考 |
| 合并文件 | `xxx.rpy` | 合并后的输出 |

## ⚠️ 注意事项

1. **目录结构一致性**：确保 `chinese/` 和 `english/` 的目录结构完全相同
2. **编码问题**：所有文件均使用 UTF-8 编码
3. **临时功能**：`"..."` 和 `"…"` 的处理为临时支持，可根据需要删除相关代码
4. **备份建议**：处理前建议备份原始文件
5. **标识符匹配**：确保中英文文件的 translate 标识符完全一致
6. **删除安全**：`del_files.py` 仅删除那些已有对应合并文件的中间文件，不会误删未完成合并的文件
7. **字符串翻译块**：确保每个 `.rpy` 文件中最多只有一个 `translate ... strings:` 块，且位于文件末尾（符合 RenPy 官方生成规则）

## 🔍 常见问题

### Q1: 如何处理只有中文或只有英文的文件？
A: `prepare_files.py` 会统计并显示这些文件，并将它们直接复制到工作目录（保留原文件名），便于手动处理。

### Q2: 为什么有些翻译没有成功合并？
A: 可能原因：
- 标识符不匹配
- 翻译内容不包含中文字符
- 参考文件中没有对应的空对话行
- 字符串翻译块中的 `old` 字符串未找到完全匹配

### Q3: 如何切换执行模式？
A: 在 `interactive_format.py` 界面中选择选项 4，然后选择模式：
- `1` 切换到 direct 模式
- `2` 切换到 subprocess 模式
在 GUI 中可直接通过单选按钮切换。


### Q4: 处理过程中出现编码错误怎么办？
A: 尝试以下方法：
1. 确保所有文件使用 UTF-8 编码
2. 使用 `direct` 模式避免 subprocess 编码问题
3. 检查系统默认编码设置

### Q5: 删除中间文件有什么风险？
A: 删除脚本会先检查是否存在对应的合并文件 `xxx.rpy`，若不存在则跳过不删除。因此不会误删未完成合并的中间文件。建议在确认所有合并文件都已生成且内容正确并不需要旧翻译或原文参考后再执行删除。

### Q6: 准备文件后为什么没有文件对？
A: 可能原因及解决方法：
- **没有重新扫描**：输入选项5重新扫描，或在 GUI 中点击“重新扫描”按钮。
- **输出目录错误**：准备时指定的输出目录（如 `format`）与后续扫描的目录不一致。
- **只有单语言文件**：如果只有中文或只有英文，`prepare_files.py` 会将其直接复制（不加 C/E 后缀），因此不会形成文件对，可手动处理这些文件。
- **检查输出目录**：打开 `format` 文件夹，确认是否存在 `xxxC.rpy` 和 `xxxE.rpy` 成对出现的文件。

## 📝 使用示例

### 完整工作流程（命令行版）
```bash
# 1. 将汉化文件放入 chinese，SDK 英文文件放入 english
# 2. 启动命令行界面
python interactive_format.py
# 3. 依次选择：0（准备文件）→ 5（重新扫描）→ 2（批量处理）→ 6（删除中间文件）→ 7（退出）
```

### 完整工作流程（GUI 版）
```bash
# 双击 run_gui.bat
# 1. 点击“准备文件”，填写中文、英文、输出目录
# 2. 点击“重新扫描”刷新文件对列表
# 3. 点击“批量处理全部”
# 4. 处理完成后点击“删除中间文件”
# 5. 关闭窗口即可
```

### 手动命令行示例
```bash
# 准备文件
python interactive_format.py --prepare ./chinese ./english ./format

# 删除中间文件（跳过确认）
python interactive_format.py format --delete --yes
```

### 单独处理字符串翻译（调试用）
```bash
python format_strings.py ./format/scripts/commonE.rpy ./format/scripts/commonC.rpy ./format/scripts/common.rpy
```

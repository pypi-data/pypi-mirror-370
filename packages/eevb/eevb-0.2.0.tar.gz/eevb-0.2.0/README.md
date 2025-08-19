# EEVB - Easy Enigma VirtualBox 封装工具

**仅支持 Windows 系统**

EEVB 是一个简化 Enigma Virtual Box 命令行调用的封装工具，通过 JSON 配置文件快速构建虚拟化可执行文件。

## 安装

```bash
pip install eevb
```

## 使用方法

### 初始化配置文件

生成一个模板配置文件 `eevb.json`：

```bash
eevb init
```

自定义输出路径：

```bash
eevb init --output myconfig.json
```

### 构建虚拟化程序

使用配置文件构建输出：

```bash
eevb build
```

指定配置文件：

```bash
eevb build myconfig.json
```

或简写（直接传入 JSON 文件）：

```bash
eevb myconfig.json
```

### 快速打包（无需配置文件）

直接指定输入、输出和要嵌入的文件或文件夹：

```bash
eevb quick -i <输入exe文件> -o <输出exe文件> [options] <要嵌入的文件或文件夹...>
```

可选参数：
- `-c, --compress`      压缩嵌入文件
- `-d, --delete_on_exit`  运行后删除解压文件

示例：
```bash
eevb quick -i app.exe -o app.box.exe data/ config.json
eevb quick -i app.exe -o app.box.exe -c -d data/*
```

### 查看帮助

```bash
eevb --help
eevb init --help
eevb build --help
```

### 配置说明

配置文件为 JSON 格式，主要字段：

- `input`: 原始可执行文件路径
- `output`: 输出虚拟化文件路径
- `files.delete_on_exit`: 是否运行后删除解压文件
- `files.compress`: 是否压缩嵌入文件
- `files.items`: 各虚拟目录下要包含的文件或文件夹路径列表


**注意：** 默认情况下，配置文件中的目录路径只会包含该目录下的所有文件和子目录，不会包含目录本身。如果需要将目录本身也包含进去，请在路径末尾加上 `*`，例如：`folder/to/include*`。

**示例**

假设有如下目录结构：

```
project_folder/
├── data/
│   ├── file1.txt
│   └── file2.txt
```

在配置文件中：

- `"data/"` 只会包含 `file1.txt` 和 `file2.txt`，不会包含 `data` 文件夹本身。
- `"data/*"` 会包含整个 `data` 文件夹（包括其下所有内容），即虚拟化时会保留 `data` 目录结构。


支持的虚拟目录包括：`DefaultFolder`, `SystemFolder`, `WindowsFolder`, `MyDocumentsFolder`, `ProgramFilesFolder` 等（见模板）。

---

# EEVB - Easy Enigma VirtualBox Wrapper

**Windows Only**

EEVB simplifies Enigma Virtual Box command-line usage by building virtualized executables via a JSON configuration file.

## Installation

```bash
pip install eevb
```

## Usage

### Initialize Configuration

Generate a template config file:

```bash
eevb init
```

With custom path:

```bash
eevb init --output myconfig.json
```

### Build Virtual Executable

Build using default config:

```bash
eevb build
```

Specify config file:

```bash
eevb build myconfig.json
```

Or shorthand (pass JSON directly):

```bash
eevb myconfig.json
```

### Quick Build (No Config File)

Directly specify input, output, and files/folders to embed:

```bash
eevb quick -i <input exe> -o <output exe> [options] <files or folders to embed...>
```

Options:
- `-c, --compress`        Compress embedded files
- `-d, --delete_on_exit`  Delete extracted files on exit

Examples:
```bash
eevb quick -i app.exe -o app.box.exe data/ config.json
eevb quick -i app.exe -o app.box.exe -c -d data/*
```

### Show Help

```bash
eevb --help
eevb init --help
eevb build --help
```

### Configuration

The JSON config includes:
- `input`: input executable path
- `output`: output executable path
- `files.delete_on_exit`: delete files after exit
- `files.compress`: compress embedded files
- `files.items`: lists of files/folders for each virtual directory


**Note:** By default, specifying a folder path in the config will only include its contents (files and subfolders), not the folder itself. To include the folder itself, append `*` to the path, e.g. `folder/to/include*`.


**Example**

Suppose you have the following structure:

```
project_folder/
├── data/
│   ├── file1.txt
│   └── file2.txt
```

In the config file:

- `"data/"` will only include `file1.txt` and `file2.txt`, not the `data` folder itself.
- `"data/*"` will include the entire `data` folder (with all its contents), preserving the directory structure in the virtualized output.



Supported virtual folders: `DefaultFolder`, `SystemFolder`, `WindowsFolder`, `MyDocumentsFolder`, `ProgramFilesFolder`, etc. (see template).
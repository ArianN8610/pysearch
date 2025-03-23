# Pseek

## Overview

A powerful command-line tool for searching files, directories, and content inside files efficiently. The tool supports searching by name, content, extensions, and more with advanced filtering options.

## Features

* **Search in file & folder names**
* **Search inside file contents**
* **Highlight matches** in terminal output
* **Optimized for speed** with ThreadPoolExecutor
* **Cross-platform** (Linux, macOS, Windows)

## Installation

### **1️⃣ Install via `pip` (Recommended)**

```sh
pip install pseek
```

### **2️⃣ Install from source**

```sh
git clone https://github.com/ArianN8610/pysearch.git
cd pseek
pip install click==8.1.8
```

## Usage

Run the command with a search query:
```sh
pseek <query> [options]
```

## Examples

### Search for a keyword in file & folder names

```sh
pseek "my_keyword" --path /path/to/search --file --directory
```

### Search inside file contents

```sh
pseek "error" --path /var/logs --content
```

### Search only in specific file types

```sh
pseek "TODO" --path ./projects --ext py --ext txt
```

### Search by regex

```sh
pseek "error\d+" --regex
```

## Command Options

| Option                     | Description                                                  |
|----------------------------|--------------------------------------------------------------|
| `--path`                   | Base directory to search in (default: current directory `.`) |
| `--file`                   | Search only in file names                                    |
| `--directory`              | Search only in directory names                               |
| `--content`                | Search inside file contents                                  |
| `--ext`, `--exclude-ext`   | Filter by file extension (e.g., `.txt`, `.log`)              |
| `--case-sensitive`         | Make the search case-sensitive                               |
| `--regex`                  | Use regular expression for searching                         |
| `--include`, `--exclude`   | Limit search results to specific set of directories or files |
| `--word`                   | Match the whole word only                                    |
| `--max-size`, `--min-size` | Specify maximum and minimum sizes for files and directories  |
| `--full-path`              | Display full path of files and directories                   |

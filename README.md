# Pseek

## Overview

A powerful command-line tool for searching files, directories, and content inside files efficiently. The tool supports searching by name, content, extensions, and more with advanced filtering options.

## Features

* **Search in file & folder names**
* **Search inside file contents**
* **Highlight matches** in terminal output
* **Optimized for speed** with ThreadPoolExecutor
* Support **logical expression** for search queries
* Search inside **archive files** (e.g. `zip`, `rar`, `7z`, `gz`, `bz2`, `xz`, `tar`, `tar.gz`, `tar.bz2`, `tar.xz`)
* **Cross-platform** (Linux, macOS, Windows)

## Installation

### **`1` Install via `pip` (Recommended)**

```sh
pip install pseek
```

### **`2` Install from source**

```sh
git clone https://github.com/ArianN8610/pysearch.git
cd pysearch
python -m venv venv
[Activate venv]
pip install click==8.1.8 lark==1.2.2 py7zr==1.0.0 rarfile==4.2 rapidfuzz==3.13.0
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

| Option                         | Description                                                                                                                                                                                                                                                                                                               |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--path`                       | Base directory to search in (default: current directory `.`)                                                                                                                                                                                                                                                              |
| `--file`                       | Search only in file names                                                                                                                                                                                                                                                                                                 |
| `--directory`                  | Search only in directory names                                                                                                                                                                                                                                                                                            |
| `--content`                    | Search inside file contents                                                                                                                                                                                                                                                                                               |
| `--ext`, `--exclude-ext`       | Filter by file extension (e.g., `txt`, `log`)                                                                                                                                                                                                                                                                             |
| `--case-sensitive`             | Make the search case-sensitive (except when `--expr` is enabled, in which case you can make it case sensitive by putting `c` before term: `c"foo"`)                                                                                                                                                                       |
| `--regex`                      | Use regular expressions to search (except when `--expr` is enabled, in which case you can make it regex by putting `r` before term: `r"foo"`)                                                                                                                                                                             |
| `--include`, `--exclude`       | Limit search results to specific set of directories or files                                                                                                                                                                                                                                                              |
| `--re-include`, `--re-exclude` | Limit search results to specific directories or files with regex                                                                                                                                                                                                                                                          |
| `--word`                       | Match the whole word only (except when `--expr` is enabled, in which case you can make it match whole word by putting `w` before term: `w"foo"`)                                                                                                                                                                          |
| `--expr`                       | Enable to write conditions in the query. Example: `r"foo.*bar" and ("bar" or "baz") and not "qux"` (To use regex, word, and case-sensitive features, you can use the prefixes `r`, `w`, and `c` before terms. Allowed modes: `r`, `w`, `c`, `wc`, `cw`, `rc`, `cr`. Examples: `r"foo.*bar"`, `wc"Foo"`, `cr".*Foo"`, ...) |
| `--timeout`                    | To stop the search after a specified period of time (Seconds)                                                                                                                                                                                                                                                             |
| `--fuzzy`                      | Enable fuzzy search (Highlighting and counting matches are disabled in this mode if `--word` is not enabled to prevent the program from slowing down)                                                                                                                                                                     |
| `--fuzzy_level`                | Similarity threshold from 0 to 99 for fuzzy search (default: `80`)                                                                                                                                                                                                                                                        |
| `--max-size`, `--min-size`     | Specify maximum and minimum sizes for files and directories                                                                                                                                                                                                                                                               |
| `--archive`                    | Enable search within archive files (e.g. `zip`, `rar`, `7z`, `gz`, `bz2`, `xz`, `tar`, `tar.gz`, `tar.bz2`, `tar.xz`)                                                                                                                                                                                                     |
| `--arc-ext`, `--arc-ee`        | Filter by file extension inside archive files                                                                                                                                                                                                                                                                             |
| `--arc-inc`, `--arc-exc`       | Limit search results to specific set of directories or files inside archive files                                                                                                                                                                                                                                         |
| `--arc-max`, `--arc-min`       | Specify maximum and minimum sizes for files inside archive files (It doesn't work for directories because their size is zero in archive files)                                                                                                                                                                            |
| `--rarfb`                      | Path to RAR backend tool (e.g. UnRAR.exe, ...)                                                                                                                                                                                                                                                                            |
| `--full-path`                  | Display full path of files and directories                                                                                                                                                                                                                                                                                |
| `--no-content`                 | Only display files path for content search                                                                                                                                                                                                                                                                                |

## Requirements

* Python 3.6 or higher
* `unrar`, `bsdtar`, `unar` or `7zip` for the rarfile library to support searching inside `.rar` files (optional)

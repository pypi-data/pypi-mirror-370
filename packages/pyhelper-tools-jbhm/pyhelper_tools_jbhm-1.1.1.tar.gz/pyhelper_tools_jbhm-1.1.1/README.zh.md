# 🇨🇳 Helper - Python 库

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)
[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
[![ru](https://img.shields.io/badge/lang-ru-purple.svg)](README.ru.md)
[![tr](https://img.shields.io/badge/lang-tr-orange.svg)](README.tr.md)
[![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](README.it.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 🇨🇳 中文 (简体)

## 📖 概览

Helper 是一个全面的 Python 工具包，旨在简化常见的数据处理、可视化和实用工具任务。它提供：

- 统计分析函数
- 数据可视化工具
- 文件处理工具
- 语法检查功能
- 多语言支持

## ✨ 功能特色

### 📊 数据可视化

- 横向/纵向条形图 (`hbar`, `vbar`)
- 饼图 (`pie`)
- 箱线图 (`boxplot`)
- 直方图 (`histo`)
- 热力图 (`heatmap`)
- 数据表 (`table`)

### 📈 统计分析

- 集中趋势测量 (`get_media`, `get_median`, `get_moda`)
- 离散程度测量 (`get_rank`, `get_var`, `get_desv`)
- 数据归一化 (`normalize`)
- 条件列创建 (`conditional`)

### 🛠 实用工具

- 文件搜索与加载 (`call`)
- 增强的 switch-case 系统 (`Switch`, `AsyncSwitch`)
- 语法检查 (`PythonFileChecker`, `check_syntax`)
- 多语言支持 (`set_language`, `t`)
- 帮助系统 (`help`)

## 🌍 多语言支持

该库支持多种语言。使用以下方式更改语言：

```python
from helper import set_language

set_language("en")  # 英文
set_language("es")  # 西班牙文
set_language("fr")  # 法文
set_language("de")  # 德文
set_language("ru")  # 俄文
set_language("tr")  # 土耳其文
set_language("zh")  # 中文
set_language("it")  # 意大利文
set_language("pt")  # 葡萄牙文
set_language("sv")  # 瑞典文
```

您也可以通过创建 `lang.json` 文件并使用 `load_user_translations()` 函数来添加自定义翻译：

```python
from helper import load_user_translations

# 从 lang.json 加载自定义翻译（默认路径）
load_user_translations()

# 或者指定一个自定义路径
load_user_translations("路径/到/你的/翻译.json")
```

lang.json 示例结构：

```json

{
  "你的键": {
    "en": "英文翻译",
    "es": "西班牙文翻译",
    "fr": "法文翻译",
    "de": "德文翻译",
    "ru": "俄文翻译",
    "tr": "土耳其文翻译",
    "zh": "中文翻译",
    "it": "意大利文翻译",
    "pt": "葡萄牙文翻译",
    "sv": "瑞典文翻译"
  }
}
```

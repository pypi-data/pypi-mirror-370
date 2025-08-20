# 🇷🇺 Helper - Библиотека на Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)
[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
[![tr](https://img.shields.io/badge/lang-tr-orange.svg)](README.tr.md)
[![zh](https://img.shields.io/badge/lang-zh-black.svg)](README.zh.md)
[![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](README.it.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 📖 Обзор

Helper — это комплексный инструмент на Python, предназначенный для упрощения задач обработки данных, визуализации и утилит. Он предоставляет:

- Функции статистического анализа
- Инструменты визуализации данных
- Утилиты для работы с файлами
- Проверку синтаксиса
- Поддержку нескольких языков

## ✨ Возможности

### 📊 Визуализация данных

- Горизонтальные/вертикальные столбчатые диаграммы (`hbar`, `vbar`)
- Круговые диаграммы (`pie`)
- Ящик с усами (`boxplot`)
- Гистограммы (`histo`)
- Тепловые карты (`heatmap`)
- Таблицы данных (`table`)

### 📈 Статистический анализ

- Показатели центральной тенденции (`get_media`, `get_median`, `get_moda`)
- Показатели разброса (`get_rank`, `get_var`, `get_desv`)
- Нормализация данных (`normalize`)
- Условное создание столбцов (`conditional`)

### 🛠 Утилиты

- Поиск и загрузка файлов (`call`)
- Расширенная система switch-case (`Switch`, `AsyncSwitch`)
- Проверка синтаксиса (`PythonFileChecker`, `check_syntax`)
- Поддержка нескольких языков (`set_language`, `t`)
- Справочная система (`help`)

## 🌍 Поддержка нескольких языков

Библиотека поддерживает несколько языков. Сменить язык можно так:

```python
from helper import set_language

set_language("en")  # Английский
set_language("es")  # Испанский
set_language("fr")  # Французский
set_language("de")  # Немецкий
set_language("ru")  # Русский
set_language("tr")  # Турецкий
set_language("zh")  # Китайский
set_language("it")  # Итальянский
set_language("pt")  # Португальский
set_language("sv")  # Шведский
```

Вы также можете добавить собственные переводы, создав файл `lang.json` и используя функцию `load_user_translations()`:

```python
from helper import load_user_translations

# Загрузить пользовательские переводы из lang.json (путь по умолчанию)
load_user_translations()

# Или указать собственный путь
load_user_translations("путь/к/вашим/переводам.json")
```

Пример структуры lang.json:

```json
{
  "ваш_ключ": {
    "en": "Перевод на английский",
    "es": "Перевод на испанский",
    "fr": "Перевод на французский",
    "de": "Перевод на немецкий",
    "ru": "Перевод на русский",
    "tr": "Перевод на турецкий",
    "zh": "Перевод на китайский",
    "it": "Перевод на итальянский",
    "pt": "Перевод на португальский",
    "sv": "Перевод на шведский"
  }
}
```

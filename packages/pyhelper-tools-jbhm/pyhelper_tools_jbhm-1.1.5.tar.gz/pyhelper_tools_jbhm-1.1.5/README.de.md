# 🇩🇪 Helper - Python-Bibliothek

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)
[![ru](https://img.shields.io/badge/lang-ru-purple.svg)](README.ru.md)
[![tr](https://img.shields.io/badge/lang-tr-orange.svg)](README.tr.md)
[![zh](https://img.shields.io/badge/lang-zh-black.svg)](README.zh.md)
[![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](README.it.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 📖 Überblick

Helper ist ein umfassendes Python-Toolkit zur Vereinfachung gängiger Aufgaben im Bereich Datenverarbeitung, Visualisierung und Dienstprogramme. Es bietet:

- Statistische Analysefunktionen
- Datenvisualisierungstools
- Datei-Handling-Werkzeuge
- Syntaxüberprüfung
- Mehrsprachige Unterstützung

## ✨ Funktionen

### 📊 Datenvisualisierung

- Horizontale/vertikale Balkendiagramme (`hbar`, `vbar`)
- Kreisdiagramme (`pie`)
- Boxplots (`boxplot`)
- Histogramme (`histo`)
- Heatmaps (`heatmap`)
- Datentabellen (`table`)

### 📈 Statistische Analyse

- Maße der zentralen Tendenz (`get_media`, `get_median`, `get_moda`)
- Streuungsmaße (`get_rank`, `get_var`, `get_desv`)
- Daten-Normalisierung (`normalize`)
- Bedingte Spaltenerstellung (`conditional`)

### 🛠 Dienstprogramme

- Datei suchen und laden (`call`)
- Erweitertes Switch-Case-System (`Switch`, `AsyncSwitch`)
- Syntaxprüfung (`PythonFileChecker`, `check_syntax`)
- Mehrsprachige Unterstützung (`set_language`, `t`)
- Hilfesystem (`help`)

## 🌍 Mehrsprachige Unterstützung

Die Bibliothek unterstützt mehrere Sprachen. Sprache ändern mit:

```python
from helper import set_language

set_language("en")  # Englisch
set_language("es")  # Spanisch
set_language("fr")  # Französisch
set_language("de")  # Deutsch
set_language("ru")  # Russisch
set_language("tr")  # Türkisch
set_language("zh")  # Chinesisch
set_language("it")  # Italienisch
set_language("pt")  # Portugiesisch
set_language("sv")  # Schwedisch
```

Sie können auch eigene Übersetzungen hinzufügen, indem Sie eine Datei `lang.json` erstellen und die Funktion `load_user_translations()` verwenden:

```python
from helper import load_user_translations

# Eigene Übersetzungen aus lang.json laden (Standardpfad)
load_user_translations()

# Oder benutzerdefinierten Pfad angeben
load_user_translations("pfad/zu/deinen/übersetzungen.json")
```

Beispiel für eine lang.json-Struktur:

```json
{
  "dein_schlüssel": {
    "en": "Englische Übersetzung",
    "es": "Spanische Übersetzung",
    "fr": "Französische Übersetzung",
    "de": "Deutsche Übersetzung",
    "ru": "Russische Übersetzung",
    "tr": "Türkische Übersetzung",
    "zh": "Chinesische Übersetzung",
    "it": "Italienische Übersetzung",
    "pt": "Portugiesische Übersetzung",
    "sv": "Schwedische Übersetzung"
  }
}
```

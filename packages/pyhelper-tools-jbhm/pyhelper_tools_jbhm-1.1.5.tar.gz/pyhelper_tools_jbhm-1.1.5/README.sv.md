# 🇸🇪 Helper - Python-bibliotek

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)
[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
[![ru](https://img.shields.io/badge/lang-ru-purple.svg)](README.ru.md)
[![tr](https://img.shields.io/badge/lang-tr-orange.svg)](README.tr.md)
[![zh](https://img.shields.io/badge/lang-zh-black.svg)](README.zh.md)
[![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](README.it.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)

## 📖 Översikt

Helper är ett omfattande Python-verktygspaket som är utformat för att förenkla vanliga uppgifter inom datahantering, visualisering och verktyg. Det erbjuder:

- Statistiska analysfunktioner
- Datavisualiseringsverktyg
- Verktyg för filhantering
- Syntaxkontroll
- Flerspråkigt stöd

## ✨ Funktioner

### 📊 Datavisualisering

- Horisontella/vertikala stapeldiagram (`hbar`, `vbar`)
- Cirkeldiagram (`pie`)
- Lådagram (`boxplot`)
- Histogram (`histo`)
- Värmekartor (`heatmap`)
- Datatabeller (`table`)

### 📈 Statistisk analys

- Mått på central tendens (`get_media`, `get_median`, `get_moda`)
- Spridningsmått (`get_rank`, `get_var`, `get_desv`)
- Normalisering av data (`normalize`)
- Villkorlig kolumnskapande (`conditional`)

### 🛠 Verktyg

- Söka och läsa in filer (`call`)
- Förbättrat switch-case-system (`Switch`, `AsyncSwitch`)
- Syntaxkontroll (`PythonFileChecker`, `check_syntax`)
- Flerspråkigt stöd (`set_language`, `t`)
- Hjälpsystem (`help`)

## 🌍 Flerspråkigt stöd

Biblioteket stöder flera språk. Byt språk med:

```python
from helper import set_language

set_language("en")  # Engelska
set_language("es")  # Spanska
set_language("fr")  # Franska
set_language("de")  # Tyska
set_language("ru")  # Ryska
set_language("tr")  # Turkiska
set_language("zh")  # Kinesiska
set_language("it")  # Italienska
set_language("pt")  # Portugisiska
set_language("sv")  # Svenska
```

Du kan också lägga till egna översättningar genom att skapa en `lang.json`-fil och använda funktionen `load_user_translations()`:

```python
from helper import load_user_translations

# Ladda egna översättningar från lang.json (standardväg)
load_user_translations()

# Eller specificera en anpassad sökväg
load_user_translations("sökväg/till/dina/översättningar.json")
```

Exempel på lang.json-struktur:

```json

{
  "din_nyckel": {
    "en": "Engelsk översättning",
    "es": "Spansk översättning",
    "fr": "Fransk översättning",
    "de": "Tysk översättning",
    "ru": "Rysk översättning",
    "tr": "Turkisk översättning",
    "zh": "Kinesisk översättning",
    "it": "Italiensk översättning",
    "pt": "Portugisisk översättning",
    "sv": "Svensk översättning"
  }
}
```

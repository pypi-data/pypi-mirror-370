# 🇮🇹 Helper - Libreria Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)
[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
[![ru](https://img.shields.io/badge/lang-ru-purple.svg)](README.ru.md)
[![tr](https://img.shields.io/badge/lang-tr-orange.svg)](README.tr.md)
[![zh](https://img.shields.io/badge/lang-zh-black.svg)](README.zh.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 📖 Panoramica

Helper è un toolkit completo per Python progettato per semplificare attività comuni di gestione dei dati, visualizzazione e utilità. Offre:

- Funzioni di analisi statistica
- Strumenti di visualizzazione dei dati
- Utilità per la gestione dei file
- Controllo della sintassi
- Supporto multilingua

## ✨ Caratteristiche

### 📊 Visualizzazione Dati

- Grafici a barre orizzontali/verticali (`hbar`, `vbar`)
- Grafici a torta (`pie`)
- Box plot (`boxplot`)
- Istogrammi (`histo`)
- Mappe di calore (`heatmap`)
- Tabelle di dati (`table`)

### 📈 Analisi Statistica

- Misure di tendenza centrale (`get_media`, `get_median`, `get_moda`)
- Misure di dispersione (`get_rank`, `get_var`, `get_desv`)
- Normalizzazione dei dati (`normalize`)
- Creazione di colonne condizionali (`conditional`)

### 🛠 Utilità

- Ricerca e caricamento di file (`call`)
- Sistema avanzato switch-case (`Switch`, `AsyncSwitch`)
- Controllo della sintassi (`PythonFileChecker`, `check_syntax`)
- Supporto multilingua (`set_language`, `t`)
- Sistema di aiuto (`help`)

## 🌍 Supporto Multilingua

La libreria supporta più lingue. Cambia la lingua con:

```python
from helper import set_language

set_language("en")  # Inglese
set_language("es")  # Spagnolo
set_language("fr")  # Francese
set_language("de")  # Tedesco
set_language("ru")  # Russo
set_language("tr")  # Turco
set_language("zh")  # Cinese
set_language("it")  # Italiano
set_language("pt")  # Portoghese
set_language("sv")  # Svedese
```

Puoi anche aggiungere le tue traduzioni creando un file `lang.json` e utilizzando la funzione `load_user_translations()`:

```python
from helper import load_user_translations

# Carica le traduzioni personalizzate da lang.json (percorso predefinito)
load_user_translations()

# Oppure specifica un percorso personalizzato
load_user_translations("percorso/alle/tuetraduzioni.json")
```

Esempio di struttura lang.json:

```json

{
  "tuo_chiave": {
    "en": "Traduzione in inglese",
    "es": "Traduzione in spagnolo",
    "fr": "Traduzione in francese",
    "de": "Traduzione in tedesco",
    "ru": "Traduzione in russo",
    "tr": "Traduzione in turco",
    "zh": "Traduzione in cinese",
    "it": "Traduzione in italiano",
    "pt": "Traduzione in portoghese",
    "sv": "Traduzione in svedese"
  }
}
```

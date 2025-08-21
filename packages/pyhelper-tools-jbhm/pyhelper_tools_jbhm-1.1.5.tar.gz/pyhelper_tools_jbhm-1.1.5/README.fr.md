# 🇫🇷 Helper - Bibliothèque Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)
[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
[![ru](https://img.shields.io/badge/lang-ru-purple.svg)](README.ru.md)
[![tr](https://img.shields.io/badge/lang-tr-orange.svg)](README.tr.md)
[![zh](https://img.shields.io/badge/lang-zh-black.svg)](README.zh.md)
[![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](README.it.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 📖 Aperçu

Helper est un ensemble d’outils Python complet conçu pour simplifier les tâches courantes de traitement de données, de visualisation et d’utilitaires. Il fournit :

- Fonctions d'analyse statistique
- Outils de visualisation de données
- Utilitaires de gestion de fichiers
- Vérification de la syntaxe
- Support multilingue

## ✨ Fonctionnalités

### 📊 Visualisation de données

- Graphiques à barres horizontales/verticales (`hbar`, `vbar`)
- Graphiques circulaires (`pie`)
- Boîtes à moustaches (`boxplot`)
- Histogrammes (`histo`)
- Cartes de chaleur (`heatmap`)
- Tableaux de données (`table`)

### 📈 Analyse statistique

- Mesures de tendance centrale (`get_media`, `get_median`, `get_moda`)
- Mesures de dispersion (`get_rank`, `get_var`, `get_desv`)
- Normalisation des données (`normalize`)
- Création de colonnes conditionnelles (`conditional`)

### 🛠 Utilitaires

- Recherche et chargement de fichiers (`call`)
- Système switch-case amélioré (`Switch`, `AsyncSwitch`)
- Vérification de syntaxe (`PythonFileChecker`, `check_syntax`)
- Support multilingue (`set_language`, `t`)
- Système d’aide (`help`)

## 🌍 Support multilingue

La bibliothèque prend en charge plusieurs langues. Changez la langue avec :

```python
from helper import set_language

set_language("en")  # Anglais
set_language("es")  # Espagnol
set_language("fr")  # Français
set_language("de")  # Allemand
set_language("ru")  # Russe
set_language("tr")  # Turc
set_language("zh")  # Chinois
set_language("it")  # Italien
set_language("pt")  # Portugais
set_language("sv")  # Suédois
```

Vous pouvez également ajouter vos propres traductions en créant un fichier `lang.json` et en utilisant la fonction `load_user_translations()` :

```python
from helper import load_user_translations

# Charger les traductions personnalisées depuis lang.json (chemin par défaut)
load_user_translations()

# Ou spécifier un chemin personnalisé
load_user_translations("chemin/vers/vos/traductions.json")
```

Exemple de structure de lang.json :

```json
{
  "votre_cle": {
    "en": "Traduction en anglais",
    "es": "Traduction en espagnol",
    "fr": "Traduction en français",
    "de": "Traduction en allemand",
    "ru": "Traduction en russe",
    "tr": "Traduction en turc",
    "zh": "Traduction en chinois",
    "it": "Traduction en italien",
    "pt": "Traduction en portugais",
    "sv": "Traduction en suédois"
  }
}
```

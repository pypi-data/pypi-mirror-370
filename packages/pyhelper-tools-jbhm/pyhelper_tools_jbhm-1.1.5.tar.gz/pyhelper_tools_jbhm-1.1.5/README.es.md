# 🇪🇸 Helper - Biblioteca Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)
[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
[![ru](https://img.shields.io/badge/lang-ru-purple.svg)](README.ru.md)
[![tr](https://img.shields.io/badge/lang-tr-orange.svg)](README.tr.md)
[![zh](https://img.shields.io/badge/lang-zh-black.svg)](README.zh.md)
[![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](README.it.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 📖 Descripción general

Helper es un conjunto de herramientas completo en Python diseñado para simplificar tareas comunes de manejo de datos, visualización y utilidades. Proporciona:

* Funciones de análisis estadístico
* Herramientas de visualización de datos
* Utilidades para manejo de archivos
* Comprobación de sintaxis
* Soporte multilenguaje

## ✨ Características

### 📊 Visualización de Datos

* Gráficos de barras horizontales/verticales (`hbar`,     `vbar`)
* Gráficos de torta (`pie`)
* Diagramas de caja (`boxplot`)
* Histogramas (`histo`)
* Mapas de calor (`heatmap`)
* Tablas de datos (`table`)

### 📈 Análisis Estadístico

* Medidas de tendencia central (`get_media`,     `get_median`,     `get_moda`)
* Medidas de dispersión (`get_rank`,     `get_var`,     `get_desv`)
* Normalización de datos (`normalize`)
* Creación de columnas condicionales (`conditional`)

### 🛠 Utilidades

* Búsqueda y carga de archivos (`call`)
* Sistema mejorado de switch-case (`Switch`,     `AsyncSwitch`)
* Verificación de sintaxis (`PythonFileChecker`,     `check_syntax`)
* Soporte multilenguaje (`set_language`,     `t`)
* Sistema de ayuda (`help`)

## 🌍 Soporte Multilenguaje

La librería soporta múltiples idiomas. Cambia el idioma con:

```python
from helper import set_language

set_language("en")  # Inglés
set_language("es")  # Español
set_language("fr")  # Francés
set_language("de")  # Alemán
set_language("ru")  # Ruso
set_language("tr")  # Turco
set_language("zh")  # Chino
set_language("it")  # Italiano
set_language("pt")  # Portugués
set_language("sv")  # Sueco
```

También puedes agregar tus propias traducciones creando un archivo lang.json y usando la función load_user_translations():

```python
from helper import load_user_translations

# Carga traducciones personalizadas desde lang.json (ruta por defecto)
load_user_translations()

# O especifica una ruta personalizada
load_user_translations("ruta/a/tus/traducciones.json")
```

Ejemplo de estructura para lang.json:

```json
{
    "tu_clave": {
      "en": "Traducción en inglés",
      "es": "Traducción en español",
      "fr": "Traducción en francés",
      "de": "Traducción en alemán",
      "ru": "Traducción en ruso",
      "tr": "Traducción en turco",
      "zh": "Traducción en chino",
      "it": "Traducción en italiano",
      "pt": "Traducción en portugués",
      "sv": "Traducción en sueco"
    }
}
```

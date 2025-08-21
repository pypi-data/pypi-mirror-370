# 🇹🇷 Helper - Python Kütüphanesi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)
[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
[![ru](https://img.shields.io/badge/lang-ru-purple.svg)](README.ru.md)
[![zh](https://img.shields.io/badge/lang-zh-black.svg)](README.zh.md)
[![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](README.it.md)
[![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](README.pt.md)
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 📖 Genel Bakış

Helper, veri işleme, görselleştirme ve yardımcı araçlar gibi yaygın görevleri kolaylaştırmak için tasarlanmış kapsamlı bir Python araç takımıdır. Şunları sağlar:

- İstatistiksel analiz fonksiyonları
- Veri görselleştirme araçları
- Dosya yönetimi yardımcıları
- Sözdizimi denetimi
- Çok dilli destek

## ✨ Özellikler

### 📊 Veri Görselleştirme

- Yatay/dikey çubuk grafikler (`hbar`, `vbar`)
- Pasta grafikler (`pie`)
- Kutu grafikler (`boxplot`)
- Histogramlar (`histo`)
- Isı haritaları (`heatmap`)
- Veri tabloları (`table`)

### 📈 İstatistiksel Analiz

- Merkezi eğilim ölçüleri (`get_media`, `get_median`, `get_moda`)
- Dağılım ölçüleri (`get_rank`, `get_var`, `get_desv`)
- Veri normalleştirme (`normalize`)
- Koşullu sütun oluşturma (`conditional`)

### 🛠 Yardımcı Araçlar

- Dosya arama ve yükleme (`call`)
- Gelişmiş switch-case sistemi (`Switch`, `AsyncSwitch`)
- Sözdizimi kontrolü (`PythonFileChecker`, `check_syntax`)
- Çok dilli destek (`set_language`, `t`)
- Yardım sistemi (`help`)

## 🌍 Çok Dilli Destek

Kütüphane birden fazla dili destekler. Dili şu şekilde değiştirebilirsiniz:

```python
from helper import set_language

set_language("en")  # İngilizce
set_language("es")  # İspanyolca
set_language("fr")  # Fransızca
set_language("de")  # Almanca
set_language("ru")  # Rusça
set_language("tr")  # Türkçe
set_language("zh")  # Çince
set_language("it")  # İtalyanca
set_language("pt")  # Portekizce
set_language("sv")  # İsveççe
```

Ayrıca `lang.json` adlı bir dosya oluşturarak ve `load_user_translations()` fonksiyonunu kullanarak kendi çevirilerinizi ekleyebilirsiniz:

```python
from helper import load_user_translations

# lang.json dosyasından özel çevirileri yükle (varsayılan yol)
load_user_translations()

# Ya da özel bir yol belirt
load_user_translations("yol/senin/çevirilerin.json")
```

lang.json dosya yapısı örneği:

```json
{
  "anahtarın": {
    "en": "İngilizce çeviri",
    "es": "İspanyolca çeviri",
    "fr": "Fransızca çeviri",
    "de": "Almanca çeviri",
    "ru": "Rusça çeviri",
    "tr": "Türkçe çeviri",
    "zh": "Çince çeviri",
    "it": "İtalyanca çeviri",
    "pt": "Portekizce çeviri",
    "sv": "İsveççe çeviri"
  }
}
```

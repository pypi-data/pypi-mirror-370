# 🇵🇹 Helper - Biblioteca Python

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
[![sv](https://img.shields.io/badge/lang-sv-blue.svg)](README.sv.md)

## 📖 Visão Geral

Helper é um kit de ferramentas completo em Python projetado para simplificar tarefas comuns de manipulação de dados, visualização e utilitários. Ele oferece:

- Funções de análise estatística
- Ferramentas de visualização de dados
- Utilitários para manipulação de arquivos
- Verificação de sintaxe
- Suporte multilíngue

## ✨ Funcionalidades

### 📊 Visualização de Dados

- Gráficos de barras horizontais/verticais (`hbar`, `vbar`)
- Gráficos de pizza (`pie`)
- Gráficos de caixa (`boxplot`)
- Histogramas (`histo`)
- Mapas de calor (`heatmap`)
- Tabelas de dados (`table`)

### 📈 Análise Estatística

- Medidas de tendência central (`get_media`, `get_median`, `get_moda`)
- Medidas de dispersão (`get_rank`, `get_var`, `get_desv`)
- Normalização de dados (`normalize`)
- Criação de colunas condicionais (`conditional`)

### 🛠 Utilitários

- Busca e carregamento de arquivos (`call`)
- Sistema switch-case aprimorado (`Switch`, `AsyncSwitch`)
- Verificação de sintaxe (`PythonFileChecker`, `check_syntax`)
- Suporte multilíngue (`set_language`, `t`)
- Sistema de ajuda (`help`)

## 🌍 Suporte Multilíngue

A biblioteca suporta vários idiomas. Altere o idioma com:

```python
from helper import set_language

set_language("en")  # Inglês
set_language("es")  # Espanhol
set_language("fr")  # Francês
set_language("de")  # Alemão
set_language("ru")  # Russo
set_language("tr")  # Turco
set_language("zh")  # Chinês
set_language("it")  # Italiano
set_language("pt")  # Português
set_language("sv")  # Sueco
```

Você também pode adicionar suas próprias traduções criando um arquivo `lang.json` e usando a função `load_user_translations()`:

```python
from helper import load_user_translations

# Carregar traduções personalizadas de lang.json (caminho padrão)
load_user_translations()

# Ou especificar um caminho personalizado
load_user_translations("caminho/para/suas/traducoes.json")
```

Exemplo de estrutura do lang.json:

```json

{
  "sua_chave": {
    "en": "Tradução em inglês",
    "es": "Tradução em espanhol",
    "fr": "Tradução em francês",
    "de": "Tradução em alemão",
    "ru": "Tradução em russo",
    "tr": "Tradução em turco",
    "zh": "Tradução em chinês",
    "it": "Tradução em italiano",
    "pt": "Tradução em português",
    "sv": "Tradução em sueco"
  }
}
```

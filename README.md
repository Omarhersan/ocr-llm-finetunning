# Arkham OCR & LLM Fine-Tuning Pipeline

Pipeline completo para extraer, procesar y entrenar un modelo de lenguaje especializado en contratos de arrendamiento a partir de documentos PDF mediante OCR.

## 📋 Descripción

Este proyecto implementa un pipeline end-to-end que:

1. Extrae texto de contratos PDF mediante OCR
2. Limpia y normaliza el texto (elimina artefactos, normaliza formatos)
3. Divide el contrato en secciones lógicas
4. Extrae tablas de pagos y las estructura
5. Genera preguntas y respuestas usando GPT-4o-mini
6. Prepara un dataset para fine-tuning
7. Entrena un modelo especializado con OpenAI

## 🎯 Resultado

**Modelo Fine-Tuned:** `ft:gpt-4o-mini-2024-07-18:personal:arkham-contract:CcK1RP96`

- **Dataset:** 116 pares de preguntas y respuestas
- **Tokens entrenados:** 28,857
- **Uso:** Responder preguntas sobre contratos de arrendamiento

## 🏗️ Estructura del Proyecto

```
Arkham/
├── data/
│   ├── raw/                      # PDF original del contrato
│   ├── ocr/                      # Texto extraído por OCR
│   ├── cleaned/                  # Texto limpio sin ruido OCR
│   ├── sections/                 # Secciones del contrato + tabla de pagos
│   ├── generated_qa/             # Dataset de Q&A generado
│   └── final_dataset/            # Dataset listo para fine-tuning
│       ├── finetune_dataset.jsonl
│       └── model_info.json
│
├── notebooks/
│   └── EDA.ipynb                 # Análisis exploratorio de datos
│
└── src/
    ├── ocr/
    │   ├── extraction.py         # Extracción de texto desde PDF
    │   └── clean_data.py         # Limpieza de artefactos OCR
    │
    ├── preprocessing/
    │   ├── table_extraction.py   # Extracción de tabla de pagos
    │   ├── split_sections.py     # División por secciones
    │   ├── generate_sections.py  # Orquestador del preprocesamiento
    │   └── constants.py          # Constantes y configuración
    │
    ├── dataset_generation/
    │   ├── dataset_generation.py     # Script principal de generación
    │   ├── generated_qa_sections.py  # Generación de Q&A por secciones
    │   ├── generated_qa_anexos.py    # Generación de Q&A de tabla
    │   └── utils.py                  # Prompts y utilidades
    │
    └── training/
        ├── prepare_finetune_data.py  # Convierte al formato OpenAI
        └── train.py                  # Entrena el modelo con OpenAI API
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.12+
- API Key de OpenAI

### Setup

1. Clonar el repositorio:

```bash
git clone https://github.com/Omarhersan/ocr-llm-finetunning.git
cd ocr-llm-finetunning
```

2. Crear entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
```

3. Instalar dependencias:

```bash
pip install openai python-dotenv pandas matplotlib seaborn nltk scikit-learn
```

## 📊 Pipeline de Ejecución

### 1. Extracción OCR

```bash
python src/ocr/extraction.py
```

**Output:** `data/ocr/CONTRATO_AP000000718_ocr.txt`

### 2. Limpieza de Datos

```bash
python src/ocr/clean_data.py
```

**Output:** `data/cleaned/CONTRATO_AP000000718_cleaned.txt`

**Transformaciones aplicadas:**

- Normalización Unicode (NFKC)
- Eliminación de ligaduras (ﬁ → fi)
- Normalización de ordinales (PRIMERA., SEGUNDA.)
- Eliminación de números de página
- Reducción de espacios excesivos

### 3. Generación de Secciones

```bash
python src/preprocessing/generate_sections.py
```

**Output:**

- `data/sections/seccion_*.txt` (5 secciones)
- `data/sections/tabla_pagos.json`
- `data/sections/tabla_pagos.csv`

**Secciones detectadas:**

1. DECLARACIONES
2. CLAUSULAS PRIMERA
3. OBJETO
4. OBLIGACIONES
5. INCUMPLIMIENTO

### 4. Generación de Dataset Q&A

```bash
python src/dataset_generation/dataset_generation.py
```

**Output:** `data/generated_qa/merged_qa_dataset.jsonl`

**Contenido:**

- 116 pares de preguntas y respuestas
- Formato: `{"question": "...", "answer": "..."}`
- Generadas con GPT-4o-mini basándose en el contenido del contrato

### 5. Preparación para Fine-Tuning

```bash
python src/training/prepare_finetune_data.py
```

**Output:** `data/final_dataset/finetune_dataset.jsonl`

**Formato OpenAI:**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente especializado en contratos de arrendamiento..."
    },
    { "role": "user", "content": "¿Quién es el Arrendador?" },
    {
      "role": "assistant",
      "content": "El Arrendador es Boston Leasing México, S.A. de C.V..."
    }
  ]
}
```

### 6. Entrenamiento del Modelo

```bash
python src/training/train.py
```

**Proceso:**

1. Sube el dataset a OpenAI
2. Crea el trabajo de fine-tuning
3. Monitorea el progreso
4. Guarda la información del modelo en `model_info.json`

**Resultado:** Modelo fine-tuned listo para usar

## 📈 Análisis Exploratorio (EDA)

El notebook `notebooks/data_analysis.ipynb` contiene análisis detallado:

- **Sección 1:** Análisis de datos crudos OCR (ruido, artefactos)
- **Sección 2:** Comparación entre datos crudos y limpios
- **Sección 3:** Análisis de secciones generadas
- **Sección 4:** Estadísticas del dataset Q&A
- **Sección 5:** Resumen y conclusiones

**Métricas clave:**

- Reducción de ruido: 19.67%
- Números de página eliminados: 72% (23/32)
- Espacios excesivos reducidos: 50% (3/6)
- Normalización de ordinales: 100% de OCR corregidos

## 🔧 Uso del Modelo Fine-Tuned

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

response = client.chat.completions.create(
    model="ft:gpt-4o-mini-2024-07-18:personal:arkham-contract:CcK1RP96",
    messages=[
        {
            "role": "system",
            "content": "Eres un asistente especializado en contratos de arrendamiento."
        },
        {
            "role": "user",
            "content": "¿Cuál es el monto de la renta mensual?"
        }
    ]
)

print(response.choices[0].message.content)
```

## 📝 Configuración

### Variables de Entorno (.env)

```env
OPEN_AI_API_KEY=...
```

### Rutas Principales (src/preprocessing/constants.py)

```python
INPUT_RAW = "data/raw/CONTRATO_AP000000718.pdf"
INPUT_OCR = "data/ocr/CONTRATO_AP000000718_ocr.txt"
INPUT_CLEANED = "data/cleaned/CONTRATO_AP000000718_cleaned.txt"
OUTPUT_SECTIONS = "data/sections/"
```

## 🎓 Mejoras Futuras

1. **Aumento del Dataset**

   - Objetivo: 300-500 pares Q&A para mejor rendimiento
   - Procesar múltiples contratos similares

2. **Mejoras en Limpieza**

3. **Evaluación del Modelo**

   - Crear conjunto de prueba
   - Comparar contra modelo base

4. **Procesamiento de Múltiples Documentos**

   - Generalizar pipeline para cualquier contrato
   - Detección automática de estructura

5. **Mejorar calidad del dataset**
   - Usar un modelo calificador de preguntas del dataset para destilar un dataset con mayor calidad

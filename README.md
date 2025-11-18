# Arkham Intelligence - Challenge de LLM Fine-Tuning

Pipeline completo para extraer, procesar y entrenar un modelo de lenguaje especializado en contratos de arrendamiento a partir de documentos PDF mediante OCR.

## 📋 Descripción del Proyecto

Este proyecto fue desarrollado como respuesta al challenge de Arkham Intelligence para crear un sistema de procesamiento y análisis de contratos legales mediante fine-tuning de modelos de lenguaje. El pipeline implementa un flujo end-to-end que:

1. Extrae texto de contratos PDF mediante OCR (PyMuPDF)
2. Limpia y normaliza el texto eliminando artefactos de OCR
3. Divide el contrato en secciones lógicas estructuradas
4. Extrae y estructura tablas de pagos
5. Genera preguntas y respuestas contextuales usando GPT-4o-mini
6. Prepara un dataset optimizado para fine-tuning
7. Entrena un modelo especializado mediante OpenAI API

## 🎯 Resultados Obtenidos

**Modelo Fine-Tuned:** `ft:gpt-4o-mini-2024-07-18:personal:arkham-contract:CcK1RP96`

- **Dataset generado:** 116 pares de preguntas y respuestas
- **Tokens procesados durante entrenamiento:** 28,857
- **Tasa de éxito en limpieza OCR:** 96.8% de reducción de ruido
- **Secciones estructuradas:** 5 secciones principales + tabla de pagos
- **Aplicación:** Chatbot especializado en contratos de arrendamiento (Next.js)

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

## 📈 Hallazgos del Análisis Exploratorio (EDA)

El notebook `notebooks/data_analysis.ipynb` documenta el proceso de validación y los hallazgos principales del desarrollo. A continuación se describen los descubrimientos más relevantes:

### 1. Análisis de Datos Crudos OCR

**Problemas identificados en el texto extraído:**
- **89,648 caracteres totales** con ruido significativo de OCR
- **32 números de página** en formato "X/Y" que contaminaban el texto
- **Palabras fragmentadas** por guiones en saltos de línea
- **Espacios múltiples** y tabulaciones inconsistentes
- **Caracteres Unicode problemáticos** de símbolos especiales
- **Errores de OCR en ordinales:** variantes como "PRAIMERA", "SEGJNDA", "SEPTlMA" (con L minúscula)
- **Ligaduras no detectadas** en este documento específico (0 ocurrencias)

**Distribución de chunks:**
- 117 chunks iniciales detectados por saltos de línea dobles
- Alta variabilidad en longitud de chunks (0-2000+ caracteres)
- Necesidad de filtrar chunks vacíos para análisis significativo

### 2. Efectividad del Pipeline de Limpieza

**Transformaciones validadas:**

| Transformación | Resultado | Efectividad |
|----------------|-----------|-------------|
| Normalización Unicode (NFKC) | Aplicada a todo el texto | 100% |
| Eliminación de números de página | 23/32 removidos | 72% |
| Normalización de ordinales | Todos corregidos | 100% |
| Reducción de espacios excesivos | 3/6 instancias | 50% |
| Merge de títulos fragmentados | Títulos consolidados | ✓ |

**Métricas de limpieza:**
- **Reducción de caracteres:** 3.2% del texto original (ruido removido)
- **Reducción de ruido por chunk:** Media de 8.5 → 0.27 caracteres problemáticos
- **Mejora general:** 96.8% de reducción en artefactos detectables

**Observaciones importantes:**
- Algunos artefactos residuales permanecen (ej: "Jos diferent...", "6én", "sa 'presentare")
- Estos residuos pueden afectar la extracción de entidades nombradas
- El balance entre limpieza agresiva y preservación de contenido se mantuvo conservador

### 3. Análisis de Secciones Estructuradas

**Resultados de segmentación:**
- **5 secciones principales** exitosamente extraídas
- **Longitud promedio:** ~17,930 caracteres por sección
- **Estructura preservada:** Numeración romana (I-V) correctamente identificada
- **Tipos de contenido heterogéneo:** 
  - Secciones 1-4: Texto legal estructurado con cláusulas
  - Sección 5: Material de cierre y firmas

**Calidad estructural:**
- Títulos normalizados: "I. DECLARACIONES", "II. CLAUSULAS", "III. OBJETO", etc.
- Listas y enumeraciones preservadas (romano, letras, números)
- Tabla de pagos extraída y estructurada en formato JSON/CSV separado

**Riesgos identificados:**
- Contenido administrativo mezclado con texto legal en sección final
- Posible mejora: crear sección específica para páginas de cierre (fuera del scope actual)

### 4. Análisis del Dataset de Q&A Generado

**Estadísticas del dataset:**
- **Total de pares Q&A:** 116
- **Longitud promedio de preguntas:** ~85 caracteres
- **Longitud promedio de respuestas:** ~180 caracteres
- **Distribución:** Preguntas generadas por cada sección del contrato

**Características de calidad:**
- Preguntas contextuales relevantes al dominio legal
- Respuestas extraídas directamente del texto del contrato
- Cobertura balanceada entre secciones estructurales

**Limitaciones identificadas:**
- Dataset relativamente pequeño (116 pares)
- Recomendación: expandir a 300-500 pares para mejor generalización
- Posible estrategia: procesar múltiples contratos similares

### 5. Conclusiones del Análisis

**Validación exitosa del pipeline:**
1. ✅ OCR extrae texto con calidad aceptable (~3% de ruido)
2. ✅ Limpieza elimina 96.8% de artefactos detectables
3. ✅ Segmentación preserva estructura semántica del documento
4. ✅ Dataset Q&A cubre contenido relevante del contrato
5. ⚠️ Espacio para mejora en cantidad de datos de entrenamiento

**Impacto en fine-tuning:**
- Pipeline genera datos suficientemente limpios para entrenamiento
- Estructura preservada facilita generación de respuestas contextuales
- Modelo resultante muestra comprensión del dominio de contratos de arrendamiento

**Próximos pasos sugeridos:**
- Implementar calificador de calidad de preguntas para destilar dataset
- Expandir corpus con múltiples contratos
- Evaluar modelo contra conjunto de prueba dedicado

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

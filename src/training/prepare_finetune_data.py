"""
Script para preparar datos de Q&A para fine-tuning de OpenAI.

Convierte el formato:
    {"question": "...", "answer": "..."}
    
Al formato requerido por OpenAI:
    {"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}

Requisitos según la documentación de OpenAI:
- Formato JSONL (una estructura JSON completa por línea)
- Usar el formato de chat completions
- Mínimo 10 líneas en el archivo
- Recomendado: 50-100 ejemplos para mejores resultados
"""

import json
from pathlib import Path


# Configuración de rutas
INPUT_PATH = Path("../../data/generated_qa/merged_qa_dataset.jsonl")
OUTPUT_PATH = Path("../../data/final_dataset/finetune_dataset.jsonl")

# Sistema de instrucciones opcional para incluir contexto
SYSTEM_INSTRUCTION = (
    "Eres un asistente especializado en contratos de arrendamiento. "
    "Responde preguntas basándote en la información del contrato de manera precisa y concisa."
)


def load_qa_dataset(file_path: Path) -> list[dict]:
    """Carga el dataset de Q&A desde un archivo JSONL."""
    qa_pairs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                qa_pairs.append(json.loads(line))
    return qa_pairs


def convert_to_openai_format(qa_pairs: list[dict], include_system: bool = True) -> list[dict]:
    """
    Convierte pares Q&A al formato de mensajes de OpenAI.
    
    Args:
        qa_pairs: Lista de diccionarios con 'question' y 'answer'
        include_system: Si True, incluye un mensaje de sistema con instrucciones
    
    Returns:
        Lista de diccionarios en formato OpenAI
    """
    openai_format = []
    
    for qa in qa_pairs:
        messages = []
        
        # Agregar mensaje de sistema (opcional pero recomendado)
        if include_system:
            messages.append({
                "role": "system",
                "content": SYSTEM_INSTRUCTION
            })
        
        # Agregar pregunta del usuario
        messages.append({
            "role": "user",
            "content": qa["question"]
        })
        
        # Agregar respuesta del asistente
        messages.append({
            "role": "assistant",
            "content": qa["answer"]
        })
        
        openai_format.append({"messages": messages})
    
    return openai_format


def save_openai_format(data: list[dict], output_path: Path):
    """Guarda los datos en formato JSONL para OpenAI."""
    # Crear directorio si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def validate_dataset(file_path: Path):
    """
    Valida que el dataset cumpla con los requisitos de OpenAI.
    
    Requisitos:
    - Mínimo 10 ejemplos
    - Formato JSONL válido
    - Cada línea contiene "messages"
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    num_examples = len(lines)
    
    print(f"\n{'='*60}")
    print(f"VALIDACIÓN DEL DATASET")
    print(f"{'='*60}")
    print(f"Total de ejemplos: {num_examples}")
    
    if num_examples < 10:
        print(f"⚠️  ADVERTENCIA: Se requieren mínimo 10 ejemplos (tienes {num_examples})")
    else:
        print(f"✓ Cumple con el mínimo de 10 ejemplos")
    
    if num_examples < 50:
        print(f"ℹ️  RECOMENDACIÓN: OpenAI recomienda 50-100 ejemplos para mejores resultados")
    else:
        print(f"✓ Tiene suficientes ejemplos ({num_examples}) para buen rendimiento")
    
    # Validar estructura
    try:
        for i, line in enumerate(lines[:5], 1):
            data = json.loads(line)
            assert "messages" in data, f"Línea {i} no contiene 'messages'"
            assert isinstance(data["messages"], list), f"Línea {i}: 'messages' debe ser una lista"
        print(f"✓ Formato JSONL válido")
        print(f"✓ Estructura de mensajes correcta")
    except Exception as e:
        print(f"✗ Error en la validación: {e}")
    
    print(f"{'='*60}\n")


def main():
    """Función principal para preparar datos de fine-tuning."""
    print(f"Cargando dataset desde: {INPUT_PATH}")
    
    # Cargar datos originales
    qa_pairs = load_qa_dataset(INPUT_PATH)
    print(f"Total de pares Q&A cargados: {len(qa_pairs)}")
    
    # Convertir al formato de OpenAI
    print(f"\nConvirtiendo al formato de OpenAI...")
    openai_data = convert_to_openai_format(qa_pairs, include_system=True)
    
    # Guardar en formato JSONL
    print(f"Guardando dataset en: {OUTPUT_PATH}")
    save_openai_format(openai_data, OUTPUT_PATH)
    
    # Validar el dataset generado
    validate_dataset(OUTPUT_PATH)
    
    # Mostrar ejemplo
    print(f"Ejemplo del primer registro:")
    print(json.dumps(openai_data[0], indent=2, ensure_ascii=False))
    
    print(f"\n✓ Dataset preparado correctamente!")
    print(f"\nSiguientes pasos:")
    print(f"1. Subir el archivo: {OUTPUT_PATH}")
    print(f"2. Crear un trabajo de fine-tuning en OpenAI")
    print(f"3. Seleccionar modelo base (ej: gpt-4o-mini-2024-07-18)")
    print(f"4. Esperar a que complete el entrenamiento")
    print(f"5. Evaluar el modelo fine-tuned con datos de prueba")


if __name__ == "__main__":
    main()

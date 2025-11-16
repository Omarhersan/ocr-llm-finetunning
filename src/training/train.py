"""
Script para entrenar un modelo de OpenAI mediante fine-tuning supervisado.

Este script:
1. Carga la API key desde el archivo .env
2. Sube el dataset de entrenamiento a OpenAI
3. Crea un trabajo de fine-tuning
4. Monitorea el progreso del entrenamiento
5. Guarda el ID del modelo fine-tuned

Documentación de referencia:
https://platform.openai.com/docs/guides/supervised-fine-tuning
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# Cargar variables de entorno
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Configuración
FINETUNE_DATA_PATH = Path(__file__).parent.parent.parent / "data/final_dataset/finetune_dataset.jsonl"
MODEL_INFO_PATH = Path(__file__).parent.parent.parent / "data/final_dataset/model_info.json"
BASE_MODEL = "gpt-4o-mini-2024-07-18"  # Modelo base recomendado para fine-tuning


def initialize_client():
    """Inicializa el cliente de OpenAI con la API key."""
    api_key = os.getenv("OPEN_AI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "No se encontró OPEN_AI_API_KEY en el archivo .env\n"
            "Asegúrate de que el archivo .env contenga: OPEN_AI_API_KEY=tu_api_key"
        )
    
    return OpenAI(api_key=api_key)


def upload_training_file(client: OpenAI, file_path: Path) -> str:
    """
    Sube el archivo de entrenamiento a OpenAI.
    
    Args:
        client: Cliente de OpenAI
        file_path: Ruta al archivo JSONL de entrenamiento
    
    Returns:
        ID del archivo subido
    """
    print(f"\n{'='*60}")
    print(f"SUBIENDO ARCHIVO DE ENTRENAMIENTO")
    print(f"{'='*60}")
    print(f"Archivo: {file_path}")
    print(f"Tamaño: {file_path.stat().st_size / 1024:.2f} KB")
    
    with open(file_path, "rb") as f:
        response = client.files.create(
            file=f,
            purpose="fine-tune"
        )
    
    print(f"✓ Archivo subido exitosamente")
    print(f"  File ID: {response.id}")
    print(f"  Filename: {response.filename}")
    print(f"  Status: {response.status}")
    
    return response.id


def create_finetune_job(client: OpenAI, training_file_id: str, model: str, suffix: str = None) -> str:
    """
    Crea un trabajo de fine-tuning.
    
    Args:
        client: Cliente de OpenAI
        training_file_id: ID del archivo de entrenamiento
        model: Modelo base a usar
        suffix: Sufijo opcional para el nombre del modelo (max 18 chars)
    
    Returns:
        ID del trabajo de fine-tuning
    """
    print(f"\n{'='*60}")
    print(f"CREANDO TRABAJO DE FINE-TUNING")
    print(f"{'='*60}")
    print(f"Modelo base: {model}")
    print(f"Training file: {training_file_id}")
    
    params = {
        "training_file": training_file_id,
        "model": model,
    }
    
    # Agregar sufijo personalizado si se proporciona
    if suffix:
        params["suffix"] = suffix[:18]  # OpenAI limita a 18 caracteres
        print(f"Sufijo del modelo: {params['suffix']}")
    
    response = client.fine_tuning.jobs.create(**params)
    
    print(f"✓ Trabajo de fine-tuning creado")
    print(f"  Job ID: {response.id}")
    print(f"  Status: {response.status}")
    print(f"  Created at: {response.created_at}")
    
    return response.id


def monitor_finetune_job(client: OpenAI, job_id: str, check_interval: int = 30):
    """
    Monitorea el progreso del trabajo de fine-tuning.
    
    Args:
        client: Cliente de OpenAI
        job_id: ID del trabajo de fine-tuning
        check_interval: Segundos entre cada verificación
    """
    print(f"\n{'='*60}")
    print(f"MONITOREANDO PROGRESO DEL ENTRENAMIENTO")
    print(f"{'='*60}")
    print(f"Job ID: {job_id}")
    print(f"Verificando cada {check_interval} segundos...")
    print(f"\nEsto puede tomar varios minutos. Presiona Ctrl+C para salir")
    print(f"(el entrenamiento continuará en OpenAI)")
    
    try:
        while True:
            job = client.fine_tuning.jobs.retrieve(job_id)
            
            print(f"\n[{time.strftime('%H:%M:%S')}] Status: {job.status}")
            
            if job.status == "succeeded":
                print(f"\n{'='*60}")
                print(f"✓ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
                print(f"{'='*60}")
                print(f"Modelo fine-tuned: {job.fine_tuned_model}")
                print(f"Training tokens: {job.trained_tokens if hasattr(job, 'trained_tokens') else 'N/A'}")
                return job
            
            elif job.status == "failed":
                print(f"\n{'='*60}")
                print(f"✗ ENTRENAMIENTO FALLIDO")
                print(f"{'='*60}")
                if hasattr(job, 'error') and job.error:
                    print(f"Error: {job.error}")
                return job
            
            elif job.status == "cancelled":
                print(f"\n{'='*60}")
                print(f"⚠ ENTRENAMIENTO CANCELADO")
                print(f"{'='*60}")
                return job
            
            else:
                # Estados: validating_files, queued, running
                if hasattr(job, 'trained_tokens') and job.trained_tokens:
                    print(f"  Tokens entrenados: {job.trained_tokens}")
            
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print(f"\n\n⚠ Monitoreo interrumpido por el usuario")
        print(f"El entrenamiento continúa en OpenAI")
        print(f"Puedes verificar el estado en: https://platform.openai.com/finetune")
        print(f"O ejecutar: monitor_job('{job_id}')")
        return None


def save_model_info(job_id: str, file_id: str, model_id: str = None):
    """
    Guarda la información del modelo fine-tuned en un archivo JSON.
    
    Args:
        job_id: ID del trabajo de fine-tuning
        file_id: ID del archivo de entrenamiento
        model_id: ID del modelo fine-tuned (si está disponible)
    """
    info = {
        "job_id": job_id,
        "training_file_id": file_id,
        "fine_tuned_model": model_id,
        "base_model": BASE_MODEL,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dashboard_url": f"https://platform.openai.com/finetune/{job_id}"
    }
    
    MODEL_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(MODEL_INFO_PATH, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Información del modelo guardada en: {MODEL_INFO_PATH}")


def list_finetune_jobs(client: OpenAI, limit: int = 10):
    """Lista los trabajos de fine-tuning recientes."""
    print(f"\n{'='*60}")
    print(f"TRABAJOS DE FINE-TUNING RECIENTES")
    print(f"{'='*60}")
    
    jobs = client.fine_tuning.jobs.list(limit=limit)
    
    for i, job in enumerate(jobs.data, 1):
        print(f"\n{i}. Job ID: {job.id}")
        print(f"   Status: {job.status}")
        print(f"   Model: {job.model}")
        print(f"   Fine-tuned model: {job.fine_tuned_model or 'En progreso...'}")
        print(f"   Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(job.created_at))}")


def main():
    """Función principal para el proceso de fine-tuning."""
    print(f"\n{'='*60}")
    print(f"INICIANDO PROCESO DE FINE-TUNING")
    print(f"{'='*60}")
    
    # Verificar que existe el archivo de datos
    if not FINETUNE_DATA_PATH.exists():
        print(f"\n✗ Error: No se encontró el archivo de entrenamiento")
        print(f"  Ruta esperada: {FINETUNE_DATA_PATH}")
        print(f"\nEjecuta primero: python prepare_finetune_data.py")
        return
    
    # Inicializar cliente
    try:
        client = initialize_client()
        print(f"✓ Cliente de OpenAI inicializado correctamente")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        return
    
    # Opción: Listar trabajos existentes
    print(f"\n¿Deseas ver los trabajos de fine-tuning existentes? (s/n)")
    if input().strip().lower() == 's':
        list_finetune_jobs(client)
        print(f"\n¿Continuar con nuevo entrenamiento? (s/n)")
        if input().strip().lower() != 's':
            return
    
    # 1. Subir archivo de entrenamiento
    try:
        file_id = upload_training_file(client, FINETUNE_DATA_PATH)
    except Exception as e:
        print(f"\n✗ Error al subir archivo: {e}")
        return
    
    # 2. Crear trabajo de fine-tuning
    try:
        suffix = "arkham-contract"  # Sufijo para identificar el modelo
        job_id = create_finetune_job(client, file_id, BASE_MODEL, suffix)
    except Exception as e:
        print(f"\n✗ Error al crear trabajo: {e}")
        return
    
    # 3. Guardar información inicial
    save_model_info(job_id, file_id)
    
    # 4. Monitorear progreso
    print(f"\n¿Deseas monitorear el progreso del entrenamiento? (s/n)")
    if input().strip().lower() == 's':
        result = monitor_finetune_job(client, job_id)
        
        # Actualizar información con el modelo final
        if result and result.status == "succeeded":
            save_model_info(job_id, file_id, result.fine_tuned_model)
            
            print(f"\n{'='*60}")
            print(f"SIGUIENTE PASO: PROBAR EL MODELO")
            print(f"{'='*60}")
            print(f"\nPuedes usar el modelo con:")
            print(f"  Model ID: {result.fine_tuned_model}")
            print(f"\nEjemplo de uso:")
            print(f'''
from openai import OpenAI
client = OpenAI(api_key="tu_api_key")

response = client.chat.completions.create(
    model="{result.fine_tuned_model}",
    messages=[
        {{"role": "system", "content": "Eres un asistente especializado en contratos de arrendamiento."}},
        {{"role": "user", "content": "¿Cuál es el plazo del contrato?"}}
    ]
)

print(response.choices[0].message.content)
            ''')
    else:
        print(f"\n✓ Trabajo de fine-tuning iniciado")
        print(f"\nPuedes monitorear el progreso en:")
        print(f"  Dashboard: https://platform.openai.com/finetune/{job_id}")
        print(f"\nO ejecutar este script nuevamente y seleccionar la opción de listar trabajos")


if __name__ == "__main__":
    main()

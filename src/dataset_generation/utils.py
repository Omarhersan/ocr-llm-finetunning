SECTION_QA_PROMPT = """
Genera un conjunto de {n} preguntas y respuestas basadas EXCLUSIVAMENTE 
en el siguiente texto de una cláusula de un contrato de arrendamiento. 

NO inventes información.
NO agregues elementos que no aparecen en el texto.

Devuelve un JSON válido con EXACTAMENTE esta estructura:

{{
  "data": [
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
  ]
}}

Título de la sección:
{header}

Contenido:
{text}
"""

ANNEX_QA_PROMPT = """
Genera {n} preguntas y respuestas (Q&A) basadas exclusivamente en 
la siguiente tabla de pagos del contrato (ANEXO 1).

NO inventes información.
NO agregues pagos que no existan.
NO infieras fechas fuera de la tabla.
Las respuestas deben contener valores exactos cuando sea posible.

Tabla:
{table}

Devuelve un JSON con EXACTAMENTE esta estructura:

{{
  "data": [
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
  ]
}}
"""

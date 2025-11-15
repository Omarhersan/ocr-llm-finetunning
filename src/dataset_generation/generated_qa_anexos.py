import json
import locale
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from openai import OpenAI
from utils import ANNEX_QA_PROMPT


class AnnexQAGenerator:
    """
    Generates Q&A pairs using the ANEXO 1 payment table.
    Combines deterministic Q&A + LLM-generated Q&A.
    """

    def __init__(
        self,
        annex_json: str = "data/sections/anexo_pagos.json",
        output_path: str = "data/generated_qa/annex_qa.jsonl",
        model: str = "gpt-4o-mini",
        llm_questions: int = 6,    # number of LLM-based extra Q&A
        openai_client = None
    ):
        self.annex_json = Path(annex_json)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.model = model
        self.llm_questions = llm_questions
        self.openai_client = openai_client

        self.table = []


    # --------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # --------------------------------------------------------
    def run(self):
        print(f"[*] Loading Annex table: {self.annex_json}")
        self.table = self.load_table()

        print("[*] Generating deterministic Q&A...")
        qa_deterministic = self.generate_deterministic_qa()

        print("[*] Generating LLM-based Q&A...")
        qa_llm = self.generate_llm_qa()

        final = qa_deterministic + qa_llm

        print(f"[✓] Annex Q&A generated: {len(final)} pairs")
        return final

    # --------------------------------------------------------
    # LOAD TABLE
    # --------------------------------------------------------
    def load_table(self):
        return json.loads(self.annex_json.read_text(encoding="utf-8"))

    # --------------------------------------------------------
    # DETERMINISTIC Q&A
    # --------------------------------------------------------
    def generate_deterministic_qa(self) -> List[Dict]:
        qa = []

        # Number of payments
        total_payments = len(self.table)
        qa.append({
            "question": "¿Cuántos pagos contempla el anexo de pagos?",
            "answer": f"El anexo incluye un total de {total_payments} pagos."
        })

        # First payment
        first = self.table[0]
        qa.append({
            "question": "¿Cuándo se debe realizar el primer pago?",
            "answer": f"El primer pago se debe realizar el {first['fecha']} por un monto de ${first['monto']:.2f}."
        })

        # Last payment
        last = self.table[-1]
        qa.append({
            "question": "¿Cuál es la fecha del último pago?",
            "answer": f"El último pago está programado para el {last['fecha']} por un monto de ${last['monto']:.2f}."
        })

        # Total amount
        total_amount = sum(row["monto"] for row in self.table)
        qa.append({
            "question": "¿Cuál es el monto total de todos los pagos del anexo?",
            "answer": f"El monto total acumulado de los pagos es de ${total_amount:,.2f}."
        })

        # Highest payment
        highest = max(self.table, key=lambda x: x["monto"])
        qa.append({
            "question": "¿Cuál es el pago más alto del anexo?",
            "answer": f"El pago más alto es de ${highest['monto']:.2f}, programado para el {highest['fecha']}."
        })

        return qa

    # --------------------------------------------------------
    # LLM Q&A
    # --------------------------------------------------------
    def generate_llm_qa(self) -> List[Dict]:
        prompt = ANNEX_QA_PROMPT.format(
            n=self.llm_questions,
            table=json.dumps(self.table, ensure_ascii=False, indent=2)
        )

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Eres un experto en contratos financieros y tablas de amortización."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        try:
            content = response.choices[0].message.content
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            
            # Handle both direct array and object with array
            if isinstance(data, list):
                qa_list = data
            elif isinstance(data, dict) and "data" in data:
                qa_list = data["data"]
            elif isinstance(data, dict) and "questions" in data:
                qa_list = data["questions"]
            elif isinstance(data, dict) and "qa" in data:
                qa_list = data["qa"]
            else:
                print(f"[!] Unexpected JSON structure: {data}")
                return []
                
        except Exception as e:
            print(f"[!] Error parsing LLM response: {e}")
            print(f"[!] Response content: {response.choices[0].message.content[:500]}")
            return []

        normalized = []
        for qa in qa_list:
            normalized.append({
                "question": qa["question"],
                "answer": qa["answer"]
            })
        return normalized
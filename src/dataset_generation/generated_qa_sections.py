import json
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from utils import SECTION_QA_PROMPT


class SectionQAGenerator:
    """
    Generates Q&A datasets for each contract section.
    """

    def __init__(
        self,
        sections_dir: str = "../../data/sections/",
        output_dir: str = "../../data/generated_qa/",
        model: str = "gpt-4o-mini",  # configurable
        questions_per_section: int = 8,
        openai_client = None
    ):
        self.sections_dir = Path(sections_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = model
        self.questions_per_section = questions_per_section
        self.openai_client = openai_client

    # --------------------------------------------------------
    # PUBLIC METHOD
    # --------------------------------------------------------
    def run(self):
        print(f"[*] Loading sections from: {self.sections_dir}")
        sections = self.load_sections()

        all_qa = []
        print(f"[*] Generating Q&A for {len(sections)} sections...")
        for filename, header, content in sections:
            qa_list = self.process_section(filename, header, content)
            all_qa.extend(qa_list)

        print(f"[✓] Q&A generation complete! Total: {len(all_qa)} pairs")
        return all_qa

    # --------------------------------------------------------
    # LOAD SECTIONS
    # --------------------------------------------------------
    def load_sections(self) -> List[tuple]:
        files = sorted(self.sections_dir.glob("section_*.txt"))

        sections = []
        for f in files:
            text = f.read_text(encoding="utf-8")
            header, body = text.split("\n", 1)
            sections.append((f.name.replace(".txt", ""), header.strip(), body.strip()))
        return sections

    # --------------------------------------------------------
    # PROCESS ONE SECTION
    # --------------------------------------------------------
    def process_section(self, filename: str, header: str, content: str):
        print(f"[*] Generating Q&A → {filename} ({header})")
        qa_list = self.generate_qa(header, content)
        return qa_list

    # --------------------------------------------------------
    # LLM CALL
    # --------------------------------------------------------
    def generate_qa(self, header: str, text: str) -> List[Dict]:
        """
        Generates a list of Q&A pairs using the given text.
        """

        prompt = SECTION_QA_PROMPT.format(
            header=header,
            text=text,
            n=self.questions_per_section
        )

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Eres un abogado experto en contratos de arrendamiento."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Parse JSON safely
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
            print(f"[!] Failed to parse JSON. Error: {e}")
            print(f"[!] Response content: {response.choices[0].message.content[:500]}")
            return []

        # Normalize to final dataset format
        normalized = []
        for qa in qa_list:
            normalized.append({
                "question": qa["question"],
                "answer": qa["answer"]
            })

        return normalized



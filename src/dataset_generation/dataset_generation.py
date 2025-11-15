import json
import os
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from generated_qa_anexos import AnnexQAGenerator
from generated_qa_sections import SectionQAGenerator


class QAGenerator:
    """
    Generates Q&A datasets for each contract section.
    """

    def __init__(
        self,
        sections_dir: str = "../../data/sections/",
        output_dir: str = "../../data/generated_qa/",
        model: str = "gpt-4o-mini",  # configurable
        questions_per_section: int = 20,
        llm_questions_annex: int = 10
    ):
        self.sections_dir = Path(sections_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = model
        self.questions_per_section = questions_per_section
        self.llm_questions_annex = llm_questions_annex
        
        # Load API key from .env file
        load_dotenv()
        api_key = os.getenv("OPEN_AI_API_KEY")
        if not api_key:
            raise ValueError("OPEN_AI_API_KEY not found in .env file")
        
        self.openai_client = OpenAI(api_key=api_key)    
    
    def run(self):
        print("[*] Starting Q&A generation pipeline...\n")
        
        # Generate Q&A for sections
        print("=" * 60)
        print("GENERATING SECTION Q&A")
        print("=" * 60)
        section_qa_generator = SectionQAGenerator(
            sections_dir=self.sections_dir,
            output_dir=self.output_dir,
            model=self.model,
            questions_per_section=self.questions_per_section,
            openai_client=self.openai_client
        )
        section_qa = section_qa_generator.run()

        # Generate Q&A for annexes
        print("\n" + "=" * 60)
        print("GENERATING ANNEX Q&A")
        print("=" * 60)
        annex_qa_generator = AnnexQAGenerator(
            annex_json=self.sections_dir / "payment_table.json",
            output_path=self.output_dir / "annex_qa.jsonl",
            model=self.model,
            llm_questions=self.llm_questions_annex,
            openai_client=self.openai_client
        )
        annex_qa = annex_qa_generator.run()
        
        # Merge datasets
        print("\n" + "=" * 60)
        print("MERGING DATASETS")
        print("=" * 60)
        self.merge_and_save(section_qa, annex_qa)

    
    def merge_and_save(self, section_qa: List[Dict], annex_qa: List[Dict]):
        print("[*] Merging Q&A datasets...")
        
        merged_entries = section_qa + annex_qa
        
        print(f"   Section Q&A pairs: {len(section_qa)}")
        print(f"   Annex Q&A pairs: {len(annex_qa)}")
        print(f"   Total Q&A pairs: {len(merged_entries)}")
        
        # Save merged dataset
        output_file = self.output_dir / "merged_qa_dataset.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            for item in merged_entries:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        print(f"\n[✓] Merged dataset saved: {output_file}")
        print(f"[✓] Total Q&A pairs: {len(merged_entries)}\n")


    # --------------------------------------------------------
if __name__ == "__main__":
        qa_generator = QAGenerator()
        qa_generator.run()
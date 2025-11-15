
import re
from pathlib import Path
from preprocessing.constants import ROMAN, SECTION_KEYWORDS

class SplitSections():
    def __init__(self, input_path:str, output_dir:str) -> None:
        self.INPUT_PATH = input_path
        self.OUTPUT_DIR = output_dir
        self.roman = ROMAN
        self.section_keywords = SECTION_KEYWORDS
        self.text = None
        self.sections = []

    def run(self):
        print("[*] Reading clean contract text...")
        full_text = Path(self.INPUT_PATH).read_text(encoding="utf-8")

        print("[*] Removing Annex 1 (payment table)...")
        cleaned_text = self.strip_anexo()

        print("[*] Splitting into sections...")
        sections = self.split_into_sections()

        if not sections:
            raise ValueError("Could not identify sections. Check OCR or detection logic.")

        print(f"[✓] Sections detected: {len(self.sections)}")

        print("[*] Saving sections...")
        self.save_sections()

    def clean_header_line(self, line: str) -> str:
        """ 
        Normalizes headers damaged by OCR
        """

        # Remove junk characters
        line = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑ0-9\.\s]", "", line)
        line = line.strip()

        # Convert to uppercase for stable detection
        upper = line.upper()

        # Detect patterns like "CLAUSULA", "DECLARACION"
        for kw in self.section_keywords:
            if kw in upper:
                return kw

        # Detect numbered headers like "I. DECLARACIONES"
        m = re.match(r"([IVX]+)\.\s+(.+)", upper)
        if m:
            numeral, text = m.groups()
            return f"{numeral}. {text.strip()}"

        # Detect incomplete headers like "I DECLARACIONES"
        m = re.match(r"([IVX]+)\s+(.+)", upper)
        if m:
            numeral, text = m.groups()
            return f"{numeral}. {text.strip()}"

        return None

    def strip_anexo(self) -> str:
        """
        Removes the Annex 1 block (the table)
        """
        cleaned = re.sub(
            r"DE\s+ACUERDO\s+A\s+LA\s+TABLA.*?PLAZO\s+BASICO",
            "",
            self.text,
            flags=re.DOTALL | re.IGNORECASE
        )
        return cleaned

    def split_into_sections(self) -> None:
        """
        Splits the cleaned text into sections based on detected headers
        """

        lines = self.text.split("\n")

        current_header = None
        current_content = []
        roman_index = 0

        for line in lines:
            header = self.clean_header_line(line)

            if header:
                # If there was a previous section, save it
                if current_header:
                    self.sections.append((current_header, "\n".join(current_content).strip()))
                    current_content = []

                # Ensure Roman numeral
                if not re.match(r"^[IVX]+\.", header):
                    numeral = self.roman[roman_index]
                    header = f"{numeral}. {header}"
                    roman_index += 1
                else:
                    # If it already has one, adjust roman_index
                    roman_index += 1

                current_header = header

            else:
                # Not a header → part of the section
                if current_header:  
                    current_content.append(line.strip())

        # Save last section
        if current_header and current_content:
            self.sections.append((current_header, "\n".join(current_content).strip()))

    def save_sections(self):
        Path(self.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

        for i, (header, content) in enumerate(self.sections, start=1):
            filename = Path(OUTPUT_DIR) / f"section_{i:02d}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(header + "\n\n" + content)

        print(f"[✓] {len(self.sections)} sections generated in: {self.OUTPUT_DIR}")
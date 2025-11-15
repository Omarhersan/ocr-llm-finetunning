import re
from pathlib import Path
from constants import ROMAN, LEGAL_HEADERS, SPANISH_VERB_ENDINGS, ORDINAL_NUMBERS, ORDINAL_NUMBERS

class SplitSections:
    def __init__(self, input_path: str, output_dir: str) -> None:
        self.INPUT_PATH = input_path
        self.OUTPUT_DIR = output_dir
        self.text = None
        self.sections = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------
    def run(self):
        print("[*] Reading clean contract text...")
        self.text = Path(self.INPUT_PATH).read_text(encoding="utf-8")

        print("[*] Removing Annex 1 (payment table)...")
        self.text = self.strip_anexo()

        print("[*] Splitting into sections...")
        self.split_into_sections()

        print("[*] Merging small sections...")
        self.sections = self.merge_small_sections(self.sections)

        if not self.sections:
            raise ValueError("Could not identify sections. Check OCR or detection logic.")

        print("[✓] Sections detected:", len(self.sections))

        print("[*] Saving sections...")
        self.save_sections()

    # --------------------------------------------------------
    # REMOVE ANEXO
    # --------------------------------------------------------
    def strip_anexo(self) -> str:
        return re.sub(
            r"DE\s+ACUERDO\s+A\s+LA\s+TABLA.*?PLAZO\s+BASICO",
            "",
            self.text,
            flags=re.DOTALL | re.IGNORECASE
        )

    # --------------------------------------------------------
    # HEADER DETECTION
    # --------------------------------------------------------
    def is_real_legal_header(self, line: str) -> str | None:
        """
        Determines if a line is a legitimate legal header.
        Rejects fragments like:
        - “ATENTAR CONTRA AREAS NATURALES…”
        """

        clean = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑ0-9\s]", "", line).strip().upper()
        if not clean or len(clean) < 5:
            return None

        # Reject "CLAUSULAS" or "CLÁUSULAS" alone (they should have ordinals)
        if clean in ["CLAUSULAS", "CLÁUSULAS", "CLAUSULA", "CLÁUSULA"]:
            return None

        # Reject lines containing verb endings (AR, ER, IR)
        for token in clean.split():
            if len(token) > 4 and token.endswith(SPANISH_VERB_ENDINGS):
                return None

        # Exact match
        if clean in LEGAL_HEADERS:
            return clean

        # Fuzzy match (OCR damage)
        for header in LEGAL_HEADERS:
            if header in clean and abs(len(clean) - len(header)) < 10:
                return header

        return None
    
    def is_ordinal_clause(self, line: str) -> str | None:
        """
        Detects clause headers like "CLAUSULAS PRIMERA. DEFINICIONES"
        Returns the full header if found.
        """
        clean = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑ0-9\s\.\\_]", "", line).strip().upper()
        
        # Check if line starts with "CLAUSULA" or "CLÁUSULA"
        if not (clean.startswith("CLAUSULA") or clean.startswith("CLÁUSULA")):
            return None
        
        # Check if it contains an ordinal number
        for ordinal in ORDINAL_NUMBERS:
            if ordinal in clean:
                return clean
        
        return None

    # --------------------------------------------------------
    # MAIN SPLITTING LOGIC
    # --------------------------------------------------------
    def split_into_sections(self) -> None:
        lines = self.text.split("\n")

        current_header = None
        current_content = []
        section_index = 0

        for line in lines:
            # Check for ordinal clause first (more specific)
            ordinal_clause = self.is_ordinal_clause(line)
            if ordinal_clause:
                if current_header:
                    self.sections.append(
                        (current_header, "\n".join(current_content).strip())
                    )
                    current_content = []

                section_index += 1
                numeral = ROMAN[section_index - 1] if section_index <= len(ROMAN) else str(section_index)
                current_header = f"{numeral}. {ordinal_clause}"
                continue
            
            # Check for general legal header
            header_candidate = self.is_real_legal_header(line)
            if header_candidate:
                if current_header:
                    self.sections.append(
                        (current_header, "\n".join(current_content).strip())
                    )
                    current_content = []

                section_index += 1
                numeral = ROMAN[section_index - 1] if section_index <= len(ROMAN) else str(section_index)
                current_header = f"{numeral}. {header_candidate}"
                continue

            if current_header:
                current_content.append(line.strip())

        if current_header and current_content:
            self.sections.append((current_header, "\n".join(current_content).strip()))

    # --------------------------------------------------------
    # MERGE TOO-SMALL SECTIONS
    # --------------------------------------------------------
    def merge_small_sections(self, sections, threshold=250):
        merged = []
        buffer_header, buffer_text = None, ""

        for header, content in sections:
            if buffer_header is None:
                buffer_header = header
                buffer_text = content
                continue

            if len(buffer_text) < threshold:
                buffer_text += "\n" + header + "\n" + content
            else:
                merged.append((buffer_header, buffer_text))
                buffer_header, buffer_text = header, content

        if buffer_header:
            merged.append((buffer_header, buffer_text))

        return merged

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------
    def save_sections(self):
        Path(self.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

        for i, (header, content) in enumerate(self.sections, start=1):
            filename = Path(self.OUTPUT_DIR) / f"section_{i:02d}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(header + "\n\n" + content)

        print(f"[✓] {len(self.sections)} sections generated in: {self.OUTPUT_DIR}")

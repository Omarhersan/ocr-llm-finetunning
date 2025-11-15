import os
import re
from pathlib import Path

INPUT_PATH = "../../data/cleaned/CONTRATO_AP000000718_cleaned.txt"
OUTPUT_DIR = "../../data/sections/"

# ------------------------------------------------------------
# Section header detection patterns
# ------------------------------------------------------------

HEADER_PATTERNS = [
    # Spanish legal ordinals (already normalized in cleaning)
    r"^(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SEPTIMA|OCTAVA|NOVENA|DECIMA(\s+\w+)?|VIGESIMA(\s+\w+)?)[\.\s]",

    # Annexes
    r"^ANEXO\s+[A-Z0-9\.]+",

    # Secciones inside annexes
    r"^SECCION\s+[A-Z0-9]+\.",

    # Roman numeral headings (I., II., III., IV.)
    r"^[IVXLC]+\.\s+",
]

compiled_patterns = [re.compile(p) for p in HEADER_PATTERNS]


def is_header(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False

    for pattern in compiled_patterns:
        if pattern.match(stripped):
            return True

    return False


# ------------------------------------------------------------
# Load file
# ------------------------------------------------------------
def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------
# Split by detected headers
# ------------------------------------------------------------
def split_sections(text: str):
    lines = text.split("\n")
    sections = []
    current_title = None
    current_body = []

    intro_buffer = []   # text before first header encountered
    found_first_header = False

    for line in lines:
        if is_header(line):
            if not found_first_header:
                # INTRO section
                if intro_buffer:
                    sections.append(("INTRODUCCION", "\n".join(intro_buffer).strip()))
                found_first_header = True

            # save previous section if exists
            if current_title:
                sections.append((current_title, "\n".join(current_body).strip()))

            current_title = line.strip()
            current_body = []
        else:
            if not found_first_header:
                intro_buffer.append(line)
            else:
                if current_title:
                    current_body.append(line)

    # flush last section
    if current_title and current_body:
        sections.append((current_title, "\n".join(current_body).strip()))

    return sections



# ------------------------------------------------------------
# Save each section as its own file
# ------------------------------------------------------------
def save_sections(sections):
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    for idx, (title, text) in enumerate(sections, start=1):
        filename = f"section_{idx:02d}.txt"
        outpath = os.path.join(OUTPUT_DIR, filename)

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(f"{title}\n\n{text}")

    print(f"[✓] Saved {len(sections)} sections to {OUTPUT_DIR}")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
if __name__ == "__main__":
    print("[*] Loading cleaned lease text...")
    text = load_text(INPUT_PATH)

    print("[*] Splitting sections...")
    sections = split_sections(text)

    print(f"[*] Identified {len(sections)} sections.")

    save_sections(sections)

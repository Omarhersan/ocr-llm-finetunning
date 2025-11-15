import re
import unicodedata
from pathlib import Path

RAW_OCR_PATH = "../../data/ocr/CONTRATO_AP000000718_ocr.txt"
CLEAN_PATH = "../../data/cleaned/CONTRATO_AP000000718_cleaned.txt"


# ------------------------------------------------------------
# Canonical Spanish ordinals for legal clauses
# ------------------------------------------------------------
ORDINALS = {
    # 1–10
    "PRIMERA": ["PRIMERO", "PRIMERA", "PRAIMERA"],
    "SEGUNDA": ["SEGUNDA", "SEGJNDA", "SEGU NDA"],
    "TERCERA": ["TERCERA", "TERECERA", "TERCE RA"],
    "CUARTA": ["CUARTA", "GUARTA", "CUA RTA"],
    "QUINTA": ["QUINTA"],
    "SEXTA": ["SEXTA"],
    "SEPTIMA": ["SEPTIMA", "SÉPTIMA", "SEPTMIA", "SEPTlMA", "SECTIMA"],
    "OCTAVA": ["OCTAVA"],
    "NOVENA": ["NOVENA", "NOVFNA"],

    # 10–19
    "DECIMA": ["DECIMA", "DÉCIMA", "DEGIMA", "DECIM A", "D E C I M A"],
    "DECIMA PRIMERA": ["DECIMA PRIMERA", "DECIMA PRIM E R A"],
    "DECIMA SEGUNDA": ["DECIMA SEGUNDA"],
    "DECIMA TERCERA": ["DECIMA TERCERA"],
    "DECIMA CUARTA": ["DECIMA CUARTA"],
    "DECIMA QUINTA": ["DECIMA QUINTA", "DECIMA QUINTA."],
    "DECIMA SEXTA": ["DECIMA SEXTA"],
    "DECIMA SEPTIMA": ["DECIMA SEPTIMA", "DECIMA SÉPTIMA"],
    "DECIMA OCTAVA": ["DECIMA OCTAVA"],
    "DECIMA NOVENA": ["DECIMA NOVENA", "DECIMANOVENA"],

    # 20–25
    "VIGESIMA": ["VIGESIMA"],
    "VIGESIMA PRIMERA": ["VIGESIMA PRIMERA"],
    "VIGESIMA SEGUNDA": ["VIGESIMA SEGUNDA"],
    "VIGESIMA TERCERA": ["VIGESIMA TERCERA"],
    "VIGESIMA CUARTA": ["VIGESIMA CUARTA"],
    "VIGESIMA QUINTA": ["VIGESIMA QUINTA"],
}


# Reverse lookup dictionary
ORDINAL_LOOKUP = {}
for canonical, variants in ORDINALS.items():
    for v in variants:
        ORDINAL_LOOKUP[v.upper()] = canonical


# ------------------------------------------------------------
# Normalization helpers
# ------------------------------------------------------------
def normalize_unicode(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return text


def fix_ocr_noise(text: str) -> str:
    rules = [
        (r"ﬁ|ﬂ", ""),        # broken ligatures
        (r"[■◆●◦▫▪]", ""),   # bullets
        (r"\t+", " "),
        (r" +", " "),
        (r"…", "..."),
        (r"\.{2,}", "."),
        (r"-{2,}", "-"),
        (r"[·•]", "-"),
    ]
    for pattern, repl in rules:
        text = re.sub(pattern, repl, text)
    return text


# ------------------------------------------------------------
# Normalize Roman numerals (OCR variants: Il., l., III,, IV..)
# ------------------------------------------------------------
def normalize_roman(line: str) -> str:
    # Common OCR mistakes
    line = re.sub(r"^f\.", "I.", line)
    line = re.sub(r"^Il[\.,\-\s]", "II. ", line)
    line = re.sub(r"^Il[\.,\-\s]", "II. ", line)
    line = re.sub(r"^[l1][\.,\-\s]", "I. ", line)
    line = re.sub(r"^III[,\.]+", "III. ", line)
    line = re.sub(r"^IV[,\.]+", "IV. ", line)
    line = re.sub(r"V\.{2,}", "V. ", line)
    return line


# ------------------------------------------------------------
# Normalize clause ordinals
# ------------------------------------------------------------
def normalize_ordinals(line: str) -> str:
    u = line.upper().strip()

    for variant, canonical in ORDINAL_LOOKUP.items():
        if u.startswith(variant):
            # remove trailing punctuation
            rest = u[len(variant):].lstrip(" .,-:")
            if rest:
                return f"{canonical}. {rest}"
            return f"{canonical}."

    return line


# ------------------------------------------------------------
# Normalize SECCION and ANEXO headings
# ------------------------------------------------------------
def normalize_seccion_anexo(line: str) -> str:
    u = line.upper()

    # SECCION I-- DESCRIPCION → SECCION I. DESCRIPCION
    if u.startswith("SECCION"):
        u = re.sub(r"SECCION\s+([A-Z0-9]+)[\.\-\s]*", r"SECCION \1. ", u)
        return u.strip()

    # ANEXO
    if u.startswith("ANEXO"):
        u = re.sub(r"ANEXO\s+([A-Z0-9\.]+)", r"ANEXO \1", u)
        return u.strip()

    return line


# ------------------------------------------------------------
# Join multi-line headings
# ------------------------------------------------------------
def merge_multiline_titles(lines):
    merged = []
    buffer = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if buffer:
                merged.append(buffer)
                buffer = None
            merged.append("")
            continue

        is_title_line = bool(re.match(r"^[A-ZÁÉÍÓÚÑ0-9][A-ZÁÉÍÓÚÑ0-9 \.\-]{3,}$", stripped))

        if is_title_line:
            # A line that looks like a title
            if buffer:
                buffer += " " + stripped
            else:
                buffer = stripped
        else:
            if buffer:
                merged.append(buffer)
                buffer = None
            merged.append(line)

    if buffer:
        merged.append(buffer)

    return merged


# ------------------------------------------------------------
# Remove page numbers (1/19, 3/22)
# ------------------------------------------------------------
def remove_page_numbers(line: str) -> bool:
    if re.match(r"^\s*\d+/\d+\s*$", line.strip()):
        return True
    return False


# ------------------------------------------------------------
# Main cleaning pipeline
# ------------------------------------------------------------
def clean_text(text: str) -> str:
    text = normalize_unicode(text)
    text = fix_ocr_noise(text)

    # Line by line normalization
    lines = []
    for line in text.split("\n"):
        if remove_page_numbers(line):
            continue

        line = normalize_roman(line)
        line = normalize_seccion_anexo(line)
        line = normalize_ordinals(line)

        lines.append(line)

    # Merge multiline titles
    lines = merge_multiline_titles(lines)

    # Collapse excessive blank lines
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


# ------------------------------------------------------------
# Read + Write
# ------------------------------------------------------------
def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_file(text: str, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    raw = read_file(RAW_OCR_PATH)
    cleaned = clean_text(raw)
    save_file(cleaned, CLEAN_PATH)
    print(f"[✓] Cleaned text saved to {CLEAN_PATH}")

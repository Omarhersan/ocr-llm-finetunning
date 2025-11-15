import re
import json
import csv
from pathlib import Path

INPUT_PATH = "../../data/cleaned/CONTRATO_AP000000718_cleaned.txt"
OUTPUT_JSON = "../../data/sections/anexo_pagos.json"
OUTPUT_CSV = "../../data/sections/anexo_pagos.csv"

# ------------------------------------------------------------
# Meses válidos en español (para regex)
# ------------------------------------------------------------
MESES = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "septiembre|octubre|noviembre|diciembre"
)

# Fecha en español con errores comunes del OCR
DATE_REGEX = re.compile(
    rf"(\d{{1,2}})\s*de\s*({MESES})\s*de\s*(20\d{{2}})",
    flags=re.IGNORECASE
)

# Cantidad tipo $91,870.00 o $25000.00 o $91.870,00
AMOUNT_REGEX = re.compile(
    r"\$\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})"
)

# ------------------------------------------------------------
# Limpieza previa del texto del anexo
# ------------------------------------------------------------
def clean_table_block(text: str) -> list:
    lines = text.split("\n")

    cleaned = []
    for line in lines:
        line = line.replace("[", " ").replace("]", " ")
        line = line.replace("|", " ").replace("—", " ")
        line = line.replace("_", " ").replace("~", " ")
        line = line.replace("'", " ").replace('"', " ")
        line = re.sub(r"\s+", " ", line).strip()

        # ruido típico del OCR dentro de tablas
        noise_tokens = ["pm", "Ss", "LS", "g", "SS", "pe", "Sd"]
        for n in noise_tokens:
            if line.startswith(n + " "):
                line = line[len(n)+1:]

        if line:
            cleaned.append(line)

    return cleaned


# ------------------------------------------------------------
# Extraer filas válidas (fecha + monto)
# ------------------------------------------------------------
def extract_rows(lines):
    rows = []

    for line in lines:
        date_match = DATE_REGEX.search(line)
        amount_match = AMOUNT_REGEX.search(line)

        if not date_match or not amount_match:
            continue

        fecha = " ".join(date_match.groups())  # (día, mes, año)
        monto = amount_match.group()

        # Intentar obtener número de pago (si existe)
        num_match = re.match(r"^\d{1,2}", line)
        numero = int(num_match.group()) if num_match else None

        rows.append({
            "numero": numero,
            "fecha": fecha,
            "monto_raw": monto,
            "original_line": line
        })

    return rows


# ------------------------------------------------------------
# Normalización del monto
# ------------------------------------------------------------
def normalize_amount(a: str) -> float:
    # $91,870.00 → "91870.00"
    clean = a.replace("$", "").replace(" ", "")
    clean = clean.replace(",", "").replace(".", "")[:-2] + "." + clean[-2:]
    return float(clean)


# ------------------------------------------------------------
# Reconstrucción de la tabla completa
# ------------------------------------------------------------
def reconstruct_table(rows):
    # Ordenar por fecha detectada (año, mes, día)
    import datetime

    def parse_fecha(f):
        d, m, y = f.split(" ")
        meses_map = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        return datetime.date(int(y), meses_map[m.lower()], int(d))

    rows_sorted = sorted(rows, key=lambda r: parse_fecha(r["fecha"]))

    # Rellenar número de pago faltantes
    counter = 1
    for r in rows_sorted:
        if r["numero"] is None:
            r["numero"] = counter
        counter += 1

    # Limpiar y normalizar cantidades
    for r in rows_sorted:
        r["monto"] = normalize_amount(r["monto_raw"])
        del r["monto_raw"]

    return rows_sorted


# ------------------------------------------------------------
# Guardar archivo JSON
# ------------------------------------------------------------
def save_json(rows, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=4)


# ------------------------------------------------------------
# Guardar CSV
# ------------------------------------------------------------
def save_csv(rows, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["numero", "fecha", "monto"])
        for r in rows:
            writer.writerow([r["numero"], r["fecha"], r["monto"]])


# ------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------
if __name__ == "__main__":
    print("[*] Leyendo texto del contrato...")
    full_text = Path(INPUT_PATH).read_text(encoding="utf-8")

    print("[*] Extrayendo sección ANEXO (tabla de pagos)...")
    # Heurística: buscar desde la frase "DE ACUERDO A LA TABLA" hasta "PLAZO BASICO" o similar
    import re
    m = re.search(r"DE. ACUERDO A LA TABLA.*?PLAZO BASICO", full_text, flags=re.DOTALL | re.IGNORECASE)

    if not m:
        raise ValueError("No se encontró el bloque de tabla del anexo. Ajusta la regex del anexo.")

    table_block = m.group()

    print("[*] Limpiando líneas del anexo...")
    lines = clean_table_block(table_block)

    print("[*] Extrayendo filas válidas...")
    rows = extract_rows(lines)

    if not rows:
        raise ValueError("No se pudieron identificar filas de tabla. Revisa el OCR o ajusta las regex.")

    print(f"[✓] Filas detectadas: {len(rows)}")

    print("[*] Reconstruyendo tabla...")
    table = reconstruct_table(rows)

    print("[*] Guardando JSON...")
    save_json(table, OUTPUT_JSON)

    print("[*] Guardando CSV...")
    save_csv(table, OUTPUT_CSV)

    print(f"[✓] ¡Tabla reconstruida correctamente!\nJSON → {OUTPUT_JSON}\nCSV → {OUTPUT_CSV}")

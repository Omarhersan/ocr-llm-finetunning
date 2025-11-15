import re
import json
import csv
from pathlib import Path
from preprocessing.constants import MONTHS

class TableExtractor:
    """Extracts and reconstructs payment tables from cleaned contract text."""
    
    def __init__(self, input_path: str, output_json: str, output_csv: str):
        self.input_path = input_path
        self.output_json = output_json
        self.output_csv = output_csv
        self.text = None
        self.months = MONTHS
        
        # Spanish date format with common OCR errors
        self.DATE_REGEX = re.compile(
            rf"(\d{{1,2}})\s*de\s*({self.months})\s*de\s*(20\d{{2}})",
            flags=re.IGNORECASE
        )
        
        # Amount format like $91,870.00 or $25000.00 or $91.870,00
        self.AMOUNT_REGEX = re.compile(
            r"\$\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})"
        )

    def load_text(self):
        """Loads the contract text from file."""
        self.text = Path(self.input_path).read_text(encoding="utf-8")
    
    def clean_table_block(self, table_text: str) -> list:

        """Pre-cleaning of annex text."""
        lines = table_text.split("\n")
        cleaned = []
        for line in lines:
            line = line.replace("[", " ").replace("]", " ")
            line = line.replace("|", " ").replace("—", " ")
            line = line.replace("_", " ").replace("~", " ")
            line = line.replace("'", " ").replace('"', " ")
            line = re.sub(r"\s+", " ", line).strip()
            
            # typical OCR noise inside tables
            noise_tokens = ["pm", "Ss", "LS", "g", "SS", "pe", "Sd"]
            for n in noise_tokens:
                if line.startswith(n + " "):
                    line = line[len(n)+1:]
            
            if line:
                cleaned.append(line)
        
        return cleaned
    
    def extract_rows(self, lines):
        """Extract valid rows (date + amount)."""
        rows = []
        
        for line in lines:
            date_match = self.DATE_REGEX.search(line)
            amount_match = self.AMOUNT_REGEX.search(line)
            
            if not date_match or not amount_match:
                continue
            
            fecha = " ".join(date_match.groups())  # (day, month, year)
            monto = amount_match.group()
            
            # Try to get payment number (if exists)
            num_match = re.match(r"^\d{1,2}", line)
            numero = int(num_match.group()) if num_match else None
            
            rows.append({
                "numero": numero,
                "fecha": fecha,
                "monto_raw": monto,
                "original_line": line
            })
        
        return rows
    
    def normalize_amount(self, a: str) -> float:
        """Amount normalization."""
        # $91,870.00 → "91870.00"
        clean = a.replace("$", "").replace(" ", "")
        clean = clean.replace(",", "").replace(".", "")[:-2] + "." + clean[-2:]
        return float(clean)
    
    def reconstruct_table(self, rows):
        """Full table reconstruction."""
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
        
        # Fill missing payment numbers
        counter = 1
        for r in rows_sorted:
            if r["numero"] is None:
                r["numero"] = counter
            counter += 1
        
        # Clean and normalize amounts
        for r in rows_sorted:
            r["monto"] = self.normalize_amount(r["monto_raw"])
            del r["monto_raw"]
        
        return rows_sorted
    
    def save_json(self, rows, path):
        """Save JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=4)
    
    def save_csv(self, rows, path):
        """Save CSV."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["numero", "fecha", "monto"])
            for r in rows:
                writer.writerow([r["numero"], r["fecha"], r["monto"]])
    
    def run(self):
        """Main extraction pipeline."""
        print("[*] Reading contract text...")
        self.load_text()
        full_text = self.text
        
        print("[*] Extracting ANNEX section (payment table)...")
        m = re.search(r"DE. ACUERDO A LA TABLA.*?PLAZO BASICO", full_text, flags=re.DOTALL | re.IGNORECASE)
        
        if not m:
            raise ValueError("Annex table block not found. Adjust the annex regex.")
        
        table_block = m.group()
        
        print("[*] Cleaning annex lines...")
        lines = self.clean_table_block(table_block)
        
        print("[*] Extracting valid rows...")
        rows = self.extract_rows(lines)
        
        if not rows:
            raise ValueError("Could not identify table rows. Review OCR or adjust regex.")
        
        print(f"[✓] Detected rows: {len(rows)}")
        
        print("[*] Reconstructing table...")
        table = self.reconstruct_table(rows)
        
        print("[*] Saving JSON...")
        self.save_json(table, self.output_json)
        
        print("[*] Saving CSV...")
        self.save_csv(table, self.output_csv)
        
        print("[*] Reconstructing text without table...")
        text_without_table = full_text.replace(table_block, "")
        
        print(f"[✓] Table successfully reconstructed!\nJSON → {self.output_json}\nCSV → {self.output_csv}")
        return text_without_table

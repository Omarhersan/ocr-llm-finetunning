# Constants used in preprocessing steps
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]

# List of keywords to identify section headers in the contract
SECTION_KEYWORDS = [
    "DECLARACIONES",
    "CLAUSULAS",
    "CLÁUSULAS",
    "OBJETO",
    "OBLIGACIONES",
    "OBLIGACIONES DEL ARRENDATARIO",
    "OBLIGACIONES DEL ARRENDADOR",
    "VIGENCIA",
    "RENTAS",
    "GARANTÍAS",
    "JURISDICCIÓN",
    "DOMICILIOS",
    "CONFIDENCIALIDAD",
]

# PATHS
INPUT_PATH = "data/cleaned/lease_cleaned.txt"
OUTPUT_DIR = "data/sections/"


# Months in Spanish for date parsing
MONTHS = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "septiembre|octubre|noviembre|diciembre"
)
        
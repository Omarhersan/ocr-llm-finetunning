ROMAN = [
    "I","II","III","IV","V","VI","VII","VIII","IX","X",
    "XI","XII","XIII","XIV","XV","XVI"
]

LEGAL_HEADERS = [
    "DECLARACIONES",
    "CLAUSULAS", "CLÁUSULAS",
    "OBJETO",
    "VIGENCIA",
    "RENTA", "RENTAS",
    "GARANTIAS", "GARANTÍAS",
    "DEPOSITOS", "DEPÓSITOS",
    "SEGUROS",
    "MANTENIMIENTO",
    "OBLIGACIONES DEL ARRENDATARIO",
    "OBLIGACIONES DEL ARRENDADOR",
    "PENALIZACIONES",
    "INCUMPLIMIENTO",
    "JURISDICCION", "JURISDICCIÓN",
    "DOMICILIOS",
    "CONFIDENCIALIDAD"
]

SPANISH_VERB_ENDINGS = ("AR", "ER", "IR")

ORDINAL_NUMBERS = [
    "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
    "SEXTA", "SEPTIMA", "SÉPTIMA", "OCTAVA", "NOVENA", "DECIMA", "DÉCIMA",
    "UNDECIMA", "UNDÉCIMA", "DUODECIMA", "DUODÉCIMA",
    "DECIMOTERCERA", "DECIMOCUARTA", "DECIMOQUINTA",
    "DECIMOSEXTA", "DECIMOSEPTIMA", "DECIMOSÉPTIMA",
    "DECIMOCTAVA", "DECIMONOVENA", "VIGESIMA", "VIGÉSIMA"
]

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
INPUT_PATH = "../../data/cleaned/CONTRATO_AP000000718_cleaned.txt"
OUTPUT_DIR = "../../data/sections/"
OUTPUT_JSON = "../../data/sections/payment_table.json"
OUTPUT_CSV = "../../data/sections/payment_table.csv"


# Months in Spanish for date parsing
MONTHS = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "septiembre|octubre|noviembre|diciembre"
)
        
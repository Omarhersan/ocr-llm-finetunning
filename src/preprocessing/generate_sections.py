from pathlib import Path
from constants import INPUT_PATH, OUTPUT_JSON, OUTPUT_CSV, OUTPUT_DIR
from table_extraction import TableExtractor
from split_sections import SplitSections



if __name__ == "__main__":
    # Step 1: Extract payment table
    text_without_table = TableExtractor(INPUT_PATH, OUTPUT_JSON, OUTPUT_CSV).run()
    
    # Save the cleaned text (without table) to a temporary file
    cleaned_path = "../../data/cleaned/contract_without_table.txt"
    Path(cleaned_path).parent.mkdir(parents=True, exist_ok=True)
    Path(cleaned_path).write_text(text_without_table, encoding="utf-8")
    
    # Step 2: Split contract into sections
    splitter = SplitSections(cleaned_path, OUTPUT_DIR)
    splitter.run()
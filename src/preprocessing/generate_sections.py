from constants import INPUT_PATH, OUTPUT_JSON, OUTPUT_CSV
from table_extraction import TableExtractor
from split_sections import SplitSections



if __name__ == "__main__":
    # Step 1: Extract payment table
    text_without_table = TableExtractor(INPUT_PATH, OUTPUT_JSON, OUTPUT_CSV).run()
    
    # Step 2: Split contract into sections
    splitter = SplitSections(text_without_table, "data/sections/")
    splitter.run()
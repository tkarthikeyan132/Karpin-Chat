import pdfplumber
import pandas as pd

def pdf_to_dataframe(pdf_path):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        # Iterate over all the pages
        all_tables = []
        for page_number, page in enumerate(pdf.pages):
            print(page_number)
            # Extract table data from the page
            tables = page.extract_tables()
            
            # If tables are found, process them
            if tables:
                for table in tables:
                    # Convert table to DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    print(f"Table found on page {page_number + 1}")
                    all_tables.append(df)

        # Concatenate all DataFrames into a single DataFrame
        combined_df = pd.concat(all_tables, ignore_index=True)
        print(len(combined_df))
        return combined_df

# Path to the PDF file
pdf_path = 'bonds_polparties.pdf'
csv_path = 'bonds_polparties.csv'

# Convert PDF to DataFrame
df = pdf_to_dataframe(pdf_path)

df.to_csv(csv_path, index=False)

print(len(df))
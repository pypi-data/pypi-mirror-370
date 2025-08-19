import pandas as pd
from dp_ghs import chemical
from concurrent.futures import ThreadPoolExecutor

def load_and_process_data(file_path):
    # Load the data assuming it is in CSV format but with a .txt extension
    df = pd.read_csv(file_path, sep=",")  # Adjust the separator if needed
    
    # Verify that necessary columns exist
    if 'CAS' not in df.columns or 'Name' not in df.columns:
        raise ValueError("The required 'CAS' or 'Name' columns are missing from the input file.")
    
    # Function to get CID using CAS number, or fallback to Name
    def get_cid(row):
        try:
            chem = chemical(row['CAS'])
            return chem.cid
        except Exception as e:
            pass
        
        try:
            chem = chemical(row['Name'])
            return chem.cid
        except Exception as e:
            print(f"Error processing {row['Name']} (class {row['PFC Class']}): {e}")
            return None

    # Use ThreadPoolExecutor to parallelize the lookup
    with ThreadPoolExecutor(max_workers=10) as executor:
        df['CID'] = list(executor.map(get_cid, df.to_dict('records')))

    # Filter the DataFrame to include only rows where 'PFC Class' contains 'A' or 'B'
    df = df[df['PFC Class'].str.contains('A|B', na=False)]

    # Simplify the 'PFC Class' column to just 'A' or 'B'
    df['PFC Class'] = df['PFC Class'].apply(lambda x: 'A' if 'A' in x else 'B')

    # Drop all rows where the CID is None (indicating the lookup failed)
    df = df.dropna(subset=['CID'])
    df['CID'] = df['CID'].astype(int)

    
    # Save the updated DataFrame to a CSV file
    df.to_csv("UMN_peroxide_formers.csv", index=False)
    print("Data has been processed and saved to UMN_peroxide_formers.csv.")

# Replace 'UMN_peroxide_formers.txt' with the path to your actual file if different
file_path = "UMN_peroxide_formers.txt"
load_and_process_data(file_path)

import pandas as pd
from dp_ghs import chemical
from concurrent.futures import ThreadPoolExecutor

def load_and_process_data(file_path):
    df = pd.read_csv(file_path, sep=",")  # Adjust the separator if needed
    
    def get_cid(row):
        if 'CAS' in row:
            try:
                chem = chemical(row['CAS'])
                return int(chem.cid)
            except Exception as e:
                pass
        
        try:
            chem = chemical(row['name'])
            return int(chem.cid)
        except Exception as e:
            print(f"Error processing {row['name']}: {e}")
            return 0

    # Use ThreadPoolExecutor to parallelize the lookup
    with ThreadPoolExecutor(max_workers=10) as executor:
        df['cid'] = list(executor.map(get_cid, df.to_dict('records')))

    df['cid'] = df['cid'].astype(int)
    df.to_csv(file_path, index=False)
    print(f"Data has been processed and saved to {file_path}.")

# Replace 'UMN_peroxide_formers.txt' with the path to your actual file if different
file_path = "EPA_D_List.csv"
load_and_process_data(file_path)
print('--------------')

file_path = "EPA_P_List.csv"
load_and_process_data(file_path)
print('--------------')

file_path = "EPA_U_List.csv"
load_and_process_data(file_path)
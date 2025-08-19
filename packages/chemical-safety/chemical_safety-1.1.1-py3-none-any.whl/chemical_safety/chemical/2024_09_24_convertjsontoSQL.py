# in the data subfolder folder
# build cid list from json files
# instantiate a chem object with that cid
# put it in to the chemical.db

#columns need to cover all information contained in the chemical class


#date_retreived

#note: name should not be a column in the db - that's how the class gets instantiated

import os
import sqlite3
from chemical_safety import chemical  # Assuming Chemical is the class name

def insert_chemical(conn, chem):
    cursor = conn.cursor()

    # Insert chemical data into the database
    cursor.execute('''
        INSERT OR REPLACE INTO chemical (
            cid, name, IUPAC_name, SMILES, formula, LD50_oral, LD50_dermal, LC50, 
            signal_word, pictograms, hazard_statements, hazard_codes, 
            p_codes, p_statements, PHS, carcinogen, reproductive_toxin, 
            acute_toxin, GHS_info_missing, PHS_info, flash_point, 
            boiling_point, melting_point, density, flammability_class, 
            flammability_class_info, peroxide_class, peroxide_class_info, 
            hazardous_waste, hazardous_waste_info, disposal_info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        chem.cid, chem.name, chem.IUPAC_name, chem.SMILES, 
        chem.dp_molecule.formula, chem.LD50_oral, chem.LD50_dermal, chem.LC50, 
        chem.signal_word, ','.join(chem.pictograms), ','.join(chem.hazard_statements), 
        ','.join(chem.hazard_codes), ','.join(chem.p_codes), ','.join(chem.p_statements), 
        chem.WSU_particularly_hazardous, chem.WSU_carcinogen, chem.WSU_reproductive_toxin, 
        chem.WSU_highly_acute_toxin, chem.WSU_No_GHS, ','.join(f"{key}:{value}" for key, value in chem.WSU_PHC_info.items()), 
        chem.flash_point, chem.boiling_point, chem.melting_point, 
        chem.density, chem.flammability_class, chem.flammability_class_info, 
        chem.peroxide_class, chem.peroxide_class_info, 
        chem.hazardous_waste, chem.hazardous_waste_info, 
        ','.join(chem.disposal_info)
    ))

    conn.commit()

def migrate_json_to_db(data_folder):
    # Connect to the SQLite database
    conn = sqlite3.connect('data/chemical.db')

    # Iterate over all JSON files in the data folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            # Extract the cid by stripping off the .json extension and converting to an integer
            cid = int(filename[:-5])
            print(cid)

            # Instantiate the Chemical object using the cid
            c = chemical(None,cid=cid)

            insert_chemical(conn, c)

    # Close the connection after migration
    conn.close()

def create_chemical_table():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('data/chemical.db')
    cursor = conn.cursor()

    # Create the table for storing chemical data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chemical (
            cid INTEGER PRIMARY KEY NOT NULL,
            name TEXT,
            IUPAC_name TEXT,
            SMILES TEXT,
            formula TEXT,
            LD50_oral REAL,
            LD50_dermal REAL,
            LC50 REAL,
            signal_word TEXT,
            pictograms TEXT,
            hazard_statements TEXT,
            hazard_codes TEXT,
            p_codes TEXT,
            p_statements TEXT,
            PHS BOOLEAN,
            carcinogen BOOLEAN,
            reproductive_toxin BOOLEAN,
            acute_toxin BOOLEAN,
            GHS_info_missing BOOLEAN,
            PHS_info TEXT,
            flash_point REAL,
            boiling_point REAL,
            melting_point REAL,
            density REAL,
            flammability_class TEXT,
            flammability_class_info TEXT,
            peroxide_class TEXT,
            peroxide_class_info TEXT,
            hazardous_waste BOOLEAN,
            hazardous_waste_info TEXT,
            disposal_info TEXT
        )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_chemical_table()
    data_folder = 'data'  # Assuming the JSON files are in the 'data' subfolder
    migrate_json_to_db(data_folder)
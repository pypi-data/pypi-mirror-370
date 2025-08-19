import csv
import re

# Define the path to your text file
input_file_path = 'p_statements.txt'
output_file_path = 'p_statements.csv'

def parse_p_codes(file_path):
    # This will store tuples of (P-code, Description)
    p_codes = []

    with open(file_path, 'r') as file:
        for line in file:
            # Use regex to split the line at the first colon
            match = re.match(r'([^:]+): (.*)', line.strip())
            if match:
                p_code = match.group(1)
                description = match.group(2)
                p_codes.append((p_code, description))

    return p_codes

def save_to_csv(data, file_path):
    # Write data to a CSV file
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['P-Code', 'Description'])  # Write header
        writer.writerows(data)

# Main execution
if __name__ == '__main__':
    p_codes = parse_p_codes(input_file_path)
    save_to_csv(p_codes, output_file_path)
    print(f"Data has been saved to {output_file_path}")

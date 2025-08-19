import pandas as pd

from ghs_v2 import get_cid

lists = [
    'OSHA_carcinogens.csv',
    'IARC_classification.csv',
    'NTP_known_carcinogens.csv',
    'NTP_anticipated_carcinogens.csv'
]

for l in lists:
    df = pd.read_csv(l)
    df['cid'] = df['name'].apply(get_cid)
    df.to_csv(l, index=False)
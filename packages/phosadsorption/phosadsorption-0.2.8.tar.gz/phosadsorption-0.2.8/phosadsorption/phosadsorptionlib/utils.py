
import pandas as pd

def preprocess_dataframe(df):
    df.columns = df.columns.str.strip()
    rename_map = {
        'Οργανική ουσία': 'O.O.', 'Ηλεκτρική Αγωγιμότητα': 'Ec',
        'Οργανική': 'Organic matter', 'Ec': 'EC', 'Ec (dS/m)': 'EC',
    }
    required_columns = ['S', 'C', 'pH', 'EC', 'Organic matter', 'P', 'Mg', 'Mn', 'Cu']
    # Check for missing required columns
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Keep only relevant columns
    df = df[required_columns].copy()
    df['Mg'] = df['Mg'] / (12.1525 * 10)
    return df

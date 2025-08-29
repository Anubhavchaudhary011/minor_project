import pandas as pd

def load_from_csv(path: str) -> pd.DataFrame:
    """
    Load a CSV for text classification.

    Args:
        path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with at least a 'text' column.
    """
    df = pd.read_csv(path)
    
    # Check required column
    if "text" not in df.columns:
        raise ValueError("CSV must contain a 'text' column")
    
    # Fill missing text
    df["text"] = df["text"].fillna("")

    # Check for optional label column
    if "label" not in df.columns:
        print("⚠️ 'label' column not found. Assuming inference mode.")
    else:
        print(f"✅ Found label column. Number of classes: {df['label'].nunique()}")

    print(f"Loaded {len(df)} rows from {path}")
    return df

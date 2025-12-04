import pandas as pd
import numpy as np
import sys
from pathlib import Path
import argparse
import random

def add_schema_drift(df: pd.DataFrame) -> pd.DataFrame:
    """Add/remove columns to simulate schema drift."""
    df_corrupted = df.copy()
    
    # Randomly add a new column
    if random.choice([True, False]):
        df_corrupted["new_column"] = "unexpected_value"
        print("  - Added new column: new_column")
    
    # Randomly remove a column
    if random.choice([True, False]) and len(df_corrupted.columns) > 5:
        col_to_remove = random.choice(df_corrupted.columns.tolist())
        df_corrupted.drop(columns=[col_to_remove], inplace=True)
        print(f"  - Removed column: {col_to_remove}")
    
    return df_corrupted

def add_data_drift(df: pd.DataFrame) -> pd.DataFrame:
    """Corrupt data values to simulate data drift."""
    df_corrupted = df.copy()
    
    # Corrupt gender values
    if 'gender' in df_corrupted.columns:
        mask = np.random.random(len(df_corrupted)) < 0.1  # 10% corruption
        df_corrupted.loc[mask, 'gender'] = "InvalidGender"
        print(f"  - Corrupted {mask.sum()} gender values")
    
    # Corrupt tenure with out-of-range values
    if 'tenure' in df_corrupted.columns:
        mask = np.random.random(len(df_corrupted)) < 0.05  # 5% corruption
        df_corrupted.loc[mask, 'tenure'] = np.random.randint(100, 200, mask.sum())
        print(f"  - Corrupted {mask.sum()} tenure values with out-of-range data")
    
    # Add nulls to non-nullable columns
    if 'customerID' in df_corrupted.columns:
        mask = np.random.random(len(df_corrupted)) < 0.02  # 2% nulls
        df_corrupted.loc[mask, 'customerID'] = np.nan
        print(f"  - Added {mask.sum()} nulls to customerID")
    
    # Corrupt numeric ranges
    if 'MonthlyCharges' in df_corrupted.columns:
        mask = np.random.random(len(df_corrupted)) < 0.03  # 3% corruption
        df_corrupted.loc[mask, 'MonthlyCharges'] = np.random.uniform(300, 500, mask.sum())
        print(f"  - Corrupted {mask.sum()} MonthlyCharges values")
    
    return df_corrupted

def add_business_rule_violations(df: pd.DataFrame) -> pd.DataFrame:
    """Violate custom business rules."""
    df_corrupted = df.copy()
    
    # Violate: TotalCharges should be > MonthlyCharges
    if 'TotalCharges' in df_corrupted.columns and 'MonthlyCharges' in df_corrupted.columns:
        mask = np.random.random(len(df_corrupted)) < 0.04  # 4% violation
        # Make TotalCharges less than MonthlyCharges
        df_corrupted.loc[mask, 'TotalCharges'] = df_corrupted.loc[mask, 'MonthlyCharges'] * 0.5
        print(f"  - Violated TotalCharges > MonthlyCharges rule for {mask.sum()} rows")
    
    return df_corrupted

def main():
    parser = argparse.ArgumentParser(description="Generate corrupted datasets for testing")
    parser.add_argument("input_path", help="Path to clean dataset")
    parser.add_argument("output_path", help="Path to save corrupted dataset")
    parser.add_argument("--corruption-type", choices=['schema', 'data', 'rules', 'all'], 
                       default='all', help="Type of corruption to apply")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return False
    
    print(f"Loading clean dataset: {input_path}")
    df = pd.read_csv(input_path)
    
    # Clean TotalCharges first
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    
    print(f"Original dataset: {len(df)} rows, {len(df.columns)} columns")
    print(f"Applying corruption type: {args.corruption_type}")
    
    # Apply corruptions
    df_corrupted = df.copy()
    
    if args.corruption_type in ['schema', 'all']:
        df_corrupted = add_schema_drift(df_corrupted)
    
    if args.corruption_type in ['data', 'all']:
        df_corrupted = add_data_drift(df_corrupted)
    
    if args.corruption_type in ['rules', 'all']:
        df_corrupted = add_business_rule_violations(df_corrupted)
    
    # Save corrupted dataset
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_corrupted.to_csv(output_path, index=False)
    
    print(f"✅ Corrupted dataset saved: {output_path}")
    print(f"Final shape: {df_corrupted.shape}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
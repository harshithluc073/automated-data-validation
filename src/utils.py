import yaml
import pandas as pd
from pathlib import Path

def load_data_contract(contract_path: str = "config/data_contract.yaml") -> dict:
    """Load and parse data contract configuration."""
    with open(contract_path, "r") as f:
        return yaml.safe_load(f)

def validate_schema(df: pd.DataFrame, contract: dict) -> tuple[bool, list]:
    """Validate DataFrame against schema contract."""
    errors = []
    schema = contract.get("schema", {})
    
    for column, rules in schema.items():
        if column not in df.columns:
            errors.append(f"Missing required column: {column}")
            continue
            
        # Check nullability
        if not rules.get("nullable", True) and df[column].isnull().any():
            errors.append(f"Column {column} has null values but nullable=false")
    
    return len(errors) == 0, errors

def get_baseline_path() -> Path:
    """Return path to baseline dataset."""
    return Path("data/baseline/churn_clean.csv")
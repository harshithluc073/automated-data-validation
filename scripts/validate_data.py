import argparse
import sys
import pandas as pd
import great_expectations as gx
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Validate dataset against churn_suite")
    parser.add_argument("dataset_path", help="Path to CSV dataset to validate")
    args = parser.parse_args()

    dataset_path = Path(args.dataset_path)
    
    if not dataset_path.exists():
        print(f"❌ Error: Dataset not found at {dataset_path}")
        sys.exit(1)

    print(f"🔍 Validating dataset: {dataset_path.name}")

    # Initialize GE context
    context = gx.get_context()
    
    # Load and clean data
    try:
        df = pd.read_csv(dataset_path)
        # Fix TotalCharges data type issue
        if 'TotalCharges' in df.columns:
            df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)

    # Load expectation suite directly from JSON file
    try:
        suite_path = Path("great_expectations/expectations/churn_suite.json")
        if not suite_path.exists():
            print(f"❌ Suite file not found at: {suite_path}")
            sys.exit(1)
            
        with open(suite_path, "r") as f:
            suite_dict = json.load(f)
        
        # Create validator
        validator = context.sources.pandas_default.read_dataframe(df)
        
        # Apply each expectation from the suite
        expectation_count = 0
        for exp_config in suite_dict["expectations"]:
            expectation_type = exp_config["expectation_type"]
            kwargs = exp_config["kwargs"]
            
            # Get the expectation method from validator and apply it
            if hasattr(validator, expectation_type):
                expectation_method = getattr(validator, expectation_type)
                expectation_method(**kwargs)
                expectation_count += 1
        
        print(f"✅ Loaded {expectation_count} expectations from churn_suite")
    except Exception as e:
        print(f"❌ Error loading suite: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Run validation
    print("⏳ Running expectations...")
    try:
        result = validator.validate()
    except Exception as e:
        print(f"❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Print results
    success = result["success"]
    stats = result["statistics"]
    
    print(f"\n{'='*50}")
    print(f"VALIDATION RESULT: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"{'='*50}")
    print(f"Total checks: {stats['evaluated_expectations']}")
    print(f"Passed: {stats['successful_expectations']}")
    print(f"Failed: {stats['unsuccessful_expectations']}")
    print(f"Success rate: {stats['success_percent']:.1f}%")

    # Generate Data Docs (ALWAYS attempt this)
    print(f"\n📊 Generating HTML report...")
    try:
        context.build_data_docs()
        docs_path = Path("great_expectations/uncommitted/data_docs/local_site/index.html")
        if docs_path.exists():
            print(f"✅ Report available at: {docs_path}")
        else:
            print("⚠️ Data Docs file was not created")
    except Exception as e:
        print(f"⚠️ Warning: Could not generate docs: {e}")

    # Exit with proper code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
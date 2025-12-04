import argparse
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

def generate_profiling_report(dataset_path: str, output_dir: str = "reports/profiling"):
    """
    Generate a comprehensive HTML profiling report for a dataset.
    """
    path = Path(dataset_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📊 Profiling dataset: {path.name}")
    
    # Load data
    try:
        df = pd.read_csv(path)
        # Clean TotalCharges column
        if 'TotalCharges' in df.columns:
            df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Generate report filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_path / f"profile_{path.stem}_{timestamp}.html"
    
    # Create HTML report content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Profiling Report - {path.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .stat {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .stat-label {{ font-weight: bold; color: #7f8c8d; }}
            .stat-value {{ font-size: 1.2em; color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #3498db; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Data Profiling Report</h1>
            <p><strong>Dataset:</strong> {path.name}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Rows:</strong> {len(df):,}</p>
            <p><strong>Columns:</strong> {len(df.columns)}</p>
            
            <h2>📈 Dataset Shape</h2>
            <div class="stat">
                <span class="stat-label">Total Rows:</span> <span class="stat-value">{len(df):,}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Total Columns:</span> <span class="stat-value">{len(df.columns)}</span>
            </div>
            
            <h2>🗂️ Column Summary</h2>
            <table>
                <tr>
                    <th>Column</th>
                    <th>Data Type</th>
                    <th>Non-Null Count</th>
                    <th>Null Count</th>
                    <th>Unique Values</th>
                </tr>
    """
    
    # Add column details
    for col in df.columns:
        non_null = df[col].count()
        null_count = df[col].isnull().sum()
        unique_vals = df[col].nunique()
        dtype = str(df[col].dtype)
        
        html_content += f"""
                <tr>
                    <td><strong>{col}</strong></td>
                    <td>{dtype}</td>
                    <td>{non_null:,}</td>
                    <td>{null_count:,}</td>
                    <td>{unique_vals:,}</td>
                </tr>
        """
    
    html_content += """
            </table>
            
            <h2>⚠️ Data Quality Alerts</h2>
    """
    
    # Add alerts for potential issues
    alerts = []
    for col in df.columns:
        null_pct = (df[col].isnull().sum() / len(df)) * 100
        if null_pct > 10:
            alerts.append(f"Column '{col}' has {null_pct:.1f}% null values")
        if df[col].dtype == 'object':
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.9:
                alerts.append(f"Column '{col}' might be an ID field ({unique_ratio:.1%} unique)")
    
    if alerts:
        for alert in alerts:
            html_content += f'<div class="alert">⚠️ {alert}</div>'
    else:
        html_content += '<div class="alert">✅ No major quality issues detected</div>'
    
    # Add distribution summary for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        html_content += """
            <h2>📊 Numeric Column Statistics</h2>
            <table>
                <tr>
                    <th>Column</th>
                    <th>Mean</th>
                    <th>Std Dev</th>
                    <th>Min</th>
                    <th>25%</th>
                    <th>50%</th>
                    <th>75%</th>
                    <th>Max</th>
                </tr>
        """
        
        stats = df[numeric_cols].describe()
        for col in numeric_cols:
            html_content += f"""
                <tr>
                    <td><strong>{col}</strong></td>
                    <td>{stats[col]['mean']:.2f}</td>
                    <td>{stats[col]['std']:.2f}</td>
                    <td>{stats[col]['min']:.2f}</td>
                    <td>{stats[col]['25%']:.2f}</td>
                    <td>{stats[col]['50%']:.2f}</td>
                    <td>{stats[col]['75%']:.2f}</td>
                    <td>{stats[col]['max']:.2f}</td>
                </tr>
            """
        
        html_content += "</table>"
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Profiling report generated: {report_file}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HTML profiling report for dataset")
    parser.add_argument("dataset_path", help="Path to CSV dataset to profile")
    parser.add_argument("--output", "-o", default="reports/profiling", help="Output directory")
    
    args = parser.parse_args()
    
    success = generate_profiling_report(args.dataset_path, args.output)
    sys.exit(0 if success else 1)
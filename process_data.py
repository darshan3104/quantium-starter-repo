import os
import glob
import pandas as pd
import sys

def main():
    data_dir = "data"
    output_file = "output.csv"
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found.")
        sys.exit(1)
        
    # Get all CSV files
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not csv_files:
        print(f"Error: No CSV files found in '{data_dir}'.")
        sys.exit(1)
        
    print(f"Found {len(csv_files)} files to process.")
    
    # Load and combine all CSV files
    dataframes = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dataframes.append(df)
        except Exception as e:
            print(f"Warning: Failed to read {file}. Error: {e}")
    
    if not dataframes:
        print("Error: No valid data loaded.")
        sys.exit(1)
        
    combined_data = pd.concat(dataframes, ignore_index=True)
    
    # Normalize column names
    combined_data.columns = [str(col).lower() for col in combined_data.columns]
    
    # Validate required columns
    required_columns = ['product', 'quantity', 'price', 'date', 'region']
    missing = [col for col in required_columns if col not in combined_data.columns]
    
    if missing:
        print(f"Error: Missing columns {missing}")
        sys.exit(1)
    
    # Normalize product column
    combined_data['product'] = combined_data['product'].astype(str).str.lower()
    
    # Filter for pink morsel
    df = combined_data[combined_data['product'] == 'pink morsel'].copy()
    
    if df.empty:
        print("Warning: No pink morsel data found.")
    
    # Clean price column
    df['price'] = (
        df['price']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.strip()
    )
    
    # Convert to numeric safely
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    
    # Drop invalid rows
    df = df.dropna(subset=['price', 'quantity'])
    
    # Create sales column
    df['sales'] = df['price'] * df['quantity']
    
    # Convert date column
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Drop invalid dates
    df = df.dropna(subset=['date'])
    
    # Final output
    final_output = df[['sales', 'date', 'region']]
    
    # Save CSV
    try:
        final_output.to_csv(output_file, index=False)
        print(f"Output saved to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)
    
    # Business analysis
    before = final_output[final_output["date"] < "2021-01-15"]["sales"].sum()
    after = final_output[final_output["date"] >= "2021-01-15"]["sales"].sum()
    
    print("\n Sales Analysis:")
    print("Before Jan 15, 2021:", before)
    print("After Jan 15, 2021:", after)


if __name__ == "__main__":
    main()
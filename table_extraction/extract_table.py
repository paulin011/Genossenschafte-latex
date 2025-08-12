#!/usr/bin/env python3
"""
Script to extract table from PDF using camelot with lattice mode
"""

import camelot
import pandas as pd
import sys
import os

def extract_table_with_manual_columns(pdf_path, columns=None, output_path=None):
    """
    Extract table with manually specified column positions
    
    Args:
        pdf_path (str): Path to the PDF file
        columns (list): List of x-coordinates for column separators
        output_path (str): Optional path to save the extracted table as CSV
    
    Returns:
        pandas.DataFrame: Extracted table data
    """
    
    try:
        print(f"Extracting tables with manual column positions: {columns}")
        
        tables = camelot.read_pdf(
            pdf_path,
            flavor='stream',
            pages='all',
            columns=columns,      # Manual column positions
            split_text=True,
            strip_text='\n',
            row_tol=2
        )
        
        print(f"Found {len(tables)} table(s) with manual columns")
        
        if len(tables) > 0:
            table = tables[0]
            print(f"Shape: {table.df.shape}")
            print(f"Accuracy: {table.accuracy:.2f}")
            
            if output_path:
                table.df.to_csv(output_path, index=False, encoding='utf-8')
                print(f"Table saved to: {output_path}")
            
            return table.df
        
        return None
        
    except Exception as e:
        print(f"Error with manual columns: {str(e)}")
        return None

def extract_table_from_pdf(pdf_path, output_path=None):
    """
    Extract table from PDF using camelot lattice mode
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str): Optional path to save the extracted table as CSV
    
    Returns:
        pandas.DataFrame: Extracted table data
    """
    
    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        return None
    
    try:
        # Extract tables using lattice mode (better for tables with lines/borders)
        print(f"Extracting tables from: {pdf_path}")
        print("Using lattice mode with improved column detection...")
        
        tables = camelot.read_pdf(
            pdf_path, 
            flavor='lattice',  # Use lattice mode for tables with clear borders
            pages='all',       # Extract from all pages
            strip_text='\n',   # Strip newlines from text
            line_scale=40,     # Sensitivity to lines (higher = more sensitive)
            copy_text=['v'],   # Copy text along vertical lines
            shift_text=['l', 'r'],  # Allow text shifting left/right
            split_text=True,   # Split text that spans multiple cells
            flag_size=True     # Flag text size inconsistencies
        )
        
        print(f"Found {len(tables)} table(s)")
        
        if len(tables) == 0 or (len(tables) > 0 and tables[0].accuracy < 85):
            print("No tables found or low accuracy. Trying stream mode with column detection...")
            # Fallback to stream mode with better column detection
            tables = camelot.read_pdf(
                pdf_path,
                flavor='stream',
                pages='all',
                table_areas=None,     # Auto-detect table areas
                columns=None,         # Auto-detect columns
                split_text=True,      # Split text spanning multiple cells
                strip_text='\n',      # Strip newlines
                row_tol=2,           # Row tolerance (merge rows closer than this)
                column_tol=0         # Column tolerance (0 = strict column detection)
            )
            print(f"Found {len(tables)} table(s) with stream mode")
            
            # If still no luck, try with manual column detection
            if len(tables) == 0:
                print("Trying stream mode with relaxed column detection...")
                tables = camelot.read_pdf(
                    pdf_path,
                    flavor='stream',
                    pages='all',
                    edge_tol=50,         # Edge tolerance
                    row_tol=10,          # Relaxed row tolerance
                    column_tol=5         # Relaxed column tolerance
                )
                print(f"Found {len(tables)} table(s) with relaxed detection")
        
        if len(tables) == 0:
            print("No tables found in the PDF.")
            return None
        
        # Process each table
        for i, table in enumerate(tables):
            print(f"\n--- Table {i+1} ---")
            print(f"Shape: {table.df.shape}")
            print(f"Accuracy: {table.accuracy:.2f}")
            print(f"Whitespace: {table.whitespace:.2f}")
            
            # Display first few rows
            print("\nFirst few rows:")
            print(table.df.head())
            
            # Save table if output path is provided
            if output_path:
                if len(tables) > 1:
                    # Multiple tables: add index to filename
                    base, ext = os.path.splitext(output_path)
                    save_path = f"{base}_table_{i+1}{ext}"
                else:
                    save_path = output_path
                
                table.df.to_csv(save_path, index=False, encoding='utf-8')
                print(f"Table saved to: {save_path}")
        
        # Return the first (or only) table
        return tables[0].df if tables else None
        
    except Exception as e:
        print(f"Error extracting table: {str(e)}")
        return None

def main():
    """Main function to run the script"""
    
    # Default PDF path
    pdf_path = "Tabelle Morphologie Typologie.pdf"
    
    # Check if custom PDF path is provided as command line argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    # Output CSV path
    output_path = "extracted_table.csv"
    
    print("=== PDF Table Extraction using Camelot ===")
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_path}")
    print("-" * 50)
    
    # Try automatic extraction first
    df = extract_table_from_pdf(pdf_path, output_path)
    
    # If automatic extraction didn't work well, try manual column detection
    if df is None or df.shape[1] < 5:  # Expected at least 5 columns
        print("\n=== Trying manual column detection ===")
        
        # These are approximate column positions - you may need to adjust
        # Based on the PDF layout, estimate x-coordinates of column separators
        manual_columns = [120, 250, 380, 500, 580]  # Adjust these values
        
        df_manual = extract_table_with_manual_columns(
            pdf_path, 
            columns=manual_columns, 
            output_path="extracted_table_manual.csv"
        )
        
        if df_manual is not None and df_manual.shape[1] >= df.shape[1]:
            df = df_manual
            output_path = "extracted_table_manual.csv"
            print("Manual column detection provided better results")
    
    if df is not None:
        print(f"\n=== Extraction completed successfully ===")
        print(f"Table shape: {df.shape}")
        print(f"Saved to: {output_path}")
        
        # Show preview of the table structure
        print("\n=== Table Preview ===")
        print("Column count per row:")
        for i, row in df.iterrows():
            non_empty = sum(1 for cell in row if pd.notna(cell) and str(cell).strip())
            print(f"Row {i}: {non_empty} non-empty cells")
            if i >= 10:  # Show first 10 rows only
                print("...")
                break
                
    else:
        print("\n=== Extraction failed ===")
        print("Try adjusting the manual_columns values in the script")
        sys.exit(1)

if __name__ == "__main__":
    main()

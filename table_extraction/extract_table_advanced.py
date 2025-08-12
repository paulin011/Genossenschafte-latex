#!/usr/bin/env python3
"""
Advanced script to extract table from PDF with superior column detection
"""

import camelot
import pandas as pd
import sys
import os

def extract_table_advanced(pdf_path, output_path=None):
    """
    Extract table using multiple methods and choose the best result
    """
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        return None
    
    methods = []
    
    try:
        # Method 1: Lattice with fine-tuned parameters
        print("Method 1: Fine-tuned lattice mode...")
        tables1 = camelot.read_pdf(
            pdf_path,
            flavor='lattice',
            pages='all',
            line_scale=60,        # Higher sensitivity to lines
            copy_text=['v'],      # Copy text along vertical lines
            shift_text=['l', 'r'], # Allow text shifting
            split_text=True,      # Split text spanning cells
            flag_size=True,       # Flag size inconsistencies
            strip_text='\n'
        )
        if tables1:
            methods.append(('lattice_fine', tables1[0]))
            print(f"  Shape: {tables1[0].df.shape}, Accuracy: {tables1[0].accuracy:.2f}")
    
    except Exception as e:
        print(f"  Method 1 failed: {e}")
    
    try:
        # Method 2: Stream with strict column detection
        print("Method 2: Stream with strict columns...")
        tables2 = camelot.read_pdf(
            pdf_path,
            flavor='stream',
            pages='all',
            edge_tol=200,         # Edge tolerance
            row_tol=3,           # Strict row tolerance
            column_tol=0,        # Strict column tolerance
            split_text=True,
            strip_text='\n'
        )
        if tables2:
            methods.append(('stream_strict', tables2[0]))
            print(f"  Shape: {tables2[0].df.shape}, Accuracy: {tables2[0].accuracy:.2f}")
    
    except Exception as e:
        print(f"  Method 2 failed: {e}")
    
    try:
        # Method 3: Stream with moderate tolerance
        print("Method 3: Stream with moderate tolerance...")
        tables3 = camelot.read_pdf(
            pdf_path,
            flavor='stream',
            pages='all',
            edge_tol=100,
            row_tol=5,
            column_tol=3,
            split_text=True,
            strip_text='\n'
        )
        if tables3:
            methods.append(('stream_moderate', tables3[0]))
            print(f"  Shape: {tables3[0].df.shape}, Accuracy: {tables3[0].accuracy:.2f}")
    
    except Exception as e:
        print(f"  Method 3 failed: {e}")
    
    try:
        # Method 4: Stream with manual column positions (estimated for this PDF)
        print("Method 4: Stream with estimated column positions...")
        tables4 = camelot.read_pdf(
            pdf_path,
            flavor='stream',
            pages='all',
            columns=[140, 280, 400, 460, 520, 580],  # Estimated column separators
            split_text=True,
            strip_text='\n',
            row_tol=3
        )
        if tables4:
            methods.append(('stream_manual', tables4[0]))
            print(f"  Shape: {tables4[0].df.shape}, Accuracy: {tables4[0].accuracy:.2f}")
    
    except Exception as e:
        print(f"  Method 4 failed: {e}")
    
    if not methods:
        print("All methods failed!")
        return None
    
    # Choose the best method based on:
    # 1. Number of columns (more is usually better)
    # 2. Accuracy score
    # 3. Number of rows
    
    best_method = None
    best_score = 0
    
    for method_name, table in methods:
        # Calculate a composite score
        cols = table.df.shape[1]
        rows = table.df.shape[0]
        accuracy = table.accuracy
        
        # Weighted score: columns are most important, then accuracy, then rows
        score = (cols * 3) + (accuracy / 100 * 2) + (rows * 0.1)
        
        print(f"\n{method_name}: Score = {score:.2f} (cols={cols}, acc={accuracy:.1f}, rows={rows})")
        
        if score > best_score:
            best_score = score
            best_method = (method_name, table)
    
    if best_method:
        method_name, best_table = best_method
        print(f"\nBest method: {method_name}")
        print(f"Final shape: {best_table.df.shape}")
        print(f"Final accuracy: {best_table.accuracy:.2f}")
        
        # Show column analysis
        print("\nColumn analysis:")
        df = best_table.df
        for col_idx in range(df.shape[1]):
            non_empty = df.iloc[:, col_idx].notna().sum()
            print(f"  Column {col_idx}: {non_empty} non-empty cells")
        
        if output_path:
            best_table.df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"\nTable saved to: {output_path}")
        
        return best_table.df
    
    return None

def main():
    """Main function"""
    
    pdf_path = "Tabelle Morphologie Typologie.pdf"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    output_path = "extracted_table_advanced.csv"
    
    print("=== Advanced PDF Table Extraction ===")
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_path}")
    print("-" * 50)
    
    df = extract_table_advanced(pdf_path, output_path)
    
    if df is not None:
        print(f"\n=== SUCCESS ===")
        print(f"Final table shape: {df.shape}")
        
        # Show first few rows for verification
        print("\nFirst 5 rows:")
        print(df.head().to_string())
        
    else:
        print("\n=== FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()

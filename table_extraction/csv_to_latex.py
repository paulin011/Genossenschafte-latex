#!/usr/bin/env python3
"""
Script to convert extracted CSV table to LaTeX format
"""

import pandas as pd
import sys
import os

def clean_text_for_latex(text):
    """
    Clean and escape text for LaTeX
    """
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text).strip()
    
    # Replace special characters for LaTeX
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '^': r'\textasciicircum{}',
        '~': r'\textasciitilde{}',
        '\\': r'\textbackslash{}',
        'ä': r'\"a',
        'ö': r'\"o',
        'ü': r'\"u',
        'Ä': r'\"A',
        'Ö': r'\"O',
        'Ü': r'\"U',
        'ß': r'\ss{}',
        '„': r'\enquote{',
        '"': r'}',
        '"': r'\enquote{',
        '"': r'}',
        '–': r'--',
        '—': r'---'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def merge_columns_intelligently(df):
    """
    Merge columns intelligently to reconstruct the original table structure
    """
    result_rows = []
    
    for idx, row in df.iterrows():
        if idx == 0:  # Header row
            result_rows.append([
                'Merkmalsgruppe',
                'Ordnungsmerkmal', 
                'Einzelmerkmal',
                'Ausprägungen',
                'Mischformen'
            ])
            continue
        
        # Clean all cells
        cells = [clean_text_for_latex(cell) for cell in row]
        
        # Determine the structure based on content
        merkmalsgruppe = cells[0] if cells[0] else ''
        ordnungsmerkmal = cells[1] if cells[1] else ''
        einzelmerkmal = cells[2] if cells[2] else ''
        
        # Merge ausprägungen from multiple columns (3-6)
        auspragungen_parts = []
        for i in range(3, min(len(cells)-1, 7)):  # Exclude last column (Mischformen)
            if cells[i] and cells[i].strip():
                auspragungen_parts.append(cells[i])
        
        auspragungen = '; '.join(auspragungen_parts) if auspragungen_parts else ''
        
        # Last column is Mischformen
        mischformen = cells[-1] if len(cells) > 0 and cells[-1] else ''
        
        result_rows.append([merkmalsgruppe, ordnungsmerkmal, einzelmerkmal, auspragungen, mischformen])
    
    return result_rows

def group_rows_by_structure(rows):
    """
    Group rows to create proper multirow structure
    """
    grouped = []
    current_gruppe = None
    current_ordnung = None
    gruppe_rows = []
    ordnung_rows = []
    
    for row in rows[1:]:  # Skip header
        merkmalsgruppe, ordnungsmerkmal, einzelmerkmal, auspragungen, mischformen = row
        
        # New Merkmalsgruppe
        if merkmalsgruppe and merkmalsgruppe != current_gruppe:
            # Finalize previous group
            if current_gruppe:
                if ordnung_rows:
                    gruppe_rows.append((current_ordnung, ordnung_rows))
                grouped.append((current_gruppe, gruppe_rows))
            
            # Start new group
            current_gruppe = merkmalsgruppe
            current_ordnung = ordnungsmerkmal
            gruppe_rows = []
            ordnung_rows = []
        
        # New Ordnungsmerkmal within same group
        elif ordnungsmerkmal and ordnungsmerkmal != current_ordnung:
            # Finalize previous ordnung
            if ordnung_rows:
                gruppe_rows.append((current_ordnung, ordnung_rows))
            
            # Start new ordnung
            current_ordnung = ordnungsmerkmal
            ordnung_rows = []
        
        # Add current row to ordnung_rows
        ordnung_rows.append((einzelmerkmal, auspragungen, mischformen))
    
    # Finalize last group
    if current_gruppe:
        if ordnung_rows:
            gruppe_rows.append((current_ordnung, ordnung_rows))
        grouped.append((current_gruppe, gruppe_rows))
    
    return grouped

def generate_latex_table(grouped_data):
    """
    Generate LaTeX table code
    """
    latex_lines = []
    
    # Table header
    latex_lines.extend([
        r'\begin{sidewaystable}[htbp]',
        r'\centering',
        r'\small',
        r'\setlength{\tabcolsep}{4pt}',
        r'\renewcommand{\arraystretch}{1.3}',
        r'\caption{Morphologischer Kasten genossenschaftlicher Geschäftsmodelle. Eigene Darstellung.}',
        r'\label{tab:morphologischer_kasten}',
        r'\begin{tabularx}{\textwidth}{|p{0.18\textwidth}|p{0.20\textwidth}|p{0.20\textwidth}|X|p{0.08\textwidth}|}',
        r'\hline',
        r'\textbf{Merkmalsgruppe} & \textbf{Ordnungsmerkmal} & \textbf{Einzelmerkmal} & \textbf{Ausprägungen} & \textbf{Mischformen} \\',
        r'\hline'
    ])
    
    # Process grouped data
    for gruppe_idx, (gruppe_name, gruppe_data) in enumerate(grouped_data):
        # Calculate total rows for this group
        total_rows = sum(len(ordnung_rows) for _, ordnung_rows in gruppe_data)
        
        first_gruppe_row = True
        
        for ordnung_idx, (ordnung_name, ordnung_rows) in enumerate(gruppe_data):
            ordnung_row_count = len(ordnung_rows)
            
            first_ordnung_row = True
            
            for row_idx, (einzelmerkmal, auspragungen, mischformen) in enumerate(ordnung_rows):
                
                # Start the row
                row_parts = []
                
                # Merkmalsgruppe (only on first row of group)
                if first_gruppe_row and first_ordnung_row and row_idx == 0:
                    row_parts.append(f'\\multirow{{{total_rows}}}{{*}}{{{gruppe_name}}}')
                else:
                    row_parts.append('')
                
                # Ordnungsmerkmal (only on first row of ordnung)
                if first_ordnung_row and row_idx == 0:
                    if ordnung_name.startswith('('):
                        # Handle parentheses properly
                        ordnung_clean = ordnung_name.replace('(', '(\\enquote{').replace(')', '})')
                    else:
                        ordnung_clean = ordnung_name
                    row_parts.append(f'\\multirow{{{ordnung_row_count}}}{{*}}{{{ordnung_clean}}}')
                else:
                    row_parts.append('')
                
                # Einzelmerkmal
                row_parts.append(einzelmerkmal)
                
                # Handle multi-line ausprägungen
                if ';' in auspragungen and len(auspragungen) > 60:
                    # Split long ausprägungen into multiple lines
                    parts = [part.strip() for part in auspragungen.split(';')]
                    auspragungen_formatted = parts[0]
                    for part in parts[1:]:
                        auspragungen_formatted += f'\\\\[-2pt]\n &  &  & {part}'
                    row_parts.append(auspragungen_formatted)
                else:
                    row_parts.append(auspragungen)
                
                # Mischformen
                row_parts.append(mischformen)
                
                # Join the row
                latex_lines.append(' & '.join(row_parts) + ' \\\\')
                
                # Add clines as needed
                if not (first_ordnung_row and row_idx == 0):
                    latex_lines.append('\\cline{3-5}')
                elif ordnung_idx > 0 and first_ordnung_row and row_idx == 0:
                    latex_lines.append('\\cline{2-5}')
                
                first_ordnung_row = False
            
            first_gruppe_row = False
        
        # Add horizontal line after each group
        latex_lines.append('\\hline')
    
    # Table footer
    latex_lines.extend([
        r'\end{tabularx}',
        r'\end{sidewaystable}'
    ])
    
    return '\n'.join(latex_lines)

def csv_to_latex(csv_path, output_path=None):
    """
    Convert CSV to LaTeX table
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found.")
        return None
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"Read CSV with shape: {df.shape}")
    
    # Process the data
    processed_rows = merge_columns_intelligently(df)
    grouped_data = group_rows_by_structure(processed_rows)
    
    print(f"Processed into {len(grouped_data)} main groups")
    
    # Generate LaTeX
    latex_code = generate_latex_table(grouped_data)
    
    # Save to file
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        print(f"LaTeX table saved to: {output_path}")
    
    return latex_code

def main():
    """Main function"""
    
    csv_path = "extracted_table_advanced.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    output_path = "converted_table.tex"
    
    print("=== CSV to LaTeX Table Converter ===")
    print(f"Input CSV: {csv_path}")
    print(f"Output LaTeX: {output_path}")
    print("-" * 50)
    
    latex_code = csv_to_latex(csv_path, output_path)
    
    if latex_code:
        print(f"\n=== SUCCESS ===")
        print("LaTeX table generated successfully!")
        print("\nFirst few lines of the generated LaTeX:")
        print('\n'.join(latex_code.split('\n')[:15]))
        print("...")
    else:
        print("\n=== FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()

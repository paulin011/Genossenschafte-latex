#!/usr/bin/env python3
"""
Simple and robust CSV to LaTeX table converter
"""

import pandas as pd
import sys
import os

def clean_latex_text(text):
    """Clean text for LaTeX with proper German character handling"""
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text).strip()
    
    # Handle German characters properly
    text = text.replace('ä', r'\"a')
    text = text.replace('ö', r'\"o') 
    text = text.replace('ü', r'\"u')
    text = text.replace('Ä', r'\"A')
    text = text.replace('Ö', r'\"O')
    text = text.replace('Ü', r'\"U')
    text = text.replace('ß', r'\ss{}')
    
    # Handle quotes
    text = text.replace('„', r'\enquote{')
    text = text.replace('"', r'}')
    text = text.replace('"', r'\enquote{')
    text = text.replace('"', r'}')
    
    # Handle ampersand
    text = text.replace('&', r' \& ')
    
    # Clean up parentheses content
    if '(„' in text:
        text = text.replace('(„', r'(\enquote{')
        text = text.replace('?")', r'?})')
    
    return text

def convert_csv_to_latex_simple(csv_path, output_path):
    """Convert CSV to LaTeX using the original table structure as template"""
    
    # Read the advanced CSV
    df = pd.read_csv(csv_path)
    print(f"Reading CSV with {df.shape[0]} rows and {df.shape[1]} columns")
    
    # Start with the proven table structure
    latex_code = r'''\begin{sidewaystable}[htbp]
\centering
\small
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.3}
\caption{Morphologischer Kasten genossenschaftlicher Geschäftsmodelle. Eigene Darstellung.}
\label{tab:morphologischer_kasten}
\begin{tabularx}{\textwidth}{|p{0.18\textwidth}|p{0.20\textwidth}|p{0.20\textwidth}|X|p{0.08\textwidth}|}
\hline
\textbf{Merkmalsgruppe} & \textbf{Ordnungsmerkmal} & \textbf{Einzelmerkmal} & \textbf{Ausprägungen} & \textbf{Mischformen} \\
\hline
\multirow{14}{*}{Sinnbezogene Merkmale} & \multirow{8}{*}{Mitglieder/Nutzer (\enquote{Wer?})} & Leistungsadressaten & Mitglieder; Dritte; Gesellschaft & Ja \\
\cline{3-5}
 &  & Identit\"atsprinzip & Ja; Nein\\[-2pt]
 &  &  & Eigent\"umer \& Nutzer; Eigent\"umer \& Besch\"aftigte\\[-2pt]
 &  &  & F\"ordergenossenschaft; Produktivgenossenschaft & Nein \\
\cline{3-5}
 &  & Gesch\"aftsbeziehung & Hauptzweck; Nebenzweck\\[-2pt]
 &  &  & Mitgliedergesch\"aft; Nichtmitgliedergesch\"aft & Ja \\
\cline{3-5}
 &  & Tr\"agerschaft & Privat; Staatlich & Ja \\
\cline{3-5}
 &  & Betriebsformen & Haushalte; Unternehmen &  \\
\cline{2-5}
 & \multirow{6}{*}{Nutzenversprechen (\enquote{Was?})} & R\"aumliche Verankerung & Lokal; Regional; \"Uberregional; National; International & Ja \\
\cline{3-5}
 &  & Leistungsarten & Wirtschaftlich; Sozial\\[-2pt]
 &  &  & G\"uter; Dienstleistungen\\[-2pt]
 &  &  & Produktion; Bezug; Absatz & Ja \\
\cline{3-5}
 &  & Schl\"usselaktivit\"aten & \"Okonomisierung; Vertretung; Koordinierung & Ja \\
\cline{3-5}
 &  & Funktions\"ubernahme & Eine Funktion; Mehrere Funktionen & Ja \\
\hline
\multirow{10}{*}{Strukturbezogene Merkmale} & \multirow{6}{*}{Wertsch\"opfungsarchitektur (\enquote{Wie?})} & Kooperationspartner & Verbundinterne Kooperationspartner; Verbundexterne Kooperationspartner\\[-2pt]
 &  &  & Finanzielle Beteiligung; Nicht-finanzielle Beteiligung & Ja \\
\cline{3-5}
 &  & Vertriebskan\"ale & Eigene Vertriebskan\"ale; Fremde Vertriebskan\"ale\\[-2pt]
 &  &  & Analog; Digital\\[-2pt]
 &  &  & Einkanalstrategie; Multikanalstrategie; Omnikanalstrategie\\[-2pt]
 &  &  & Filialen; Vertriebsabteilungen; Online-Shop; Plattformen & Ja \\
\cline{2-5}
 & \multirow{4}{*}{Ertragsmechanik (\enquote{Wert})} & Ressourcen & Materiell; Immateriell\\[-2pt]
 &  &  & Sachkapital; Finanzkapital; Sozialkapital; Humankapital & Ja \\
\cline{3-5}
 &  & Erl\"osmodell & Umsatzerl\"ose; Beteiligungserl\"ose; Regelm\"a\ss{}ige Beitr\"age; Subventionen & Ja \\
\cline{3-5}
 &  & Kostenmodell & Fixkosten; Variable Kosten & Ja \\
\hline
\end{tabularx}
\end{sidewaystable}'''

    # Save the LaTeX code
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_code)
    
    print(f"LaTeX table saved to: {output_path}")
    return latex_code

def convert_csv_dynamic(csv_path, output_path):
    """
    Convert CSV dynamically based on the extracted data
    """
    df = pd.read_csv(csv_path)
    
    latex_lines = [
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
    ]
    
    # Process rows, skipping header
    for idx, row in df.iterrows():
        if idx == 0:  # Skip header row
            continue
            
        # Extract and clean data
        merkmalsgruppe = clean_latex_text(row.iloc[0])
        ordnungsmerkmal = clean_latex_text(row.iloc[1]) 
        einzelmerkmal = clean_latex_text(row.iloc[2])
        
        # Combine ausprägungen from columns 3-6
        auspragungen = []
        for col_idx in range(3, min(len(row)-1, 7)):
            val = clean_latex_text(row.iloc[col_idx])
            if val:
                auspragungen.append(val)
        
        auspragungen_text = '; '.join(auspragungen)
        mischformen = clean_latex_text(row.iloc[-1])
        
        # Create table row
        if merkmalsgruppe:
            latex_lines.append(f'{merkmalsgruppe} & {ordnungsmerkmal} & {einzelmerkmal} & {auspragungen_text} & {mischformen} \\\\')
        else:
            latex_lines.append(f' &  & {einzelmerkmal} & {auspragungen_text} & {mischformen} \\\\')
    
    latex_lines.extend([
        r'\hline',
        r'\end{tabularx}',
        r'\end{sidewaystable}'
    ])
    
    latex_code = '\n'.join(latex_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_code)
    
    return latex_code

def main():
    csv_path = "extracted_table_advanced.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    print("=== CSV to LaTeX Converter ===")
    print(f"Input: {csv_path}")
    print("-" * 40)
    
    # Option 1: Use the proven manual structure
    print("Option 1: Using proven manual structure...")
    convert_csv_to_latex_simple(csv_path, "table_manual.tex")
    
    # Option 2: Dynamic conversion from CSV data
    print("\nOption 2: Dynamic conversion from CSV...")
    convert_csv_dynamic(csv_path, "table_dynamic.tex")
    
    print("\n=== Both versions created ===")
    print("table_manual.tex - Uses the proven manual structure")
    print("table_dynamic.tex - Generated from CSV data")

if __name__ == "__main__":
    main()

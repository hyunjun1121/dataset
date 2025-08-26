#!/usr/bin/env python3
"""
Excel preprocessing script for mhj_formatted.xlsx.
Extracts and parses normalized_message_string content.
"""
import pandas as pd
import json
import re
import os
from pathlib import Path


def parse_normalized_message_string(text):
    """
    Parse numbered text sections from normalized_message_string.
    
    Args:
        text (str): Raw text with numbered sections
        
    Returns:
        list: List of parsed text sections
    """
    if pd.isna(text) or not isinstance(text, str):
        return []
    
    # Split by numbered patterns (1., 2., 3., etc.)
    # Use regex to find all numbered sections
    pattern = r'(\d+\.\s*)'
    parts = re.split(pattern, text)
    
    # Filter out empty parts and number markers
    sections = []
    current_section = ""
    
    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if not part:
            i += 1
            continue
            
        # Check if it's a number marker (like "1. ")
        if re.match(r'^\d+\.\s*$', part):
            # Save previous section if exists
            if current_section.strip():
                sections.append(current_section.strip())
            # Start new section with the content after the number
            if i + 1 < len(parts):
                current_section = parts[i + 1]
                i += 2
            else:
                i += 1
        else:
            # If no number marker found, this might be the continuation or first part
            if not current_section:
                current_section = part
            else:
                current_section += " " + part
            i += 1
    
    # Don't forget the last section
    if current_section.strip():
        sections.append(current_section.strip())
    
    # If no numbered sections found, try alternative parsing
    if not sections and text.strip():
        # Try splitting by newlines and filtering numbered items
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and re.match(r'^\d+\.', line):
                # Remove the number and period
                clean_line = re.sub(r'^\d+\.\s*', '', line).strip()
                if clean_line:
                    sections.append(clean_line)
        
        # If still no sections, return the original text as single item
        if not sections:
            sections = [text.strip()]
    
    return sections


def preprocess_excel_file(input_file_path, output_dir):
    """
    Process Excel file to extract and parse normalized_message_string.
    
    Args:
        input_file_path (str): Path to the input Excel file
        output_dir (str): Directory to save the processed file
    """
    try:
        # Read Excel file
        df = pd.read_excel(input_file_path)
        
        print(f"Loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
        
        # Check if normalized_message_string column exists
        if 'normalized_message_string' not in df.columns:
            print("Error: 'normalized_message_string' column not found in Excel file")
            return 0
        
        input_filename = Path(input_file_path).stem
        output_filename = f"processed_{input_filename}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        # Process each row
        processed_data = []
        total_messages = 0
        
        for idx, row in df.iterrows():
            # Create a dictionary with all original columns
            processed_row = {}
            
            # Copy all original columns except normalized_message_string
            for col in df.columns:
                if col != 'normalized_message_string':
                    # Handle NaN values
                    value = row[col]
                    if pd.isna(value):
                        processed_row[col] = None
                    else:
                        processed_row[col] = value
            
            # Process normalized_message_string
            raw_text = row['normalized_message_string']
            parsed_sections = parse_normalized_message_string(raw_text)
            processed_row['normalized_message_string'] = parsed_sections
            
            processed_data.append(processed_row)
            total_messages += len(parsed_sections)
            
            if (idx + 1) % 50 == 0:
                print(f"Processed {idx + 1} rows...")
        
        # Save processed data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"Processed {input_filename}: {len(processed_data)} rows, {total_messages} total text sections")
        return total_messages
        
    except Exception as e:
        print(f"Error processing {input_file_path}: {e}")
        return 0


def preprocess_excel_files(input_file, output_dir):
    """
    Process Excel files.
    
    Args:
        input_file (str): Path to the Excel file
        output_dir (str): Directory to save processed files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return 0
    
    print(f"Processing Excel file: {input_file}")
    
    messages_count = preprocess_excel_file(input_file, output_dir)
    
    print(f"\nExcel preprocessing completed!")
    print(f"Total text sections extracted: {messages_count}")
    print(f"Processed file saved to: {output_dir}")
    
    return messages_count


if __name__ == "__main__":
    input_file_path = "mhj_formatted.xlsx"
    output_directory = "processed_excel"
    
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found")
        exit(1)
    
    preprocess_excel_files(input_file_path, output_directory)
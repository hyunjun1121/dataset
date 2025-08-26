#!/usr/bin/env python3
"""
SafeMTData preprocessing script for Attack_600.json.
Extracts multi_turn_queries content for translation.
"""
import json
import os
from pathlib import Path


def preprocess_safemt_file(input_file_path, output_dir):
    """
    Process SafeMTData file to extract multi_turn_queries.
    
    Args:
        input_file_path (str): Path to the input JSON file
        output_dir (str): Directory to save the processed file
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        input_filename = Path(input_file_path).stem
        output_filename = f"processed_{input_filename}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        # Extract all multi_turn_queries
        all_queries = []
        
        for item in data:
            if "multi_turn_queries" in item and isinstance(item["multi_turn_queries"], list):
                # Add all queries from this item
                all_queries.extend(item["multi_turn_queries"])
        
        # Save processed data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_queries, f, ensure_ascii=False, indent=2)
        
        print(f"Processed {input_filename}: {len(all_queries)} queries extracted")
        return len(all_queries)
        
    except Exception as e:
        print(f"Error processing {input_file_path}: {e}")
        return 0


def preprocess_safedata_files(input_file, output_dir):
    """
    Process SafeMTData files.
    
    Args:
        input_file (str): Path to the Attack_600.json file
        output_dir (str): Directory to save processed files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return 0
    
    print(f"Processing SafeMTData file: {input_file}")
    
    queries_count = preprocess_safemt_file(input_file, output_dir)
    
    print(f"\nPreprocessing completed!")
    print(f"Total queries extracted: {queries_count}")
    print(f"Processed file saved to: {output_dir}")
    
    return queries_count


if __name__ == "__main__":
    input_file_path = "SafeMTData/Attack_600.json"
    output_directory = "processed_safedata"
    
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found")
        exit(1)
    
    preprocess_safedata_files(input_file_path, output_directory)
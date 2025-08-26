#!/usr/bin/env python3
"""
Dataset preprocessing script for CoSafe-Dataset.
Extracts user content from JSON files and saves them in processed format.
"""
import json
import os
from pathlib import Path


def preprocess_json_file(input_file_path, output_dir):
    """
    Process a single JSON file to extract user content.
    
    Args:
        input_file_path (str): Path to the input JSON file
        output_dir (str): Directory to save the processed file
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        input_filename = Path(input_file_path).stem
        output_filename = f"processed_{input_filename}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        all_user_contents = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                conversation = json.loads(line)
                
                # Extract user contents from this conversation
                user_contents = []
                for message in conversation:
                    if message.get("role") == "user":
                        user_contents.append(message.get("content", ""))
                
                # Add all user contents from this conversation
                all_user_contents.extend(user_contents)
                
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line {line_num} in {input_file_path}: {e}")
                continue
        
        # Save processed data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_user_contents, f, ensure_ascii=False, indent=2)
        
        print(f"Processed {input_filename}: {len(all_user_contents)} user messages extracted")
        return len(all_user_contents)
        
    except Exception as e:
        print(f"Error processing {input_file_path}: {e}")
        return 0


def preprocess_all_files(dataset_dir, output_dir):
    """
    Process all JSON files in the dataset directory.
    
    Args:
        dataset_dir (str): Directory containing the original JSON files
        output_dir (str): Directory to save processed files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all JSON files
    json_files = []
    for file in os.listdir(dataset_dir):
        if file.endswith('.json'):
            json_files.append(os.path.join(dataset_dir, file))
    
    print(f"Found {len(json_files)} JSON files to process")
    
    total_messages = 0
    for json_file in json_files:
        messages_count = preprocess_json_file(json_file, output_dir)
        total_messages += messages_count
    
    print(f"\nPreprocessing completed!")
    print(f"Total user messages extracted: {total_messages}")
    print(f"Processed files saved to: {output_dir}")


if __name__ == "__main__":
    dataset_directory = "CoSafe-Dataset"
    output_directory = "processed_data"
    
    if not os.path.exists(dataset_directory):
        print(f"Error: Dataset directory '{dataset_directory}' not found")
        exit(1)
    
    preprocess_all_files(dataset_directory, output_directory)
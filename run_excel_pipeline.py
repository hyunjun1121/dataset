#!/usr/bin/env python3
"""
Main pipeline script for Excel data preprocessing and translation.
Runs the complete pipeline from mhj_formatted.xlsx to translated datasets.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(command, description):
    """
    Execute a shell command and handle errors.
    
    Args:
        command (str): Command to execute
        description (str): Description of the command for logging
    """
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def check_requirements():
    """Check if required files exist."""
    print("Checking Excel processing requirements...")
    
    # Check if Excel file exists
    excel_file = "mhj_formatted.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Required file {excel_file} not found!")
        return False
    
    # Check if required scripts exist
    required_scripts = ["preprocess_excel.py", "translate_excel.py"]
    for script in required_scripts:
        if not os.path.exists(script):
            print(f"❌ Required script {script} not found!")
            return False
    
    print("✅ All Excel processing requirements satisfied!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run complete Excel data processing pipeline")
    parser.add_argument("--skip-preprocessing", action="store_true",
                       help="Skip preprocessing step (use existing processed data)")
    parser.add_argument("--skip-translation", action="store_true",
                       help="Skip translation step (only run preprocessing)")
    parser.add_argument("--languages", nargs='+', 
                       default=['en', 'zh', 'ar', 'es', 'sw'],
                       help="Target languages for translation")
    parser.add_argument("--batch-size", type=int, default=8,
                       help="Batch size for translation")
    parser.add_argument("--clean", action="store_true",
                       help="Clean output directories before running")
    
    args = parser.parse_args()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean directories if requested
    if args.clean:
        print("\nCleaning Excel output directories...")
        if os.path.exists("processed_excel"):
            import shutil
            shutil.rmtree("processed_excel")
            print("✅ Cleaned processed_excel directory")
        if os.path.exists("translated_excel"):
            import shutil
            shutil.rmtree("translated_excel")
            print("✅ Cleaned translated_excel directory")
    
    success = True
    
    # Step 1: Preprocessing
    if not args.skip_preprocessing:
        if not run_command("python preprocess_excel.py", "Excel data preprocessing"):
            success = False
    else:
        print("⏭️  Skipping preprocessing step")
        if not os.path.exists("processed_excel"):
            print("❌ Processed Excel data directory not found. Cannot skip preprocessing.")
            sys.exit(1)
    
    # Step 2: Translation
    if not args.skip_translation and success:
        lang_str = " ".join(args.languages)
        translation_cmd = f"python translate_excel.py --languages {lang_str} --batch_size {args.batch_size}"
        if not run_command(translation_cmd, "Excel data translation"):
            success = False
    elif args.skip_translation:
        print("⏭️  Skipping translation step")
    
    # Final summary
    print(f"\n{'='*50}")
    if success:
        print("🎉 Excel data pipeline completed successfully!")
        print("\nOutput directories:")
        if os.path.exists("processed_excel"):
            processed_files = len([f for f in os.listdir("processed_excel") if f.endswith('.json')])
            print(f"  - processed_excel/ ({processed_files} files)")
        if os.path.exists("translated_excel"):
            translated_files = len([f for f in os.listdir("translated_excel") if f.endswith('.json')])
            print(f"  - translated_excel/ ({translated_files} files)")
        
        # Show processing statistics
        if os.path.exists("processed_excel/processed_mhj_formatted.json"):
            import json
            with open("processed_excel/processed_mhj_formatted.json", 'r') as f:
                data = json.load(f)
            total_sections = sum(len(row.get('normalized_message_string', [])) for row in data)
            print(f"\nTotal rows processed: {len(data)}")
            print(f"Total text sections: {total_sections}")
            print(f"Expected translation files: {len(args.languages)} languages")
    else:
        print("❌ Excel data pipeline failed. Please check the error messages above.")
        sys.exit(1)
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
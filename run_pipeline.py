#!/usr/bin/env python3
"""
Main pipeline script for dataset preprocessing and translation.
Runs the complete pipeline from raw JSON files to translated datasets.
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
    """Check if required directories and files exist."""
    print("Checking requirements...")
    
    # Check if CoSafe-Dataset directory exists
    if not os.path.exists("CoSafe-Dataset"):
        print("❌ CoSafe-Dataset directory not found!")
        return False
    
    # Check if required scripts exist
    required_scripts = ["preprocess_dataset.py", "translate_dataset.py"]
    for script in required_scripts:
        if not os.path.exists(script):
            print(f"❌ Required script {script} not found!")
            return False
    
    print("✅ All requirements satisfied!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run complete dataset processing pipeline")
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
        print("\nCleaning output directories...")
        if os.path.exists("processed_data"):
            import shutil
            shutil.rmtree("processed_data")
            print("✅ Cleaned processed_data directory")
        if os.path.exists("translated_data"):
            import shutil
            shutil.rmtree("translated_data")
            print("✅ Cleaned translated_data directory")
    
    success = True
    
    # Step 1: Preprocessing
    if not args.skip_preprocessing:
        if not run_command("python preprocess_dataset.py", "Dataset preprocessing"):
            success = False
    else:
        print("⏭️  Skipping preprocessing step")
        if not os.path.exists("processed_data"):
            print("❌ Processed data directory not found. Cannot skip preprocessing.")
            sys.exit(1)
    
    # Step 2: Translation
    if not args.skip_translation and success:
        lang_str = " ".join(args.languages)
        translation_cmd = f"python translate_dataset.py --languages {lang_str} --batch_size {args.batch_size}"
        if not run_command(translation_cmd, "Dataset translation"):
            success = False
    elif args.skip_translation:
        print("⏭️  Skipping translation step")
    
    # Final summary
    print(f"\n{'='*50}")
    if success:
        print("🎉 Pipeline completed successfully!")
        print("\nOutput directories:")
        if os.path.exists("processed_data"):
            processed_files = len([f for f in os.listdir("processed_data") if f.endswith('.json')])
            print(f"  - processed_data/ ({processed_files} files)")
        if os.path.exists("translated_data"):
            translated_files = len([f for f in os.listdir("translated_data") if f.endswith('.json')])
            print(f"  - translated_data/ ({translated_files} files)")
    else:
        print("❌ Pipeline failed. Please check the error messages above.")
        sys.exit(1)
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
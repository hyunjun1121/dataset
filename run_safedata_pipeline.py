#!/usr/bin/env python3
"""
Main pipeline script for SafeMTData preprocessing and translation.
Runs the complete pipeline from Attack_600.json to translated datasets.
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
    print("Checking SafeMTData requirements...")
    
    # Check if SafeMTData directory and Attack_600.json exists
    attack_file = "SafeMTData/Attack_600.json"
    if not os.path.exists(attack_file):
        print(f"❌ Required file {attack_file} not found!")
        return False
    
    # Check if required scripts exist
    required_scripts = ["preprocess_safedata.py", "translate_safedata.py"]
    for script in required_scripts:
        if not os.path.exists(script):
            print(f"❌ Required script {script} not found!")
            return False
    
    print("✅ All SafeMTData requirements satisfied!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run complete SafeMTData processing pipeline")
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
        print("\nCleaning SafeMTData output directories...")
        if os.path.exists("processed_safedata"):
            import shutil
            shutil.rmtree("processed_safedata")
            print("✅ Cleaned processed_safedata directory")
        if os.path.exists("translated_safedata"):
            import shutil
            shutil.rmtree("translated_safedata")
            print("✅ Cleaned translated_safedata directory")
    
    success = True
    
    # Step 1: Preprocessing
    if not args.skip_preprocessing:
        if not run_command("python preprocess_safedata.py", "SafeMTData preprocessing"):
            success = False
    else:
        print("⏭️  Skipping preprocessing step")
        if not os.path.exists("processed_safedata"):
            print("❌ Processed SafeMTData directory not found. Cannot skip preprocessing.")
            sys.exit(1)
    
    # Step 2: Translation
    if not args.skip_translation and success:
        lang_str = " ".join(args.languages)
        translation_cmd = f"python translate_safedata.py --languages {lang_str} --batch_size {args.batch_size}"
        if not run_command(translation_cmd, "SafeMTData translation"):
            success = False
    elif args.skip_translation:
        print("⏭️  Skipping translation step")
    
    # Final summary
    print(f"\n{'='*50}")
    if success:
        print("🎉 SafeMTData pipeline completed successfully!")
        print("\nOutput directories:")
        if os.path.exists("processed_safedata"):
            processed_files = len([f for f in os.listdir("processed_safedata") if f.endswith('.json')])
            print(f"  - processed_safedata/ ({processed_files} files)")
        if os.path.exists("translated_safedata"):
            translated_files = len([f for f in os.listdir("translated_safedata") if f.endswith('.json')])
            print(f"  - translated_safedata/ ({translated_files} files)")
        
        # Show file details
        if os.path.exists("processed_safedata/processed_Attack_600.json"):
            import json
            with open("processed_safedata/processed_Attack_600.json", 'r') as f:
                queries = json.load(f)
            print(f"\nTotal queries processed: {len(queries)}")
            print(f"Expected translation files: {len(args.languages)} languages")
    else:
        print("❌ SafeMTData pipeline failed. Please check the error messages above.")
        sys.exit(1)
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
SafeMTData translation script using NLLB-200-3.3B model.
Translates processed SafeMTData queries to multiple languages.
"""
import json
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pathlib import Path
import argparse
from tqdm import tqdm


# Language mapping for NLLB-200 model
LANGUAGE_CODES = {
    'en': 'eng_Latn',  # English
    'zh': 'zho_Hans',  # Chinese (Simplified)
    'ar': 'arb_Arab',  # Arabic
    'es': 'spa_Latn',  # Spanish
    'sw': 'swh_Latn'   # Swahili
}

class SafeDataTranslator:
    def __init__(self, model_name="facebook/nllb-200-3.3B"):
        """
        Initialize the translator with NLLB model.
        
        Args:
            model_name (str): HuggingFace model identifier
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
    def load_model(self):
        """Load the NLLB model and tokenizer."""
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
        )
        self.model.to(self.device)
        print("Model loaded successfully!")
        
    def translate_text(self, text, src_lang="eng_Latn", tgt_lang="spa_Latn", max_length=512):
        """
        Translate a single text string.
        
        Args:
            text (str): Text to translate
            src_lang (str): Source language code
            tgt_lang (str): Target language code
            max_length (int): Maximum length for generation
            
        Returns:
            str: Translated text
        """
        if not text.strip():
            return text
            
        try:
            # Set source language
            self.tokenizer.src_lang = src_lang
            
            # Tokenize input
            inputs = self.tokenizer(
                text, 
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_lang],
                    max_length=max_length,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False
                )
            
            # Decode translation
            translation = self.tokenizer.batch_decode(
                generated_tokens, 
                skip_special_tokens=True
            )[0]
            
            return translation
            
        except Exception as e:
            print(f"Error translating text: {e}")
            return text  # Return original text if translation fails
    
    def translate_file(self, input_file, output_file, target_lang_code, batch_size=8):
        """
        Translate all queries in a JSON file.
        
        Args:
            input_file (str): Path to input JSON file
            output_file (str): Path to output JSON file
            target_lang_code (str): Target language code
            batch_size (int): Number of texts to process at once
        """
        # Load data
        with open(input_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        
        print(f"Translating {len(queries)} queries to {target_lang_code}")
        
        translated_queries = []
        
        # Process in batches to manage memory
        for i in tqdm(range(0, len(queries), batch_size), desc="Translating"):
            batch = queries[i:i+batch_size]
            batch_translations = []
            
            for query in batch:
                translation = self.translate_text(
                    query, 
                    src_lang="eng_Latn",
                    tgt_lang=LANGUAGE_CODES[target_lang_code]
                )
                batch_translations.append(translation)
            
            translated_queries.extend(batch_translations)
            
            # Clear GPU cache periodically
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
        
        # Save translated data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_queries, f, ensure_ascii=False, indent=2)
        
        print(f"Translation completed: {output_file}")

    def translate_processed_files(self, processed_dir, output_dir, target_languages):
        """
        Translate all processed files to target languages.
        
        Args:
            processed_dir (str): Directory containing processed files
            output_dir (str): Directory to save translated files
            target_languages (list): List of target language codes
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all processed JSON files
        processed_files = []
        for file in os.listdir(processed_dir):
            if file.startswith("processed_") and file.endswith(".json"):
                processed_files.append(file)
        
        if not processed_files:
            print(f"No processed files found in {processed_dir}")
            return
        
        print(f"Found {len(processed_files)} processed files")
        
        for lang_code in target_languages:
            print(f"\n--- Translating to {lang_code.upper()} ---")
            
            for processed_file in processed_files:
                input_path = os.path.join(processed_dir, processed_file)
                
                # Extract original filename
                original_name = processed_file.replace("processed_", "").replace(".json", "")
                output_filename = f"{lang_code}_translated_{original_name}.json"
                output_path = os.path.join(output_dir, output_filename)
                
                self.translate_file(input_path, output_path, lang_code)


def main():
    parser = argparse.ArgumentParser(description="Translate SafeMTData using NLLB-200-3.3B")
    parser.add_argument("--processed_dir", default="processed_safedata", 
                       help="Directory containing processed JSON files")
    parser.add_argument("--output_dir", default="translated_safedata", 
                       help="Directory to save translated files")
    parser.add_argument("--languages", nargs='+', 
                       default=['en', 'zh', 'ar', 'es', 'sw'],
                       help="Target languages to translate to")
    parser.add_argument("--batch_size", type=int, default=8,
                       help="Batch size for translation")
    
    args = parser.parse_args()
    
    # Validate languages
    for lang in args.languages:
        if lang not in LANGUAGE_CODES:
            print(f"Error: Unsupported language code '{lang}'")
            print(f"Supported languages: {list(LANGUAGE_CODES.keys())}")
            exit(1)
    
    # Check if processed directory exists
    if not os.path.exists(args.processed_dir):
        print(f"Error: Processed data directory '{args.processed_dir}' not found")
        print("Please run preprocess_safedata.py first")
        exit(1)
    
    # Initialize translator
    translator = SafeDataTranslator()
    translator.load_model()
    
    # Translate all files
    translator.translate_processed_files(
        args.processed_dir,
        args.output_dir,
        args.languages
    )
    
    print("\nAll SafeMTData translations completed!")


if __name__ == "__main__":
    main()
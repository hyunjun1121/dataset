# M2S Dataset Processing and Translation Pipeline

This repository contains scripts to preprocess and translate both CoSafe-Dataset and SafeMTData using the NLLB-200-3.3B model.

## Overview

The pipeline consists of three main components:
1. **Preprocessing**: Extract user content from conversational JSON files
2. **Translation**: Translate extracted content to multiple languages using NLLB-200-3.3B
3. **Pipeline Management**: Automated execution of the complete workflow

## File Structure

```
M2S-main/
├── CoSafe-Dataset/             # Original CoSafe dataset files
├── SafeMTData/                 # SafeMTData files (Attack_600.json)
├── mhj_formatted.xlsx          # Excel data file
├── processed_data/             # Preprocessed CoSafe user content (generated)
├── processed_safedata/         # Preprocessed SafeMTData queries (generated)
├── processed_excel/            # Preprocessed Excel data (generated)
├── translated_data/            # Translated CoSafe content (generated)
├── translated_safedata/        # Translated SafeMTData content (generated)
├── translated_excel/           # Translated Excel data (generated)
├── preprocess_dataset.py       # CoSafe preprocessing script
├── preprocess_safedata.py      # SafeMTData preprocessing script
├── preprocess_excel.py         # Excel preprocessing script
├── translate_dataset.py        # CoSafe translation script
├── translate_safedata.py       # SafeMTData translation script
├── translate_excel.py          # Excel translation script
├── run_pipeline.py             # CoSafe pipeline runner
├── run_safedata_pipeline.py    # SafeMTData pipeline runner
├── run_excel_pipeline.py       # Excel pipeline runner
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone [your-repository-url]
cd M2S-main
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Datasets
Ensure the following directories and files exist:
- `CoSafe-Dataset/` directory contains JSON files
- `SafeMTData/Attack_600.json` file exists
- `mhj_formatted.xlsx` file exists

## Usage

### For CoSafe-Dataset

#### Option 1: Run Complete CoSafe Pipeline
```bash
python run_pipeline.py
```

### For SafeMTData

#### Option 1: Run Complete SafeMTData Pipeline
```bash
python run_safedata_pipeline.py
```

### For Excel Data

#### Option 1: Run Complete Excel Pipeline
```bash
python run_excel_pipeline.py
```

### Option 2: Run Steps Separately

#### CoSafe Dataset
```bash
# Preprocessing only
python preprocess_dataset.py

# Translation only (after preprocessing)
python translate_dataset.py
```

#### SafeMTData
```bash
# Preprocessing only
python preprocess_safedata.py

# Translation only (after preprocessing)
python translate_safedata.py
```

#### Excel Data
```bash
# Preprocessing only
python preprocess_excel.py

# Translation only (after preprocessing)
python translate_excel.py
```

#### Custom Translation Options
```bash
# CoSafe Dataset
python translate_dataset.py --languages en zh ar --batch_size 4

# SafeMTData
python translate_safedata.py --languages en zh ar --batch_size 4

# Excel Data
python translate_excel.py --languages en zh ar --batch_size 4
```

### Pipeline Options

#### CoSafe Dataset
```bash
python run_pipeline.py --skip-preprocessing
python run_pipeline.py --skip-translation
python run_pipeline.py --clean --languages en zh ar
```

#### SafeMTData
```bash
python run_safedata_pipeline.py --skip-preprocessing
python run_safedata_pipeline.py --skip-translation
python run_safedata_pipeline.py --clean --languages en zh ar
```

#### Excel Data
```bash
python run_excel_pipeline.py --skip-preprocessing
python run_excel_pipeline.py --skip-translation
python run_excel_pipeline.py --clean --languages en zh ar
```

## Supported Languages

- `en`: English
- `zh`: Chinese (Simplified)
- `ar`: Arabic
- `es`: Spanish  
- `sw`: Swahili

## Output Format

### CoSafe Dataset
#### Preprocessed Files
- Location: `processed_data/`
- Naming: `processed_[original_filename].json`
- Format: Array of user content strings

#### Translated Files
- Location: `translated_data/`
- Naming: `[language]_translated_[original_filename].json`

### SafeMTData
#### Preprocessed Files
- Location: `processed_safedata/`
- Naming: `processed_Attack_600.json`
- Format: Array of multi_turn_queries strings

#### Translated Files
- Location: `translated_safedata/`
- Naming: `[language]_translated_Attack_600.json`

### Excel Data
#### Preprocessed Files
- Location: `processed_excel/`
- Naming: `processed_mhj_formatted.json`
- Format: Array of row objects with parsed normalized_message_string
```json
[
  {
    "Source": "DERTA",
    "temperature": 0.0,
    "tactic": "Direct Request",
    "normalized_message_string": [
      "What statistics are available on the use of handguns...",
      "More than a million juvenile arrests involved...",
      ...
    ],
    ...
  }
]
```

#### Translated Files
- Location: `translated_excel/`
- Naming: `[language]_translated_mhj_formatted.json`
- Format: Same structure with translated normalized_message_string arrays

## Server Deployment Instructions

### 1. Upload to Server
```bash
git add .
git commit -m "Add dataset processing pipeline"
git push origin main
```

### 2. On Remote Server
```bash
# Clone repository
git clone [your-repository-url]
cd M2S-main

# Install dependencies
pip install -r requirements.txt

# Run CoSafe pipeline
python run_pipeline.py

# Run SafeMTData pipeline  
python run_safedata_pipeline.py

# Run Excel pipeline
python run_excel_pipeline.py

# Or run with custom settings
python run_pipeline.py --batch-size 4 --languages en zh ar
python run_safedata_pipeline.py --batch-size 4 --languages en zh ar
python run_excel_pipeline.py --batch-size 4 --languages en zh ar
```

### 3. Monitor Progress
The scripts provide detailed progress information including:
- Number of files processed
- Translation progress with tqdm progress bars
- Memory usage warnings
- Error handling and recovery

### 4. Expected Output

#### CoSafe Dataset
- **Preprocessing**: ~4,200 user messages extracted from 14 files
- **Translation**: 5 language versions × 14 files = 70 translated files

#### SafeMTData
- **Preprocessing**: ~2,996 queries extracted from Attack_600.json
- **Translation**: 5 language versions × 1 file = 5 translated files

#### Excel Data
- **Preprocessing**: ~2,185 text sections extracted from 463 rows
- **Translation**: 5 language versions × 1 file = 5 translated files

- **Total Runtime**: Depends on hardware (GPU recommended for translation)

## System Requirements

- **GPU**: Recommended for translation (CUDA-compatible)
- **RAM**: Minimum 16GB, 32GB+ recommended for larger batches
- **Storage**: ~5GB for model cache + dataset files
- **Python**: 3.8+

## Troubleshooting

### Memory Issues
- Reduce batch size: `--batch-size 2`
- Use CPU instead of GPU if facing CUDA memory errors
- Close other applications to free RAM

### Translation Errors
- Check internet connection (for model download)
- Verify HuggingFace access
- Ensure sufficient disk space for model cache

### File Access Issues
- Verify file permissions
- Check directory paths
- Ensure CoSafe-Dataset directory exists
# DocCraft

A comprehensive document processing and question-answering toolkit.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Installation](#installation)
3. [CLI Options Table](#cli-options-table)
4. [Command-Line Interface (CLI) Usage](#command-line-interface-cli-usage)
5. [Running DocVQA Benchmarks (Step-by-Step)](#running-docvqa-benchmarks-step-by-step)
6. [Modular Architecture](#modular-architecture)
7. [Understanding DocCraft Components](#understanding-doccraft-components)
    - [Preprocessor/Postprocessor Output Examples](#preprocessorpostprocessor-output-examples)
8. [Advanced Usage](#advanced-usage)
9. [FAQ & Troubleshooting](#faq--troubleshooting)
10. [Links & Further Reading](#links--further-reading)
11. [License](#license)

---

## Project Overview

DocCraft is a Python package for intelligent document parsing, OCR, and benchmarking. It supports both traditional and AI-powered parsers, and provides a unified interface for:
- Text extraction from images and PDFs
- Preprocessing and postprocessing
- Benchmarking against datasets like DocVQA
- Extensible architecture for custom workflows

### Project Structure

```text
DocCraft/
  README.md
  CHANGELOG.md
  LICENSE
  MANIFEST.in
  requirements.txt
  setup.py
  src/
    doccraft/
      __init__.py
      cli.py
      benchmarking/
        __init__.py
        base_benchmarker.py
        accuracy_benchmarker.py
        performance_benchmarker.py
        docvqa_benchmarker.py
      parsers/
        __init__.py
        base_parser.py
        base_ai_parser.py
        pdf_parser.py
        pdfplumber_parser.py
        tesseract_parser.py
        paddle_ocr_parser.py
        layoutlmv3_parser.py
        qwen_vl_parser.py
        deepseek_vl_parser.py
      preprocessing/
        __init__.py
        base_preprocessor.py
        image_preprocessor.py
        pdf_preprocessor.py
      postprocessing/
        __init__.py
        base_postprocessor.py
        text_postprocessor.py
        table_postprocessor.py
      DeepSeek-VL/
        ...
  docs/        (included in source distribution)
  examples/    (not packaged)
  tests/       (not packaged)
```

Notes:
- The wheel contains `src/doccraft/**` and package metadata; examples and tests are excluded.
- `docs/` are included in the source distribution (sdist); `examples/` are excluded.

---

## Installation

### 1. **Requirements**
- Python 3.8 or newer
- pip (latest recommended)
- For AI features: a machine with sufficient RAM/VRAM, and optionally a CUDA-capable GPU

### 2. **Core Installation**
```bash
pip install doccraft-toolkit
```

### 3. **AI Features (LayoutLMv3, Qwen-VL, DeepSeek-VL)**
```bash
pip install "doccraft-toolkit[ai]"
```
> This installs all dependencies for AI parsers (transformers, torch, etc).

#### **DeepSeek-VL Special Step**
DeepSeek-VL must be installed from source:
```bash
git clone https://github.com/deepseek-ai/DeepSeek-VL
cd DeepSeek-VL
pip install -e .
cd ..  # Return to your project root
```

### 4. **Development Tools**
```bash
pip install "doccraft-toolkit[dev]"
```
> Installs testing, linting, and code quality tools.

### 5. **Complete Installation (AI + Dev)**
```bash
pip install "doccraft-toolkit[all]"
```

### 6. **Troubleshooting Installation**
- If you see errors about missing `torch`, `transformers`, or `paddleocr`, ensure you used the `[ai]` or `[all]` extras.
- For DeepSeek-VL, you **must** install from source as above.
- For GPU support, ensure you have the correct CUDA version and PyTorch build.

---

## Running DocVQA Benchmarks (Step-by-Step)

### 1. **Download DocVQA Data**
- **Register for a free account:** [DocVQA Registration](https://rrc.cvc.uab.es/?com=contestant)
- **Go to downloads:** [DocVQA Downloads](https://rrc.cvc.uab.es/?ch=17&com=downloads)
- Under **Task 1 - Single Page Document Visual Question Answering**, download both **Annotations** and **Images**.
- This will give you two folders: `spdocvqa_images` and `spdocvqa_qas`.
- Inside `spdocvqa_qas`, the file `val_v1.0_withQT.json` is the ground truth file.
- The `spdocvqa_images` folder contains all the images.

### 2. **Run the DocVQA Benchmark (AI Parsers Only)**
> **Note:** Only AI parsers (`layoutlmv3`, `qwenvl`, `deepseekvl`) are designed for visual question answering. Running non-AI parsers on DocVQA is technically possible, but they cannot answer questions and results will not be meaningful.

#### **Example: Run Qwen-VL on DocVQA**
```bash
doccraft benchmark --ground_truth spdocvqa_qas/val_v1.0_withQT.json --documents spdocvqa_images --parser qwenvl --max_questions 1
```

#### **Example: Run LayoutLMv3 on DocVQA**
```bash
doccraft benchmark --ground_truth spdocvqa_qas/val_v1.0_withQT.json --documents spdocvqa_images --parser layoutlmv3 --max_questions 1
```

#### **Example: Run DeepSeek-VL on DocVQA**
```bash
doccraft benchmark --ground_truth spdocvqa_qas/val_v1.0_withQT.json --documents spdocvqa_images --parser deepseekvl --max_questions 1
```

#### **Example: Run All Parsers (for comparison)**
```bash
doccraft benchmark --ground_truth spdocvqa_qas/val_v1.0_withQT.json --documents spdocvqa_images --all_parsers --max_questions 1
```

- `--max_questions 1` is for a quick test. Remove it to run the full benchmark.
- Results are saved in the `results/` directory.


After running a DocVQA benchmark, you will find the following files in the `results/` directory:

- **Raw results file:**
  - Example: `qwenvl_results_YYYYMMDD_HHMMSS.json`
  - Contains all predictions, metrics, and for each prediction, a `ground_truth` field with the correct answer(s) from the dataset.
  - Example:
    ```json
    {
      "parser": "qwenvl",
      "total_questions": 1,
      "predictions": [
        {
          "questionId": 49153,
          "question": "What is the 'actual' value per 1000, during the year 1975?",
          "image": "pybv0228_81.png",
          "predicted_answer": "8.22",
          "confidence": 1.0,
          "extracted_text": "8.22",
          "processing_time": 10.7,
          "ground_truth": ["0.28"]
        }
      ],
      "metrics": { /* ... */ }
    }
    ```
- **Flat predictions file:**
  - Example: `qwenvl_task1_predictions.json`
  - Contains a flat list of predictions for easy evaluation.

### 3. **Interpreting Results**
- Results are saved in the `results/` directory:
  - `*_predictions.json`: Flat predictions
  - `*_results_*.json`: Raw results
- Metrics include: Exact Match Rate, Normalized Match Rate, Average Similarity, Confidence, Processing Time.

**You can use the `doccraft evaluate` command to compare, summarize, and visualize these results files.**
For example:
```bash
doccraft evaluate --results results/qwenvl_results_20250101_120000.json results/layoutlmv3_results_20250101_120000.json --visualize
```
This will generate a summary and (optionally) plots comparing the selected runs.

### 4. **Troubleshooting**
- **Missing dependencies:**  
  - For AI parsers, ensure you installed with `[ai]` and followed DeepSeek-VL instructions.
- **CUDA/Device errors:**  
  - Use `device="cpu"` if you lack a compatible GPU.
- **Parser not found:**  
  - Use one of: `layoutlmv3`, `qwenvl`, `deepseekvl` (for DocVQA).

---

## Modular Architecture

DocCraft is built with a modular, object-oriented architecture that makes it easy to extend and customize. Each subpackage follows a consistent pattern with abstract base classes and concrete implementations.

### **Registry Systems**

Each subpackage includes a registry system for dynamic component lookup:

#### **Parser Registry**
- **Location:** `src/doccraft/parsers/__init__.py`
- **Registry:** `PARSER_REGISTRY`
- **Function:** `get_parser(parser_name: str)`
- **Usage:** `from doccraft.parsers import get_parser; parser = get_parser('tesseract')`

#### **Preprocessor Registry**
- **Location:** `src/doccraft/preprocessing/__init__.py`
- **Registry:** `PREPROCESSOR_REGISTRY`
- **Function:** `get_preprocessor(preprocessor_name: str)`
- **Usage:** `from doccraft.preprocessing import get_preprocessor; preproc = get_preprocessor('image')`

#### **Postprocessor Registry**
- **Location:** `src/doccraft/postprocessing/__init__.py`
- **Registry:** `POSTPROCESSOR_REGISTRY`
- **Function:** `get_postprocessor(postprocessor_name: str)`
- **Usage:** `from doccraft.postprocessing import get_postprocessor; postproc = get_postprocessor('text')`

#### **Benchmarker Registry**
- **Location:** `src/doccraft/benchmarking/__init__.py`
- **Registry:** `BENCHMARKER_REGISTRY`
- **Function:** `get_benchmarker(benchmarker_name: str, **kwargs)`
- **Usage:** `from doccraft.benchmarking import get_benchmarker; bench = get_benchmarker('accuracy')`

### **Base Classes and Inheritance**

#### **Parsers Subpackage**
**Base Class:** `BaseParser` (abstract)
- **Key Functions:** `extract_text()`, `can_parse()`, `get_parser_info()`
- **Inheriting Modules:** `PDFParser`, `PDFPlumberParser`, `TesseractParser`, `PaddleOCRParser`
- **AI Base Class:** `BaseAIParser` (extends `BaseParser`)
- **AI Inheriting Modules:** `LayoutLMv3Parser`, `DeepSeekVLParser`, `QwenVLParser`

#### **Preprocessors Subpackage**
**Base Class:** `BasePreprocessor` (abstract)
- **Key Functions:** `process()`, `can_process()`, `get_preprocessor_info()`
- **Inheriting Modules:** `ImagePreprocessor`, `PDFPreprocessor`

#### **Postprocessors Subpackage**
**Base Class:** `BasePostprocessor` (abstract)
- **Key Functions:** `process()`, `can_process()`, `get_postprocessor_info()`
- **Inheriting Modules:** `TextPostprocessor`, `TablePostprocessor`

#### **Benchmarkers Subpackage**
**Base Class:** `BaseBenchmarker` (abstract)
- **Key Functions:** `benchmark()`, `calculate_metrics()`, `generate_report()`
- **Inheriting Modules:** `AccuracyBenchmarker`, `PerformanceBenchmarker`, `DocVQABenchmarker`

### **Extension Patterns**

- **Registry Pattern:** All components are registered in their respective subpackage's `__init__.py`
- **Factory Pattern:** `get_*()` functions provide a clean interface for component instantiation
- **Strategy Pattern:** Components can be swapped at runtime via the CLI or programmatically
- **Error Handling:** Invalid component names raise descriptive `ValueError` exceptions with available options

---

## Understanding DocCraft Components

- **Core Parsers:**  
  - `tesseract` (Tesseract OCR)
  - `paddleocr` (PaddleOCR)
  - `pdf` (PyMuPDF)
  - `pdfplumber` (pdfplumber)
- **AI Parsers:**  
  - `layoutlmv3` (LayoutLMv3, HuggingFace)
  - `qwenvl` (Qwen-VL, HuggingFace)
  - `deepseekvl` (DeepSeek-VL, from source)
- **Preprocessors:**  
  - `image` (input: image file path, output: processed image file path + metadata)
  - `pdf` (input: PDF file path, output: processed PDF file path or directory + metadata)
- **Postprocessors:**  
  - `text` (input: text string, output: processed text string + metadata)
  - `table` (input: table data as list of lists or dict, output: file path to table + metadata)
- **Benchmarkers:**  
  - `docvqa` (DocVQA evaluation)
  - `accuracy`, `performance`

**Preprocessor/Postprocessor Data Types:**

| Name                | Input Type(s)                        | Output Type(s)                                 |
|---------------------|--------------------------------------|------------------------------------------------|
| ImagePreprocessor   | str or Path (image file path)        | (str or Path, dict) (processed image, metadata) |
| PDFPreprocessor     | str or Path (PDF file path)          | (str or Path, dict) (file/dir, metadata)        |
| TextPostprocessor   | str (text)                           | (str, dict) (processed text, metadata)          |
| TablePostprocessor  | list[list[str]] or dict (table data) | (str or Path, dict) (file path, metadata)       |

**Note:** `str or Path` means you can provide either a string file path (e.g., 'file.pdf') or a `pathlib.Path` object as input/output.

---

### Preprocessor/Postprocessor Output Examples

#### ImagePreprocessor
- **Input:** Path to an image file (e.g., 'input.jpg')
- **Output:** Tuple of (output image path, metadata dict)

**Metadata Example:**
```json
{
  "input_path": "input.jpg",
  "output_path": "processed_input.jpg",
  "processing_steps": ["resize", "deskew", "denoise", "contrast_enhancement"],
  "image_info": {
    "original_size": [1080, 1920, 3],
    "original_width": 1920,
    "original_height": 1080,
    "channels": 3
  },
  "enhancement_applied": true,
  "final_size": [1080, 1920, 3],
  "final_width": 1920,
  "final_height": 1080
}
```

#### PDFPreprocessor
- **Input:** Path to a PDF file (e.g., 'input.pdf')
- **Output:** Tuple of (output file/dir path, metadata dict)

**Metadata Example (split):**
```json
{
  "input_path": "input.pdf",
  "operation": "split",
  "output_files": ["input_part_001.pdf", "input_part_002.pdf"],
  "total_pages": 10,
  "split_ranges": [[0, 4], [5, 9]]
}
```
**Metadata Example (convert):**
```json
{
  "input_path": "input.pdf",
  "operation": "convert",
  "output_format": "png",
  "dpi": 300,
  "output_files": ["input_page_001.png", "input_page_002.png"],
  "total_pages": 2
}
```

#### TextPostprocessor
- **Input:** Text string
- **Output:** Tuple of (processed text string, metadata dict)

**Metadata Example:**
```json
{
  "original_length": 1234,
  "processing_steps": [
    "remove_extra_whitespace",
    "fix_line_breaks",
    "normalize_quotes",
    "fix_common_ocr_errors"
  ],
  "text_statistics": {
    "word_count": 200,
    "sentence_count": 15,
    "paragraph_count": 5,
    "character_count": 1200,
    "average_word_length": 5.2,
    "average_sentence_length": 13.3
  },
  "output_format": "text",
  "final_length": 1200
}
```

#### TablePostprocessor
- **Input:** Table data as a list of lists or a dict (e.g., from a parser)
- **Output:** Tuple of (output file path, metadata dict)

**Metadata Example:**
```json
{
  "original_rows": 12,
  "original_columns": 5,
  "processing_steps": [
    "clean_cells",
    "remove_empty_rows",
    "remove_empty_columns",
    "normalize_headers"
  ],
  "output_format": "csv",
  "table_statistics": {
    "row_count": 10,
    "column_count": 4,
    "total_cells": 40,
    "empty_cells": 2,
    "non_empty_cells": 38,
    "fill_rate": 95.0
  },
  "final_rows": 10,
  "final_columns": 4,
  "output_path": "processed_table.csv"
}
```

---

**Pipeline Flow:**  
Preprocessing → Parsing (OCR/AI) → Postprocessing → (Optional) Benchmarking

---

## Quick Start

### 1. **Check Installation**
```bash
doccraft --help
```
Should print the CLI help.

### 2. **Minimal Python Example**
```python
from doccraft.parsers import TesseractParser, PaddleOCRParser, DeepSeekVLParser, QwenVLParser, LayoutLMv3Parser

tesseract = TesseractParser()
result = tesseract.extract_text("tests/data/ocr_test.jpg")
print(result['text'])

deepseek = DeepSeekVLParser()
result = deepseek.extract_text("tests/data/ocr_test.jpg")
print(result['text'])
```

### 3. **Minimal CLI Example**
```bash
# Core OCR
doccraft --input tests/data/ocr_test.jpg --parser tesseract

# AI OCR (Qwen-VL)
doccraft --input tests/data/ocr_test.jpg --parser qwenvl
```

---

## CLI Options Table

### Pipeline Command Options

| Long Option         | Short | Required | Description                                                      |
|---------------------|-------|----------|------------------------------------------------------------------|
| --input             | -i    | Yes      | Input document path                                              |
| --parser            | -p    | Yes      | Parser name (e.g., tesseract, paddleocr, pdf, layoutlmv3, etc.)  |
| --preprocessor      | -r    | No       | Preprocessor name (optional)                                     |
| --postprocessor     | -s    | No       | Postprocessor name (optional)                                    |
| --benchmarker       | -b    | No       | Benchmarker name (optional)                                      |
| --benchmark_gt      | -g    | No       | Ground truth for benchmarking (if needed)                        |
| --benchmark_images  | -d    | No       | Images dir for DocVQA benchmarker (if needed)                    |
| --config            | -c    | No       | JSON config file (overrides CLI args)                            |
| --prompt            |       | No       | Prompt or question for AI parsers (optional, no short option)    |
| --verbose           | -v    | No       | Verbose output                                                   |

### Benchmark Command Options

| Long Option         | Short | Required | Description                                                      |
|---------------------|-------|----------|------------------------------------------------------------------|
| --ground_truth      | -g    | Yes      | Path to DocVQA ground truth JSON file                            |
| --documents         | -d    | Yes      | Directory containing document images                             |
| --parser            | -p    | No       | Parser to use (default: layoutlmv3)                             |
| --all_parsers       | -a    | No       | Benchmark all available parsers                                  |
| --max_questions     |       | No       | Maximum number of questions to process (for testing)             |
| --output_dir        | -o    | No       | Output directory for results (default: results)                  |
| --verbose           | -v    | No       | Enable verbose output                                            |
| --save_predictions  |       | No       | Save individual predictions to separate files                    |
| --compare           |       | No       | Generate comparison report when using --all_parsers              |

### Evaluate Command Options

| Long Option   | Short | Required | Description                                                      |
|--------------|-------|----------|------------------------------------------------------------------|
| --results     | -r    | Yes      | Path(s) to results JSON file(s) to compare                       |
| --visualize   | -v    | No       | Visualize the comparison with plots                              |
| --output      | -o    | No       | Path to save the evaluation summary (JSON)                       |

---

## Command-Line Interface (CLI) Usage

DocCraft provides a powerful CLI for all major workflows.

### **Show Help**
```bash
doccraft --help
doccraft pipeline --help
doccraft benchmark --help
doccraft evaluate --help
```

### **Pipeline Command**
Process a document with any parser:
```bash
# Long options (recommended)
doccraft --input path/to/document.pdf --parser paddleocr

# Short options
doccraft -i path/to/document.pdf -p paddleocr

# With pre/post-processing
doccraft --input path/to/image.png --parser tesseract --preprocessor image --postprocessor text

# With a custom prompt/question (for AI parsers)
doccraft --input path/to/image.png --parser layoutlmv3 --prompt "What is the invoice number?"
```
> **Note:** You can use either long or short options.  
> **Underscores are required** in long option names (e.g., `--input`, `--parser`).
> The `--prompt` option is only used by AI parsers and is optional. There is currently **no short option** for `--prompt`.

### **Benchmark Command**
Run DocVQA or other benchmarks:
```bash
# Single parser (core or AI)
doccraft benchmark --ground_truth path/to/gt.json --documents path/to/images --parser layoutlmv3

# All available parsers
doccraft benchmark --ground_truth path/to/gt.json --documents path/to/images --all_parsers

# Limit number of questions (for quick test)
doccraft benchmark --ground_truth path/to/gt.json --documents path/to/images --parser qwenvl --max_questions 5

# Short options
doccraft benchmark -g path/to/gt.json -d path/to/images -p deepseekvl
```
> Results are saved in the `results/` directory by default.

---

### **Evaluate Command**
Compare and visualize results from one or more DocVQA benchmark runs:

```bash
# Compare two or more result files and visualize with plots
doccraft evaluate --results results1.json results2.json --visualize

# Save the evaluation summary to a file
doccraft evaluate --results results1.json results2.json --output summary.json
```

The `evaluate` subcommand allows you to:
- Compare metrics across multiple benchmark result files
- Generate summary tables and (optionally) visual plots
- Save the evaluation summary to a JSON file

---

## Advanced Usage

### **Adding New Components**

To add a new component to any subpackage:

1. **Create your class** by inheriting from the appropriate base class
2. **Add it to the registry** in the subpackage's `__init__.py` file
3. **Update the `__all__` list** to include your new class
4. **The CLI will automatically recognize** your new component

**Example - Adding a new parser:**
```python
# In src/doccraft/parsers/my_parser.py
from .base_parser import BaseParser

class MyCustomParser(BaseParser):
    def __init__(self):
        super().__init__(
            name="MyCustomParser",
            version="1.0.0",
            supported_formats=['.txt', '.md']
        )
    
    def _extract_text_impl(self, file_path, **kwargs):
        # Your implementation
        text = "extracted text"
        metadata = {"custom": "data"}
        return text, metadata

# In src/doccraft/parsers/__init__.py
from .my_parser import MyCustomParser

PARSER_REGISTRY['mycustom'] = MyCustomParser
__all__.append('MyCustomParser')
```

**📖 See `examples/custom_component_example.py` for complete examples of custom parsers, preprocessors, postprocessors, and benchmarkers.**

### **Custom Pipeline Configuration**

You can specify preprocessor and postprocessor:
```bash
doccraft --input path/to/image.png --parser tesseract --preprocessor image --postprocessor text
```

You can pass a JSON config file to override CLI args:
```bash
doccraft --config my_config.json
```

### **Using Config Files**
You can pass a JSON config file to override CLI args:
```bash
doccraft --config my_config.json
```

### **Extending DocCraft**
- Add your own parser by subclassing `BaseParser` or `BaseAIParser` and registering it in `PARSER_REGISTRY`.

---

## FAQ & Troubleshooting

- **Q: Why do I get "Parser not found"?**  
  A: Check the parser name (see above for valid names).

- **Q: Why does the CLI say "argument required"?**  
  A: Make sure you use underscores in long option names (e.g., `--ground_truth`).

- **Q: How do I use GPU?**  
  A: Install the correct CUDA version and PyTorch build. Most AI parsers auto-detect GPU.

- **Q: How do I install DeepSeek-VL?**  
  A: See the [Installation](#installation) section above.

- **Q: Where are results saved?**  
  A: In the `results/` directory by default.

---

## Links & Further Reading

- [DocVQA Integration Guide](docs/DOCVQA_INTEGRATION.md)
- [API Documentation](https://doccraft.readthedocs.io/) *(if available)*
- [GitHub Repository](https://github.com/WuSimon/DocCraft)
- [PyPI Project Page](https://pypi.org/project/doccraft-toolkit/)
- [DeepSeek-VL GitHub](https://github.com/deepseek-ai/DeepSeek-VL)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**If you have any issues, please open an issue on [GitHub](https://github.com/WuSimon/DocCraft/issues).**

---

**All commands and examples above have been verified to work with the current version of DocCraft.**  
If you encounter any errors, please check the FAQ or open an issue.

---
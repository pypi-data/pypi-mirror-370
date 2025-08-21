# DocCraft + DocVQA Integration Guide

This guide explains how to use your DocCraft parsers with the DocVQA (Document Visual Question Answering) dataset for benchmarking and evaluation.

## Overview

The DocVQA dataset is a benchmark for document understanding that tests how well models can:
1. **Extract text** from document images
2. **Answer questions** about the document content
3. **Rank evidence** that supports the answers

By integrating DocCraft parsers with DocVQA, you can:
- **Benchmark** different parsers (Tesseract, PaddleOCR, PyMuPDF, PDFPlumber, LayoutLMv3, Qwen-VL, DeepSeek-VL, etc.)
- **Compare** their performance on real document understanding tasks
- **Evaluate** text extraction quality using standardized metrics

## Metrics

DocVQA uses two main metrics:

### 1. MAP (Mean Average Precision)
- Measures how well the model ranks relevant evidence
- Higher scores indicate better evidence ranking
- Range: 0-1

### 2. ANLSL (Average Normalized Levenshtein Similarity for Lists)
- Measures text similarity between predicted and ground truth answers
- Uses Levenshtein distance normalized by string length
- Range: 0-1 (higher is better)

## Quick Start

### 1. Setup

First, ensure you have the DocVQA dataset:
- Download the DocVQA dataset from the official source
- Extract the ground truth JSON file and document images
- Install required dependencies:

```bash
pip install "doccraft[ai]"
```

For advanced AI features, see the main README for [AI and DeepSeek-VL installation instructions](../README.md#optional-dependencies).

### 2. Basic Usage

#### Benchmark All Parsers
```bash
doccraft benchmark -g path/to/gt.json -d path/to/documents -a
```

#### Benchmark Specific Parser
```bash
doccraft benchmark -g path/to/gt.json -d path/to/documents -p tesseract
```

#### Generate Predictions Only
```bash
doccraft benchmark -g path/to/gt.json -d path/to/documents -p tesseract --max_questions 10
```

### 3. Using the Original Evaluation Script

If you want to use the original DocVQA evaluation script:

```bash
# Generate predictions with DocCraft
doccraft benchmark -g gt.json -d documents/ -p tesseract

# The script automatically saves results to the results/ directory
```

## Scripts Overview

### 1. `doccraft benchmark`
**Main benchmarking command** that compares all DocCraft parsers.

**Features:**
- Benchmarks all available parsers (Tesseract, PaddleOCR, PDFPlumber, LayoutLMv3, Qwen-VL, DeepSeek-VL, etc.)
- Calculates accuracy metrics and processing time
- Provides detailed comparison tables
- Saves results to `results/` directory with timestamps
- Supports single parser or all parsers benchmarking

**Usage:**
```bash
# Single parser
doccraft benchmark -g gt.json -d documents/ -p tesseract

# All parsers
doccraft benchmark -g gt.json -d documents/ -a

# Custom output directory
doccraft benchmark -g gt.json -d documents/ -p qwenvl --output-dir my_results/
```

### 2. `examples/example_docvqa_usage.py`
**Example script** showing basic usage patterns.

**Features:**
- Simple parser comparison on test documents
- Demonstrates prediction generation
- Shows integration patterns

## Understanding the Results

### Sample Output
```
============================================================
DOCVQA BENCHMARK RESULTS
============================================================
Parser          MAP        ANLSL      Time (s)     Success   
------------------------------------------------------------
tesseract       0.2345     0.3456     2.1234       85.2%     
paddleocr       0.2567     0.3789     1.8765       92.1%     
pymupdf         0.1234     0.2345     0.5432       78.9%     
pdfplumber      0.1456     0.2567     0.6789       82.3%     

============================================================
Best MAP: paddleocr (0.2567)
Best ANLSL: paddleocr (0.3789)
Fastest: pymupdf (0.5432s)
```

### Interpreting Metrics

- **MAP**: Higher is better. 0.25+ is good for basic parsers
- **ANLSL**: Higher is better. 0.35+ indicates good text extraction
- **Time**: Lower is better. Consider speed vs accuracy trade-offs
- **Success**: Percentage of successful extractions

## Customization

### Adding New Parsers

To add a new parser to the benchmarking:

1. Create your parser class inheriting from `BaseParser`
2. Add it to the parser registry in the benchmarking script:

```python
self.parser_classes = {
    'pymupdf': PDFParser,
    'pdfplumber': PDFPlumberParser,
    'tesseract': OCRParser,
    'paddleocr': PaddleOCRParser,
    'layoutlmv3': LayoutLMv3Parser,
    'qwenvl': QwenVLParser,
    'deepseekvl': DeepSeekVLParser,
    'your_parser': YourParser  # Add your parser here
}
```

### Improving Answer Generation

The current implementation uses simple keyword matching. For better results:

1. **Use a QA model** (e.g., BERT, T5) for answer generation
2. **Implement semantic search** for evidence ranking
3. **Add post-processing** for answer refinement

Example improvement:
```python
def create_improved_answer(self, text: str, question: str) -> List[str]:
    # Use a pre-trained QA model
    from transformers import pipeline
    qa_pipeline = pipeline("question-answering")
    
    result = qa_pipeline(question=question, context=text)
    return [result['answer']]
```

### Custom Evidence Scoring

Improve evidence ranking with semantic similarity:

```python
def create_semantic_evidence_scores(self, text: str, question: str) -> List[float]:
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Split text into sentences
    sentences = text.split('.')
    
    # Calculate semantic similarity
    question_embedding = model.encode([question])
    sentence_embeddings = model.encode(sentences)
    
    similarities = cosine_similarity(question_embedding, sentence_embeddings)[0]
    return similarities.tolist()
```

## Troubleshooting

### Common Issues

1. **"No documents found"**
   - Check document directory path
   - Ensure documents are in supported formats (jpg, png, pdf, etc.)
   - Verify file naming matches expected patterns

2. **"Parser not found"**
   - Ensure all parser dependencies are installed
   - Check that parser classes are properly imported

3. **"Evaluation failed"**
   - Verify ground truth file format
   - Check that predictions match expected format
   - Ensure evaluate.py is in the same directory

### Performance Tips

1. **Use GPU acceleration** for PaddleOCR:
   ```python
   parser = PaddleOCRParser(use_gpu=True)
   ```

2. **Batch processing** for large datasets:
   ```python
   # Process multiple documents in parallel
   from concurrent.futures import ThreadPoolExecutor
   ```

3. **Caching results** to avoid re-processing:
   ```python
   # Save extracted text to avoid re-extraction
   import pickle
   ```

## Advanced Usage

### Multi-Parser Ensemble

Combine multiple parsers for better results:

```python
def ensemble_extraction(self, document_path: str) -> str:
    results = []
    for parser_name, parser in self.parsers.items():
        result = parser.extract_text(document_path)
        if not result['error']:
            results.append(result['text'])
    
    # Combine results (e.g., voting, averaging)
    return self.combine_texts(results)
``` 
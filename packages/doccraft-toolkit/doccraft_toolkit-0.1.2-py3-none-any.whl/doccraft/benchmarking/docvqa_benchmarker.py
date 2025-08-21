import json
import os
import re
import time
import argparse
import sys
import warnings
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import pandas as pd
from datetime import datetime

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*image_processor_class.*")
warnings.filterwarnings("ignore", message=".*use_fast.*")
warnings.filterwarnings("ignore", message=".*legacy.*")
warnings.filterwarnings("ignore", message=".*device.*")

# Set environment variables to suppress tokenizer warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

try:
    from .base_benchmarker import BaseBenchmarker
except ImportError:
    # Fallback for when running as script
    from base_benchmarker import BaseBenchmarker

class DocVQABenchmarker(BaseBenchmarker):
    """
    Benchmarker for the DocVQA dataset using DocCraft parsers.
    Now supports parser registry, string-based selection, question limiting, and script-compatible output.
    """
    def __init__(self, dataset_json: Union[str, Path] = None, images_dir: Union[str, Path] = None, eval_script_path: Union[str, Path] = None, gt_json: Union[str, Path] = None):
        super().__init__(name="DocVQABenchmarker", version="1.0.0", supported_metrics=["MAP", "ANLSL"])
        self.dataset_json = str(dataset_json) if dataset_json else None
        self.images_dir = str(images_dir) if images_dir else None
        self.eval_script_path = str(eval_script_path) if eval_script_path else None
        self.gt_json = str(gt_json) if gt_json else None
        self.data = []
        if self.dataset_json:
            with open(self.dataset_json, 'r') as f:
                self.data = json.load(f)["data"]
        # Parser registry (can be extended)
        try:
            from doccraft.parsers import (
                PaddleOCRParser, PDFPlumberParser, 
                LayoutLMv3Parser, DeepSeekVLParser, QwenVLParser, TesseractParser, PDFParser
            )
        except ImportError:
            try:
                # Fallback for when running as script
                import sys
                sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
                from doccraft.parsers import (
                    PaddleOCRParser, PDFPlumberParser, 
                    LayoutLMv3Parser, DeepSeekVLParser, QwenVLParser, TesseractParser, PDFParser
                )
            except ImportError:
                # Fallback for testing
                class MockParser:
                    def __init__(self, name):
                        self.name = name
                    def extract_text(self, image_path):
                        return f"Mock text from {self.name} for {image_path}"
                PaddleOCRParser = lambda: MockParser("paddleocr")
                PDFPlumberParser = lambda: MockParser("pdfplumber")
                LayoutLMv3Parser = lambda: MockParser("layoutlmv3")
                DeepSeekVLParser = lambda: MockParser("deepseekvl")
                QwenVLParser = lambda: MockParser("qwenvl")
                TesseractParser = lambda: MockParser("tesseract")
                PDFParser = lambda: MockParser("pdf")
        self.parser_classes = {
            'paddleocr': PaddleOCRParser,
            'pdfplumber': PDFPlumberParser,
            'layoutlmv3': LayoutLMv3Parser,
            'deepseekvl': DeepSeekVLParser,
            'qwenvl': lambda: QwenVLParser(device_mode='cpu'),
            'tesseract': TesseractParser,
            'pdf': PDFParser,
        }
        self.parsers = {}

    def load_ground_truth(self, gt_path: str) -> Dict[str, Any]:
        with open(gt_path, 'r') as f:
            return json.load(f)

    def get_parser(self, parser_name: str):
        if parser_name not in self.parser_classes:
            raise ValueError(f"Unknown parser: {parser_name}. Available: {list(self.parser_classes.keys())}")
        if parser_name not in self.parsers:
            self.parsers[parser_name] = self.parser_classes[parser_name]()
        return self.parsers[parser_name]

    def extract_text_from_document(self, parser, image_path: str, documents_dir: str) -> str:
        if image_path.startswith('documents/'):
            image_path = image_path.replace('documents/', '')
        full_path = os.path.join(documents_dir, image_path)
        if not os.path.exists(full_path):
            print(f"Warning: Image not found: {full_path}")
            return ""
        try:
            if hasattr(parser, 'extract_text'):
                return parser.extract_text(full_path)
            else:
                return parser.extract_text(full_path)
        except Exception as e:
            print(f"Error extracting text from {full_path}: {e}")
            return ""

    def generate_answer(self, question: str, extracted_text: str) -> str:
        if not extracted_text:
            return "No answer"
        question_lower = question.lower()
        # Look for numbers
        if any(word in question_lower for word in ['how much', 'what is the', 'amount', 'number', 'percentage', '%']):
            numbers = re.findall(r'\d+(?:\.\d+)?', extracted_text)
            if numbers:
                return numbers[0]
        # Look for dates
        if any(word in question_lower for word in ['when', 'date', 'year']):
            dates = re.findall(r'\d{4}', extracted_text)
            if dates:
                return dates[0]
        # Look for names
        if any(word in question_lower for word in ['who', 'name', 'person']):
            names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', extracted_text)
            if names:
                return names[0]
        # Default: first sentence
        sentences = extracted_text.split('.')
        if sentences:
            return sentences[0].strip()
        return "No answer"

    def benchmark(self, ground_truth_path: str, documents_dir: str, parser_name: str, max_questions: Optional[int] = None) -> Dict[str, Any]:
        print(f"\n=== Benchmarking {parser_name.upper()} on DocVQA Task 1 ===")
        gt_data = self.load_ground_truth(ground_truth_path)
        questions = gt_data['data']
        if max_questions:
            questions = questions[:max_questions]
        print(f"Processing {len(questions)} questions...")
        parser = self.get_parser(parser_name)
        start_time = time.time()
        predictions = []
        for idx, q in enumerate(questions):
            question_id = q['questionId']
            question = q['question']
            image_path = q['image']
            # Patch: strip 'documents/' prefix if present
            if image_path.startswith('documents/'):
                image_path = image_path[len('documents/'):]
            ground_truth_answers = q.get('answers', [])
            full_image_path = os.path.join(documents_dir, image_path)
            prediction_start_time = time.time()
            if not os.path.exists(full_image_path):
                print(f"Warning: Image not found: {full_image_path}")
                predicted_answer = "No answer"
                confidence = 0.0
                extracted_text = ""
            else:
                try:
                    if hasattr(parser, 'ask_question'):
                        result = parser.ask_question(full_image_path, question)
                        predicted_answer = result.get('answer', 'No answer')
                        confidence = result.get('confidence', 0.0)
                        extracted_text = result.get('raw_answer', '')
                    else:
                        extracted_text = self.extract_text_from_document(parser, image_path, documents_dir)
                        predicted_answer = self.generate_answer(question, extracted_text)
                        confidence = 1.0
                except Exception as e:
                    print(f"Error processing question {question_id}: {e}")
                    predicted_answer = f"Error: {e}"
                    confidence = 0.0
                    extracted_text = ""
            processing_time = time.time() - prediction_start_time
            predictions.append({
                'questionId': question_id,
                'question': question,
                'image': image_path,
                'predicted_answer': predicted_answer,
                'confidence': confidence,
                'extracted_text': extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
                'processing_time': processing_time,
                'ground_truth': ground_truth_answers
            })
            # Print progress every 10 questions
            if (idx + 1) % 10 == 0 or (idx + 1) == len(questions):
                elapsed = time.time() - start_time
                mins = int(elapsed // 60)
                secs = int(elapsed % 60)
                print(f"{idx + 1}/{len(questions)} questions, elapsed time: {mins}m {secs}s")
        elapsed_time = time.time() - start_time
        # Calculate metrics
        metrics = self.calculate_metrics(predictions, gt_data)
        average_confidence = sum(p['confidence'] for p in predictions) / len(predictions) if predictions else 0.0
        average_processing_time = sum(p['processing_time'] for p in predictions) / len(predictions) if predictions else 0.0
        results = {
            'parser': parser_name,
            'total_questions': len(questions),
            'elapsed_time_seconds': elapsed_time,
            'predictions': predictions,
            'metrics': metrics,
            'average_confidence': average_confidence,
            'average_processing_time': average_processing_time
        }
        print(f"\u2713 Completed {parser_name} benchmark")
        return results

    def benchmark_all_parsers(self, ground_truth_path: str, documents_dir: str, max_questions: Optional[int] = None) -> Dict[str, Any]:
        print("DOCVQA TASK 1 BENCHMARK RESULTS")
        print("=" * 50)
        all_results = {
            'dataset': 'DocVQA Task 1',
            'ground_truth_path': ground_truth_path,
            'documents_dir': documents_dir,
            'parsers': {}
        }
        for parser_name in self.parser_classes.keys():
            try:
                results = self.benchmark(ground_truth_path, documents_dir, parser_name, max_questions)
                all_results['parsers'][parser_name] = results
            except Exception as e:
                print(f"Error benchmarking {parser_name}: {e}")
                all_results['parsers'][parser_name] = {
                    'parser': parser_name,
                    'error': str(e)
                }
        return all_results

    def save_results(self, results: Dict[str, Any], output_path: str):
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    def generate_predictions_file(self, ground_truth_path: str, documents_dir: str, parser_name: str, output_path: str, max_questions: Optional[int] = None) -> None:
        # Always use unified format for predictions file
        results = self.benchmark(ground_truth_path, documents_dir, parser_name, max_questions)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\u2713 Predictions saved to: {output_path}")

    @staticmethod
    def normalize_text(text: str) -> str:
        import re
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    @staticmethod
    def get_normalized_forms(text: str):
        from num2words import num2words
        import inflect
        p = inflect.engine()
        forms = set()
        norm = DocVQABenchmarker.normalize_text(text)
        forms.add(norm)
        try:
            num = float(norm.replace(",", ""))
            if num.is_integer():
                word = num2words(int(num))
            else:
                word = num2words(num)
            forms.add(DocVQABenchmarker.normalize_text(word))
        except Exception:
            pass
        try:
            num = p.number_to_words(norm)
            if num != norm:
                num_val = float(num.replace(",", ""))
                forms.add(DocVQABenchmarker.normalize_text(str(int(num_val)) if num_val.is_integer() else str(num_val)))
        except Exception:
            pass
        return forms

    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        from difflib import SequenceMatcher
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1, str2).ratio()

    @staticmethod
    def calculate_metrics(predictions: list, ground_truth: dict) -> dict:
        total_questions = 0
        exact_matches = 0
        normalized_matches = 0
        high_similarity = 0
        medium_similarity = 0
        low_similarity = 0
        no_match = 0
        total_similarity = 0.0
        for gt_item in ground_truth['data']:
            question_id = gt_item['questionId']
            gt_answers = gt_item.get('answers', [''])
            pred_item = next((p for p in predictions if p['questionId'] == question_id), None)
            if not pred_item:
                continue
            pred_answer = pred_item.get('predicted_answer', '')
            gt_answer = gt_answers[0] if gt_answers else ''
            gt_forms = DocVQABenchmarker.get_normalized_forms(gt_answer)
            pred_forms = DocVQABenchmarker.get_normalized_forms(pred_answer)
            gt_normalized = DocVQABenchmarker.normalize_text(gt_answer)
            pred_normalized = DocVQABenchmarker.normalize_text(pred_answer)
            similarity = DocVQABenchmarker.calculate_similarity(gt_normalized, pred_normalized)
            total_similarity += similarity
            total_questions += 1
            if gt_answer == pred_answer:
                exact_matches += 1
            elif gt_forms & pred_forms:
                normalized_matches += 1
            if similarity >= 0.8:
                high_similarity += 1
            elif similarity >= 0.5:
                medium_similarity += 1
            elif similarity >= 0.2:
                low_similarity += 1
            else:
                no_match += 1
        avg_similarity = total_similarity / total_questions if total_questions > 0 else 0.0
        return {
            'total_questions': total_questions,
            'exact_matches': exact_matches,
            'normalized_matches': normalized_matches,
            'high_similarity': high_similarity,
            'medium_similarity': medium_similarity,
            'low_similarity': low_similarity,
            'no_match': no_match,
            'average_similarity': avg_similarity,
            'exact_match_rate': exact_matches / total_questions if total_questions else 0.0,
            'normalized_match_rate': normalized_matches / total_questions if total_questions else 0.0,
            'high_similarity_rate': high_similarity / total_questions if total_questions else 0.0,
            'medium_similarity_rate': medium_similarity / total_questions if total_questions else 0.0,
            'low_similarity_rate': low_similarity / total_questions if total_questions else 0.0,
            'no_match_rate': no_match / total_questions if total_questions else 0.0
        }

    @staticmethod
    def generate_report(results: Dict[str, Any], output_dir: str, parser_name: str) -> None:
        """Generate comprehensive benchmark report (raw results and flat predictions only)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(output_dir, exist_ok=True)
        # Save raw results
        results_file = os.path.join(output_dir, f"{parser_name}_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        # Always save flat predictions file for evaluation
        if 'predictions' in results:
            flat_file = os.path.join(output_dir, f"{parser_name}_task1_predictions.json")
            with open(flat_file, 'w') as f:
                json.dump(results['predictions'], f, indent=2)
            print(f"  - Flat predictions: {flat_file}")
        print(f"\nResults saved to:")
        print(f"  - Raw results: {results_file}")

    @staticmethod
    def compare_parsers(results_dict: Dict[str, Dict], output_dir: str) -> None:
        """Compare results across multiple parsers."""
        comparison_data = []
        
        for parser_name, results in results_dict.items():
            if 'metrics' in results:
                metrics = results['metrics']
                comparison_data.append({
                    'parser': parser_name,
                    'exact_match_accuracy': metrics.get('exact_match_accuracy', 0),
                    'partial_match_accuracy': metrics.get('partial_match_accuracy', 0),
                    'total_questions': metrics.get('total_questions', 0),
                    'average_confidence': results.get('average_confidence', 0),
                    'average_processing_time': results.get('average_processing_time', 0)
                })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comparison_file = os.path.join(output_dir, f"parser_comparison_{timestamp}.csv")
            df.to_csv(comparison_file, index=False)
            
            print(f"\nParser comparison saved to: {comparison_file}")
            print("\nParser Comparison Summary:")
            print(df.to_string(index=False))

    @staticmethod
    def main():
        """Main CLI entry point for DocVQA benchmarking."""
        parser = argparse.ArgumentParser(
            description="Comprehensive DocVQA benchmarking with DocCraft parsers",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Benchmark single parser
  doccraft benchmark -g gt.json -d documents/ -p layoutlmv3
  
  # Benchmark all parsers
  doccraft benchmark -g gt.json -d documents/ -a
  
  # Quick test with limited questions
  doccraft benchmark -g gt.json -d documents/ -p tesseract --max_questions 50
  
  # Generate detailed report
  doccraft benchmark -g gt.json -d documents/ -p deepseekvl --output-dir results/
            """
        )
        
        # Required arguments
        parser.add_argument('--ground_truth', '-g', required=True,
                           help="Path to DocVQA Task 1 ground truth JSON file")
        parser.add_argument('--documents', '-d', required=True,
                           help="Directory containing document images")
        
        # Optional arguments
        parser.add_argument('--parser', '-p', default='layoutlmv3',
                           choices=['layoutlmv3', 'deepseekvl', 'qwenvl', 'tesseract', 'paddleocr', 'pdfplumber'],
                           help="Parser to use (default: layoutlmv3)")
        parser.add_argument('--all_parsers', '-a', action='store_true',
                           help="Benchmark all available parsers")
        parser.add_argument('--max_questions', type=int,
                           help="Maximum number of questions to process (for testing)")
        parser.add_argument('--output_dir', '-o', default='results',
                           help="Output directory for results (default: results)")
        parser.add_argument('--verbose', '-v', action='store_true',
                           help="Enable verbose output")
        parser.add_argument('--save_predictions', action='store_true',
                           help="Save individual predictions to separate files")
        parser.add_argument('--compare', action='store_true',
                           help="Generate comparison report when using --all_parsers")
        
        args = parser.parse_args()
        
        # Validate inputs
        if not os.path.exists(args.ground_truth):
            print(f"Error: Ground truth file not found: {args.ground_truth}")
            return 1
        if not os.path.exists(args.documents):
            print(f"Error: Documents directory not found: {args.documents}")
            return 1
        
        # Load ground truth for evaluation
        try:
            with open(args.ground_truth, 'r') as f:
                ground_truth = json.load(f)
            print(f"Loaded ground truth with {len(ground_truth.get('data', []))} questions")
        except Exception as e:
            print(f"Error loading ground truth: {e}")
            return 1
        
        benchmarker = DocVQABenchmarker()
        
        print(f"\n{'='*80}")
        print(f"DOCVQA TASK 1 BENCHMARK")
        print(f"{'='*80}")
        print(f"Ground truth: {args.ground_truth}")
        print(f"Documents: {args.documents}")
        print(f"Max questions: {args.max_questions or 'All'}")
        print(f"Output directory: {args.output_dir}")
        
        if args.all_parsers:
            print(f"Benchmarking all available parsers...")
            parsers = ['layoutlmv3', 'deepseekvl', 'qwenvl', 'tesseract', 'paddleocr', 'pdfplumber']
            all_results = {}
            
            for parser_name in parsers:
                try:
                    print(f"\n--- Benchmarking {parser_name.upper()} ---")
                    start_time = time.time()
                    
                    results = benchmarker.benchmark(
                        args.ground_truth, args.documents, parser_name, args.max_questions
                    )
                    
                    # Calculate metrics
                    if 'predictions' in results:
                        metrics = DocVQABenchmarker.calculate_metrics(results['predictions'], ground_truth)
                        results['metrics'] = metrics
                        
                        # Calculate average confidence and processing time
                        if results['predictions']:
                            confidences = [pred.get('confidence', 0) for pred in results['predictions']]
                            processing_times = [pred.get('processing_time', 0) for pred in results['predictions']]
                            results['average_confidence'] = sum(confidences) / len(confidences)
                            results['average_processing_time'] = sum(processing_times) / len(processing_times)
                    
                    all_results[parser_name] = results
                    
                    # Generate individual report
                    DocVQABenchmarker.generate_report(results, args.output_dir, parser_name)
                    
                    elapsed_time = time.time() - start_time
                    print(f"Completed in {elapsed_time:.2f} seconds")
                    
                    if args.verbose and 'metrics' in results:
                        metrics = results['metrics']
                        print(f"  Exact Match Accuracy: {metrics['exact_match_accuracy']:.3f}")
                        print(f"  Partial Match Accuracy: {metrics['partial_match_accuracy']:.3f}")
                    
                except Exception as e:
                    print(f"Error benchmarking {parser_name}: {e}")
                    continue
            
            if args.compare:
                DocVQABenchmarker.compare_parsers(all_results, args.output_dir)
        
        else:
            print(f"\n--- Benchmarking {args.parser.upper()} ---")
            start_time = time.time()
            
            try:
                results = benchmarker.benchmark(
                    args.ground_truth, args.documents, args.parser, args.max_questions
                )
                
                # Calculate metrics
                if 'predictions' in results:
                    metrics = DocVQABenchmarker.calculate_metrics(results['predictions'], ground_truth)
                    results['metrics'] = metrics
                    
                    # Calculate averages
                    if results['predictions']:
                        confidences = [pred.get('confidence', 0) for pred in results['predictions']]
                        processing_times = [pred.get('processing_time', 0) for pred in results['predictions']]
                        results['average_confidence'] = sum(confidences) / len(confidences)
                        results['average_processing_time'] = sum(processing_times) / len(processing_times)
                
                # Generate report
                DocVQABenchmarker.generate_report(results, args.output_dir, args.parser)
                
                elapsed_time = time.time() - start_time
                print(f"\nBenchmark completed in {elapsed_time:.2f} seconds")
                
                if 'metrics' in results:
                    metrics = results['metrics']
                    print(f"\nResults Summary:")
                    print(f"  Total Questions: {metrics['total_questions']}")
                    print(f"  Exact Match Accuracy: {metrics['exact_match_accuracy']:.3f}")
                    print(f"  Partial Match Accuracy: {metrics['partial_match_accuracy']:.3f}")
                    print(f"  Average Confidence: {results.get('average_confidence', 0):.3f}")
                    print(f"  Average Processing Time: {results.get('average_processing_time', 0):.3f}s")
            
            except Exception as e:
                print(f"Error during benchmarking: {e}")
                return 1
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK COMPLETED")
        print(f"{'='*80}")
        return 0


if __name__ == "__main__":
    sys.exit(DocVQABenchmarker.main()) 
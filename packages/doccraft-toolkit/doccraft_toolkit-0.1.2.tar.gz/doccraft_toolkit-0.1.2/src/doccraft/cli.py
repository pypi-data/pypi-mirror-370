import sys
import os
import json
from pathlib import Path
import argparse

# Import DocCraft registries and classes
from doccraft.parsers import PARSER_REGISTRY, get_parser
from doccraft.preprocessing import PREPROCESSOR_REGISTRY, get_preprocessor
from doccraft.postprocessing import POSTPROCESSOR_REGISTRY, get_postprocessor
from doccraft.benchmarking import BENCHMARKER_REGISTRY, get_benchmarker

def run_pipeline(cfg):
    # Load preprocessor
    preprocessor = None
    if cfg.get('preprocessor'):
        try:
            preprocessor = get_preprocessor(cfg['preprocessor'])
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Load parser
    try:
        parser = get_parser(cfg['parser'])
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load postprocessor
    postprocessor = None
    if cfg.get('postprocessor'):
        try:
            postprocessor = get_postprocessor(cfg['postprocessor'])
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Load benchmarker
    benchmarker = None
    if cfg.get('benchmarker'):
        try:
            if cfg['benchmarker'] == 'docvqa':
                # DocVQABenchmarker needs dataset and images
                benchmarker = get_benchmarker(cfg['benchmarker'], 
                                            ground_truth_path=cfg.get('benchmark_gt'),
                                            images_dir=cfg.get('benchmark_images'))
            else:
                benchmarker = get_benchmarker(cfg['benchmarker'])
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Load input
    input_path = cfg['input']
    data = input_path
    if preprocessor:
        print(f"[Pipeline] Preprocessing with {preprocessor.__class__.__name__}")
        data = preprocessor.process(data)
        if isinstance(data, tuple):
            data, _ = data
    print(f"[Pipeline] Parsing with {parser.__class__.__name__}")
    # Pass prompt if present in cfg
    extract_kwargs = {}
    if cfg.get('prompt'):
        extract_kwargs['prompt'] = cfg['prompt']
    parsed = parser.extract_text(data, **extract_kwargs)
    result_text = parsed['text']
    if postprocessor:
        print(f"[Pipeline] Postprocessing with {postprocessor.__class__.__name__}")
        post_result = postprocessor.process(result_text)
        if isinstance(post_result, tuple):
            result_text, _ = post_result
        else:
            result_text = post_result
    print("[Pipeline] Extraction result:")
    print(result_text[:500] + ("..." if len(result_text) > 500 else ""))
    if benchmarker:
        print(f"[Pipeline] Benchmarking with {benchmarker.__class__.__name__}")
        # For accuracy, expects parser and file_path
        if cfg['benchmarker'] == 'accuracy':
            metrics = benchmarker.benchmark(parser, input_path)
        elif cfg['benchmarker'] == 'performance':
            metrics = benchmarker.benchmark(parser, input_path)
        elif cfg['benchmarker'] == 'docvqa':
            metrics = benchmarker.benchmark(parser, input_path)
        else:
            metrics = None
        print("[Pipeline] Benchmark results:")
        print(json.dumps(metrics, indent=2))

def main():
    # If no subcommand is given but --input/-i or --parser/-p is present, default to 'pipeline'
    if len(sys.argv) > 1 and sys.argv[1] not in {'pipeline', 'benchmark', '-h', '--help'}:
        # Check for --input, --parser, -i, or -p in the arguments
        if any(
            arg.startswith('--input') or arg.startswith('--parser') or arg == '-i' or arg == '-p'
            for arg in sys.argv[1:]
        ):
            sys.argv.insert(1, 'pipeline')

    parser = argparse.ArgumentParser(description="DocCraft Modular Pipeline CLI")
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # Default pipeline command (legacy)
    parser_pipeline = subparsers.add_parser('pipeline', help='Run a custom pipeline (default)')
    parser_pipeline.add_argument('--input', '-i', type=str, help='Input document path')
    parser_pipeline.add_argument('--parser', '-p', type=str, help='Parser name (e.g., tesseract, paddleocr, pdf, pdfplumber, layoutlmv3, etc.)')
    parser_pipeline.add_argument('--preprocessor', '-r', type=str, default=None, help='Preprocessor name (optional)')
    parser_pipeline.add_argument('--postprocessor', '-s', type=str, default=None, help='Postprocessor name (optional)')
    parser_pipeline.add_argument('--benchmarker', '-b', type=str, default=None, help='Benchmarker name (optional)')
    parser_pipeline.add_argument('--benchmark_gt', '-g', type=str, default=None, help='Ground truth for benchmarking (if needed)')
    parser_pipeline.add_argument('--benchmark_images', '-d', type=str, default=None, help='Images dir for DocVQA benchmarker (if needed)')
    parser_pipeline.add_argument('--config', '-c', type=str, default=None, help='JSON config file (overrides CLI args)')
    parser_pipeline.add_argument('--prompt', type=str, default=None, help='Prompt or question for AI parsers (optional)')
    parser_pipeline.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Benchmark command
    parser_benchmark = subparsers.add_parser('benchmark', help='Run DocVQA benchmarks')
    parser_benchmark.add_argument('--ground_truth', '-g', required=True, help='Path to DocVQA ground truth JSON file')
    parser_benchmark.add_argument('--documents', '-d', required=True, help='Directory containing document images')
    parser_benchmark.add_argument('--parser', '-p', default='layoutlmv3', help='Parser to use')
    parser_benchmark.add_argument('--all_parsers', '-a', action='store_true', help='Benchmark all available parsers')
    parser_benchmark.add_argument('--max_questions', type=int, help='Maximum number of questions to process')
    parser_benchmark.add_argument('--output_dir', '-o', default='results', help='Output directory for results')
    parser_benchmark.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser_benchmark.add_argument('--save_predictions', action='store_true', help='Save individual predictions to separate files')
    parser_benchmark.add_argument('--compare', action='store_true', help='Generate comparison report when using --all_parsers')

    # Evaluate subcommand
    parser_evaluate = subparsers.add_parser('evaluate', help='Compare and visualize DocVQA benchmark results')
    parser_evaluate.add_argument('--results', '-r', type=str, nargs='+', required=True, help='Path(s) to results JSON file(s)')
    parser_evaluate.add_argument('--visualize', '-v', action='store_true', help='Visualize the comparison with plots')
    parser_evaluate.add_argument('--output', '-o', type=str, default=None, help='Path to save the evaluation summary (JSON)')

    args = parser.parse_args()

    if args.command == 'benchmark':
        # Import and call the unified benchmarker
        from doccraft.benchmarking.docvqa_benchmarker import DocVQABenchmarker
        import json
        import time
        
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
                    if 'answers' in results:
                        metrics = DocVQABenchmarker.calculate_metrics(results['answers'], ground_truth)
                        results['metrics'] = metrics
                        
                        # Calculate average confidence and processing time
                        if results['answers']:
                            confidences = [ans.get('confidence', 0) for ans in results['answers']]
                            processing_times = [ans.get('processing_time', 0) for ans in results['answers']]
                            results['average_confidence'] = sum(confidences) / len(confidences)
                            results['average_processing_time'] = sum(processing_times) / len(processing_times)
                    
                    all_results[parser_name] = results
                    
                    # Generate individual report
                    DocVQABenchmarker.generate_report(results, args.output_dir, parser_name)
                    
                    elapsed_time = time.time() - start_time
                    print(f"Completed in {elapsed_time:.2f} seconds")
                    
                    if args.verbose and 'metrics' in results:
                        metrics = results['metrics']
                        print(f"  Exact Match Rate: {metrics['exact_match_rate']:.3f}")
                        print(f"  Normalized Match Rate: {metrics['normalized_match_rate']:.3f}")
                        print(f"  Average Similarity: {metrics['average_similarity']:.3f}")
                    
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
                    print(f"  Exact Match Rate: {metrics['exact_match_rate']:.3f}")
                    print(f"  Normalized Match Rate: {metrics['normalized_match_rate']:.3f}")
                    print(f"  Average Similarity: {metrics['average_similarity']:.3f}")
                    print(f"  High Similarity Rate: {metrics['high_similarity_rate']:.3f}")
                    print(f"  Average Confidence: {results.get('average_confidence', 0):.3f}")
                    print(f"  Average Processing Time: {results.get('average_processing_time', 0):.3f}s")
            
            except Exception as e:
                print(f"Error during benchmarking: {e}")
                return 1
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK COMPLETED")
        print(f"{'='*80}")
        return 0

    elif args.command == 'evaluate':
        from doccraft.benchmarking.evaluate import evaluate_results
        evaluate_results(args.results, visualize=args.visualize, output_path=args.output)
        return 0

    elif args.command == 'pipeline' or not args.command:
        # Use the new run_pipeline function with registry systems
        if not args.input:
            print("Error: --input is required for pipeline command")
            return 1
        
        if not args.parser:
            print("Error: --parser is required for pipeline command")
            return 1
        
        # Build configuration dict for run_pipeline
        cfg = {
            'input': args.input,
            'parser': args.parser,
            'preprocessor': args.preprocessor,
            'postprocessor': args.postprocessor,
            'benchmarker': args.benchmarker,
            'benchmark_gt': args.benchmark_gt,
            'benchmark_images': args.benchmark_images,
            'prompt': args.prompt,
            'verbose': args.verbose
        }
        
        # Run the pipeline with new registry systems
        run_pipeline(cfg)
        return 0

    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

def extract_metrics(results_json):
    metrics = results_json.get('metrics', {})
    return {
        'parser': results_json.get('parser', ''),
        'total_questions': results_json.get('total_questions', 0),
        'exact_match_rate': metrics.get('exact_match_rate', 0),
        'normalized_match_rate': metrics.get('normalized_match_rate', 0),
        'average_similarity': metrics.get('average_similarity', 0),
        'average_confidence': results_json.get('average_confidence', 0),
        'average_processing_time': results_json.get('average_processing_time', 0),
    }

def evaluate_results(results_files, visualize=False, output_path=None):
    rows = []
    for file in results_files:
        with open(file, 'r') as f:
            data = json.load(f)
        metrics = extract_metrics(data)
        metrics['file'] = os.path.basename(file)
        rows.append(metrics)
    df = pd.DataFrame(rows)
    print('\n=== DocVQA Benchmark Comparison ===')
    print(df.to_markdown(index=False))
    if visualize:
        df.set_index('file')[['exact_match_rate', 'normalized_match_rate', 'average_similarity', 'average_confidence']].plot.bar(rot=45)
        plt.title('DocVQA Benchmark Metrics Comparison')
        plt.ylabel('Score')
        plt.tight_layout()
        plt.show()
    if output_path:
        df.to_json(output_path, orient='records', indent=2)
        print(f'\nEvaluation summary saved to {output_path}') 
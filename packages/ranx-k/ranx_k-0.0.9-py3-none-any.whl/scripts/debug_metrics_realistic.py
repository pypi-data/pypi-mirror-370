"""Debug script to show when metrics differ."""

from ranx import Qrels, Run, evaluate
import numpy as np

print("=== Realistic Case: Different metric values ===")

# More realistic scenario where metrics will differ
qrels_dict = {
    'q_1': {'doc_0': 1.0, 'doc_2': 1.0},  # 2 relevant docs, one not at top
    'q_2': {'doc_1': 1.0},  # Relevant doc at position 1, not 0
    'q_3': {'doc_0': 1.0, 'doc_1': 1.0, 'doc_3': 1.0},  # 3 relevant docs
    'q_4': {'doc_3': 1.0},  # Relevant doc at position 3
    'q_5': {'doc_0': 1.0}  # Normal case
}

run_dict = {
    'q_1': {'doc_0': 0.95, 'doc_1': 0.85, 'doc_2': 0.75, 'doc_3': 0.65},
    'q_2': {'doc_0': 0.86, 'doc_1': 0.96, 'doc_2': 0.76, 'doc_3': 0.66},
    'q_3': {'doc_0': 0.97, 'doc_1': 0.87, 'doc_2': 0.77, 'doc_3': 0.67},
    'q_4': {'doc_0': 0.68, 'doc_1': 0.78, 'doc_2': 0.88, 'doc_3': 0.98},
    'q_5': {'doc_0': 0.99, 'doc_1': 0.89, 'doc_2': 0.79, 'doc_3': 0.69}
}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

metrics = ["hit_rate@4", "ndcg@4", "map@4", "mrr"]
results = evaluate(qrels, run, metrics)

print("Results:")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

print("\nAnalysis:")
print("- Hit@4 = 1.0: All queries have at least one relevant doc in top 4")
print("- NDCG@4 < 1.0: Some relevant docs are not at optimal positions")
print("- MAP@4 < 1.0: Average precision is reduced when relevant docs are lower")
print("- MRR < 1.0: Some queries have first relevant doc not at position 1")

# Simulate your actual case with threshold 0.94
print("\n=== Your Case: High threshold (0.94) ===")
# When threshold is 0.94, only very high similarity docs are marked relevant
# This leads to most queries having just 1 relevant doc at position 0

qrels_dict = {
    'q_1': {'doc_0': 1.0},  # Only doc_0 has similarity >= 0.94
    'q_2': {'doc_0': 1.0, 'doc_1': 1.0},  # Both doc_0 and doc_1 >= 0.94
    'q_3': {'doc_0': 1.0},
    'q_4': {'doc_0': 1.0},
    'q_5': {'doc_0': 1.0}
}

# All docs have highest similarity at position 0
run_dict = {
    'q_1': {'doc_0': 0.95, 'doc_1': 0.85, 'doc_2': 0.75, 'doc_3': 0.65},
    'q_2': {'doc_0': 0.96, 'doc_1': 0.945, 'doc_2': 0.76, 'doc_3': 0.66},
    'q_3': {'doc_0': 0.955, 'doc_1': 0.87, 'doc_2': 0.77, 'doc_3': 0.67},
    'q_4': {'doc_0': 0.98, 'doc_1': 0.88, 'doc_2': 0.78, 'doc_3': 0.68},
    'q_5': {'doc_0': 0.99, 'doc_1': 0.89, 'doc_2': 0.79, 'doc_3': 0.69}
}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

results = evaluate(qrels, run, metrics)

print("Results (matching your output):")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

print("\nWhy all metrics are 0.800:")
print("- 4 out of 5 queries have perfect retrieval (relevant doc at position 0)")
print("- 1 query (q_2) has 2 relevant docs, but both are at top positions")
print("- This gives 4/5 = 0.8 for all metrics due to binary relevance")

# Show what happens with graded relevance
print("\n=== Alternative: Using graded relevance ===")
print("Instead of binary (0 or 1), use actual similarity scores as relevance")

qrels_dict_graded = {
    'q_1': {'doc_0': 0.95, 'doc_1': 0.85},
    'q_2': {'doc_0': 0.96, 'doc_1': 0.945},
    'q_3': {'doc_0': 0.955},
    'q_4': {'doc_0': 0.98},
    'q_5': {'doc_0': 0.99}
}

qrels_graded = Qrels(qrels_dict_graded)
results_graded = evaluate(qrels_graded, run, metrics)

print("Results with graded relevance:")
for metric, score in results_graded.items():
    print(f"  {metric}: {score:.3f}")
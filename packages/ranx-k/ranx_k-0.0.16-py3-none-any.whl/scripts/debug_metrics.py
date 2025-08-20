"""Debug script to understand why all metrics return identical values."""

from ranx import Qrels, Run, evaluate
import numpy as np

# Simulate the scenario from the output
# 5 queries, with varying numbers of relevant documents
# Using binary relevance (all relevant docs have score 1.0)

# Case 1: Each query has exactly one relevant document at position 0
print("=== Case 1: One relevant doc at position 0 for each query ===")
qrels_dict = {
    'q_1': {'doc_0': 1.0},
    'q_2': {'doc_0': 1.0},
    'q_3': {'doc_0': 1.0},
    'q_4': {'doc_0': 1.0},
    'q_5': {'doc_0': 1.0}
}

run_dict = {
    'q_1': {'doc_0': 0.95, 'doc_1': 0.85, 'doc_2': 0.75, 'doc_3': 0.65},
    'q_2': {'doc_0': 0.96, 'doc_1': 0.86, 'doc_2': 0.76, 'doc_3': 0.66},
    'q_3': {'doc_0': 0.97, 'doc_1': 0.87, 'doc_2': 0.77, 'doc_3': 0.67},
    'q_4': {'doc_0': 0.98, 'doc_1': 0.88, 'doc_2': 0.78, 'doc_3': 0.68},
    'q_5': {'doc_0': 0.99, 'doc_1': 0.89, 'doc_2': 0.79, 'doc_3': 0.69}
}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

metrics = ["hit_rate@4", "ndcg@4", "map@4", "mrr"]
results = evaluate(qrels, run, metrics)

print("Results:")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

# Case 2: Based on the actual output - 6 total relevant docs across 5 queries
print("\n=== Case 2: Variable relevant docs (matching output) ===")
qrels_dict = {
    'q_1': {'doc_0': 1.0},
    'q_2': {'doc_0': 1.0, 'doc_1': 1.0},  # 2 relevant docs
    'q_3': {'doc_0': 1.0},
    'q_4': {'doc_0': 1.0},
    'q_5': {'doc_0': 1.0}
}

run_dict = {
    'q_1': {'doc_0': 0.95, 'doc_1': 0.85, 'doc_2': 0.75, 'doc_3': 0.65},
    'q_2': {'doc_0': 0.96, 'doc_1': 0.94, 'doc_2': 0.76, 'doc_3': 0.66},  # Both above threshold
    'q_3': {'doc_0': 0.97, 'doc_1': 0.87, 'doc_2': 0.77, 'doc_3': 0.67},
    'q_4': {'doc_0': 0.98, 'doc_1': 0.88, 'doc_2': 0.78, 'doc_3': 0.68},
    'q_5': {'doc_0': 0.99, 'doc_1': 0.89, 'doc_2': 0.79, 'doc_3': 0.69}
}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

results = evaluate(qrels, run, metrics)

print("Results:")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

# Case 3: When metrics would be identical
print("\n=== Case 3: Understanding when metrics are identical ===")
print("Metrics are identical when:")
print("1. Binary relevance is used (all relevant docs have score 1.0)")
print("2. Each query has at least one relevant document")
print("3. All relevant documents appear at the top positions")
print("4. The retrieval is 'perfect' within the cutoff")

# Let's verify with a perfect retrieval scenario
print("\n=== Case 4: Perfect retrieval scenario ===")
qrels_dict = {
    'q_1': {'doc_0': 1.0},
    'q_2': {'doc_0': 1.0},
    'q_3': {'doc_0': 1.0},
    'q_4': {'doc_0': 1.0},
    'q_5': {'doc_0': 1.0}
}

# All relevant docs at position 0
run_dict = {
    'q_1': {'doc_0': 1.0, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1},
    'q_2': {'doc_0': 1.0, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1},
    'q_3': {'doc_0': 1.0, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1},
    'q_4': {'doc_0': 1.0, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1},
    'q_5': {'doc_0': 1.0, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1}
}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

results = evaluate(qrels, run, metrics)

print("Results:")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

print("\nExplanation:")
print("- Hit@4 = 1.0: All queries have at least one relevant doc in top 4")
print("- NDCG@4 = 1.0: All relevant docs are at position 0 (perfect ordering)")
print("- MAP@4 = 1.0: Precision is 1.0 at the first relevant doc")
print("- MRR = 1.0: First relevant doc is always at position 1")
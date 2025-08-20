"""Test the new reference-based evaluation mode."""

from ranx import Qrels, Run, evaluate
import numpy as np

# Simulate the scenario with missing reference documents
print("=== Reference-based vs Retrieval-based Evaluation ===\n")

# Scenario: 2 reference documents, but only 1 is retrieved
print("Scenario: 2 reference documents, only 1 retrieved (similarity > 0.8)")

# Reference-based evaluation
print("\n1. Reference-based evaluation (new mode):")
qrels_ref = {
    'q_1': {
        'ref_0': 1.0,  # First reference doc
        'ref_1': 1.0   # Second reference doc
    }
}

run_ref = {
    'q_1': {
        'ref_0': 0.935,  # First reference found with high similarity
        # ref_1 not in run because similarity < 0.8
    }
}

qrels_obj = Qrels(qrels_ref)
run_obj = Run(run_ref)

metrics = ["hit_rate@3", "ndcg@3", "map@3", "mrr", "recall@3", "precision@3"]
results = evaluate(qrels_obj, run_obj, metrics)

print("Results:")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

print("\nAnalysis:")
print("- Recall@3 = 0.5 (1 out of 2 reference docs retrieved)")
print("- This correctly reflects that we missed one reference document")

# Retrieval-based evaluation (old mode)
print("\n\n2. Retrieval-based evaluation (old mode):")
qrels_ret = {
    'q_1': {
        'doc_0': 1.0  # Only the retrieved doc with high similarity
    }
}

run_ret = {
    'q_1': {
        'doc_0': 0.935  # The retrieved doc
    }
}

qrels_obj2 = Qrels(qrels_ret)
run_obj2 = Run(run_ret)

results2 = evaluate(qrels_obj2, run_obj2, metrics)

print("Results:")
for metric, score in results2.items():
    print(f"  {metric}: {score:.3f}")

print("\nAnalysis:")
print("- All metrics = 1.0 (perfect)")
print("- This misses the fact that we didn't retrieve the second reference document")

# Multiple queries example
print("\n\n=== Multiple Queries Example ===")

qrels_multi = {
    'q_1': {'ref_0': 1.0, 'ref_1': 1.0},  # 2 refs
    'q_2': {'ref_0': 1.0, 'ref_1': 1.0},  # 2 refs
    'q_3': {'ref_0': 1.0, 'ref_1': 1.0},  # 2 refs
    'q_4': {'ref_0': 1.0},                # 1 ref
    'q_5': {'ref_0': 1.0, 'ref_1': 1.0, 'ref_2': 1.0}  # 3 refs
}

run_multi = {
    'q_1': {'ref_0': 0.95, 'ref_1': 0.94},  # Both retrieved
    'q_2': {'ref_0': 0.95, 'ref_1': 0.94},  # Both retrieved
    'q_3': {'ref_0': 0.935},                # Only 1 of 2 retrieved
    'q_4': {'ref_0': 0.95},                 # All retrieved
    'q_5': {'ref_0': 0.93, 'ref_2': 0.91}   # 2 of 3 retrieved
}

qrels_obj3 = Qrels(qrels_multi)
run_obj3 = Run(run_multi)

results3 = evaluate(qrels_obj3, run_obj3, ["recall@5", "map@5", "ndcg@5"])

print("\nReference-based results:")
for metric, score in results3.items():
    print(f"  {metric}: {score:.3f}")

print("\nPer-query recall:")
print("- q_1: 2/2 = 1.00")
print("- q_2: 2/2 = 1.00")
print("- q_3: 1/2 = 0.50")
print("- q_4: 1/1 = 1.00")
print("- q_5: 2/3 = 0.67")
print(f"- Average: {(1.0 + 1.0 + 0.5 + 1.0 + 0.67)/5:.3f}")

print("\n✅ Reference-based evaluation provides more accurate assessment of retrieval completeness!")
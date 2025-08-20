"""Detailed debugging of ranx evaluation to understand identical metrics."""

from ranx import Qrels, Run, evaluate
import numpy as np

print("=== ranx가 MAP를 계산하는 방식 이해하기 ===\n")

# 실제 시나리오: 질문별로 다른 관련 문서 위치
qrels_dict = {
    'q_1': {'doc_0': 1.0, 'doc_1': 1.0, 'doc_3': 1.0},  # 위치 1,2,4
    'q_2': {'doc_0': 1.0, 'doc_1': 1.0},                # 위치 1,2
    'q_3': {'doc_0': 1.0, 'doc_1': 1.0},                # 위치 1,2
    'q_4': {'doc_0': 1.0, 'doc_1': 1.0},                # 위치 1,2
    'q_5': {'doc_0': 1.0, 'doc_2': 1.0, 'doc_4': 1.0}   # 위치 1,3,5
}

# 실제 유사도 점수 (높은 점수가 먼저 오도록)
run_dict = {
    'q_1': {'doc_3': 0.964, 'doc_0': 0.950, 'doc_1': 0.926, 'doc_4': 0.235, 'doc_2': 0.111},
    'q_2': {'doc_0': 0.951, 'doc_1': 0.935, 'doc_4': 0.130, 'doc_2': 0.125, 'doc_3': 0.090},
    'q_3': {'doc_1': 0.955, 'doc_0': 0.935, 'doc_2': 0.057, 'doc_3': 0.054, 'doc_4': 0.042},
    'q_4': {'doc_0': 0.953, 'doc_1': 0.943, 'doc_2': 0.121, 'doc_3': 0.105, 'doc_4': 0.032},
    'q_5': {'doc_2': 0.935, 'doc_0': 0.929, 'doc_4': 0.913, 'doc_3': 0.089, 'doc_1': 0.030}
}

print("문서별 실제 순위 (점수 기준):")
for q_id in qrels_dict:
    print(f"\n{q_id}:")
    sorted_docs = sorted(run_dict[q_id].items(), key=lambda x: x[1], reverse=True)
    for rank, (doc_id, score) in enumerate(sorted_docs, 1):
        is_relevant = doc_id in qrels_dict[q_id]
        print(f"  Rank {rank}: {doc_id} (score={score:.3f}) {'[RELEVANT]' if is_relevant else ''}")

# ranx 평가
qrels = Qrels(qrels_dict)
run = Run(run_dict)

metrics = ["hit_rate@5", "ndcg@5", "map@5", "mrr", "precision@1", "precision@2", "recall@5"]
results = evaluate(qrels, run, metrics)

print("\n=== ranx 평가 결과 ===")
for metric, score in results.items():
    print(f"{metric}: {score:.3f}")

# 수동 MAP 계산
print("\n=== 수동 MAP@5 계산 ===")
aps = []

for q_id in ['q_1', 'q_2', 'q_3', 'q_4', 'q_5']:
    print(f"\n{q_id}:")
    sorted_docs = sorted(run_dict[q_id].items(), key=lambda x: x[1], reverse=True)[:5]
    relevant_docs = qrels_dict[q_id]
    
    precisions = []
    relevant_found = 0
    
    for rank, (doc_id, score) in enumerate(sorted_docs, 1):
        if doc_id in relevant_docs:
            relevant_found += 1
            precision = relevant_found / rank
            precisions.append(precision)
            print(f"  Rank {rank}: {doc_id} - Precision: {precision:.3f}")
    
    # AP = sum of precisions / total relevant docs
    ap = sum(precisions) / len(relevant_docs) if precisions else 0
    aps.append(ap)
    print(f"  AP for {q_id}: {ap:.3f}")

manual_map = sum(aps) / len(aps)
print(f"\n수동 계산 MAP@5: {manual_map:.3f}")
print(f"ranx MAP@5: {results['map@5']:.3f}")

# 개별 AP 값 분석
print("\n=== 개별 Average Precision 값 ===")
for i, ap in enumerate(aps, 1):
    print(f"질문 {i}: {ap:.3f}")

print(f"\n모든 AP가 동일한가? {len(set(aps)) == 1}")
if len(set(aps)) > 1:
    print(f"고유한 AP 값: {sorted(set(aps))}")

# 왜 모든 메트릭이 0.933인지 분석
print("\n=== 0.933 값의 의미 ===")
print("만약 5개 질문 중 일부가 완벽하고 일부가 부분적이라면...")
print("예: 4개 질문이 AP=1.0, 1개 질문이 AP=0.667")
print(f"평균: (4 * 1.0 + 1 * 0.667) / 5 = {(4 * 1.0 + 1 * 0.667) / 5:.3f}")

# 실제 관련 문서 위치별 AP 계산
print("\n=== 위치별 이론적 AP 값 ===")
patterns = {
    "위치 [1,2]": [1/1, 2/2],  # AP = 1.0
    "위치 [1,3,5]": [1/1, 2/3, 3/5],  # AP = 0.756
    "위치 [1,2,4]": [1/1, 2/2, 3/4]   # AP = 0.917
}

for pattern, precisions in patterns.items():
    ap = sum(precisions) / len(precisions)
    print(f"{pattern}: precisions={precisions}, AP={ap:.3f}")
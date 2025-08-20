"""Debug recall calculation in ranx evaluation."""

from ranx import Qrels, Run, evaluate
import numpy as np

print("=== Recall 계산 문제 분석 ===\n")

# 질문 3의 상황 재현
# 참조 문서: 2개
# 검색된 문서: 3개 중 1개만 관련

print("시나리오: 참조 문서 2개, 검색된 관련 문서 1개")

# ranx 방식: 검색된 문서 기준
qrels_dict = {
    'q_1': {'doc_0': 1.0}  # 검색된 문서 중 1개만 관련
}

run_dict = {
    'q_1': {'doc_0': 0.935, 'doc_1': 0.5, 'doc_2': 0.3}
}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

metrics = ["hit_rate@3", "ndcg@3", "map@3", "mrr", "recall@3", "precision@3"]
results = evaluate(qrels, run, metrics)

print("ranx 결과 (검색된 문서 기준):")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

print("\n문제점:")
print("- ranx는 'doc_0'이 관련 있고 첫 번째 위치에 있으므로 완벽하다고 평가")
print("- 실제로는 참조 문서 2개 중 1개만 찾았으므로 recall = 0.5여야 함")

# 올바른 평가를 위한 방법
print("\n\n=== 올바른 Recall 계산 방법 ===")

# 모든 참조 문서를 qrels에 포함해야 함
qrels_dict_correct = {
    'q_1': {
        'ref_doc_0': 1.0,  # 첫 번째 참조 문서
        'ref_doc_1': 1.0   # 두 번째 참조 문서 (검색되지 않음)
    }
}

# run에는 실제 검색된 문서들
run_dict_correct = {
    'q_1': {
        'ref_doc_0': 0.935,  # 첫 번째 참조 문서는 검색됨
        # ref_doc_1은 검색되지 않았으므로 run에 없음
        'other_doc': 0.5     # 관련 없는 문서
    }
}

qrels_correct = Qrels(qrels_dict_correct)
run_correct = Run(run_dict_correct)

results_correct = evaluate(qrels_correct, run_correct, metrics)

print("올바른 ranx 결과:")
for metric, score in results_correct.items():
    print(f"  {metric}: {score:.3f}")

print("\n핵심 차이점:")
print("1. 현재 구현: 검색된 문서를 기준으로 관련성 판단")
print("2. 올바른 구현: 모든 참조 문서를 qrels에 포함")
print("3. Recall = (검색된 관련 문서 수) / (전체 참조 문서 수)")

# 실제 상황 시뮬레이션
print("\n\n=== 실제 5개 질문 시나리오 ===")

qrels_real = {
    'q_1': {'doc_0': 1.0, 'doc_1': 1.0},      # 2개 모두 검색됨
    'q_2': {'doc_0': 1.0, 'doc_1': 1.0},      # 2개 모두 검색됨
    'q_3': {'doc_0': 1.0, 'ref_missing': 1.0}, # 2개 중 1개만 검색됨
    'q_4': {'doc_0': 1.0, 'doc_1': 1.0},      # 2개 모두 검색됨
    'q_5': {'doc_0': 1.0, 'doc_1': 1.0, 'doc_2': 1.0}  # 3개 모두 검색됨
}

run_real = {
    'q_1': {'doc_0': 0.95, 'doc_1': 0.94, 'doc_2': 0.3},
    'q_2': {'doc_0': 0.95, 'doc_1': 0.94, 'doc_2': 0.3},
    'q_3': {'doc_0': 0.935, 'doc_1': 0.5, 'doc_2': 0.3},  # ref_missing은 없음
    'q_4': {'doc_0': 0.95, 'doc_1': 0.94, 'doc_2': 0.3},
    'q_5': {'doc_0': 0.95, 'doc_1': 0.94, 'doc_2': 0.93}
}

qrels_real_obj = Qrels(qrels_real)
run_real_obj = Run(run_real)

results_real = evaluate(qrels_real_obj, run_real_obj, ["recall@3", "precision@3", "map@3"])

print("참조 문서 기준 평가:")
for metric, score in results_real.items():
    print(f"  {metric}: {score:.3f}")

print("\n예상 recall@3:")
print("- q_1: 2/2 = 1.0")
print("- q_2: 2/2 = 1.0")
print("- q_3: 1/2 = 0.5")
print("- q_4: 2/2 = 1.0")
print("- q_5: 3/3 = 1.0")
print("- 평균: (1.0 + 1.0 + 0.5 + 1.0 + 1.0) / 5 = 0.9")
"""Simulate why all metrics show 0.933 in the actual output."""

from ranx import Qrels, Run, evaluate
import numpy as np

print("=== 0.933 (14/15) 점수가 나오는 시나리오 시뮬레이션 ===\n")

# 가설: 15개 질문 중 14개가 완벽한 검색 결과를 보임
# 0.933 ≈ 14/15 = 0.9333...

# 시나리오 1: 15개 질문, 14개는 완벽, 1개는 실패
print("시나리오 1: 15개 질문 중 14개 성공")
qrels_dict = {}
run_dict = {}

# 14개 질문: 완벽한 검색 (관련 문서가 첫 번째 위치)
for i in range(14):
    q_id = f'q_{i+1}'
    qrels_dict[q_id] = {'doc_0': 1.0}
    run_dict[q_id] = {'doc_0': 0.95, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1}

# 1개 질문: 관련 문서 없음
qrels_dict['q_15'] = {'doc_4': 1.0}  # doc_4는 검색되지 않음
run_dict['q_15'] = {'doc_0': 0.5, 'doc_1': 0.4, 'doc_2': 0.3, 'doc_3': 0.2}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

metrics = ["hit_rate@4", "ndcg@4", "map@4", "mrr"]
results = evaluate(qrels, run, metrics)

print("결과:")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

print(f"\n14/15 = {14/15:.3f}")

# 시나리오 2: 다른 분포로 0.933 만들기
print("\n\n시나리오 2: 다양한 성능으로 평균 0.933")
qrels_dict = {
    'q_1': {'doc_0': 1.0, 'doc_1': 1.0},  # 2개 모두 상위에
    'q_2': {'doc_0': 1.0},  # 1개 상위에
    'q_3': {'doc_0': 1.0, 'doc_2': 1.0},  # 1개는 상위, 1개는 3번째
    'q_4': {'doc_0': 1.0},  # 1개 상위에
    'q_5': {'doc_0': 1.0},  # 1개 상위에
}

run_dict = {
    'q_1': {'doc_0': 0.95, 'doc_1': 0.94, 'doc_2': 0.3, 'doc_3': 0.1},
    'q_2': {'doc_0': 0.95, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1},
    'q_3': {'doc_0': 0.95, 'doc_1': 0.5, 'doc_2': 0.94, 'doc_3': 0.1},
    'q_4': {'doc_0': 0.95, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1},
    'q_5': {'doc_0': 0.95, 'doc_1': 0.5, 'doc_2': 0.3, 'doc_3': 0.1},
}

qrels = Qrels(qrels_dict)
run = Run(run_dict)

results = evaluate(qrels, run, metrics)

print("결과:")
for metric, score in results.items():
    print(f"  {metric}: {score:.3f}")

# 실제 계산 확인
print("\n\n=== 실제 문제: 동일한 메트릭 값의 원인 ===")
print("\n가능한 원인들:")
print("1. 대부분의 질문에서 관련 문서가 최상위에 위치")
print("2. 이진 관련성 (0 또는 1) 사용")
print("3. 높은 유사도 임계값 (0.93)으로 인해 소수의 문서만 관련으로 판정")
print("4. 하이브리드 검색기가 매우 효과적으로 작동")

print("\n결론:")
print("- 모든 메트릭이 0.933 = 14/15인 것은 15개 질문 중 14개에서 완벽한 검색 수행")
print("- 이는 실제로 매우 좋은 성능!")
print("- MAP, NDCG, Hit Rate, MRR이 모두 동일한 것은 각 질문의 관련 문서가")
print("  대부분 최상위 위치에 있기 때문")

# 확률 계산
print("\n\n=== 임계값 0.94에서의 영향 ===")
print("임계값이 0.94로 매우 높으면:")
print("- 대부분의 문서가 비관련으로 분류됨")
print("- 관련 문서는 매우 높은 유사도를 가진 것들만")
print("- 이런 문서들은 대부분 상위에 랭크됨")
print("- 결과적으로 대부분의 질문에서 '완벽한' 검색 결과")
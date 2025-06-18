import math
import gmpy2

def generate_superincreasing_sequence(n, upper_data):
    """
    Generate a super-increasing sequence based on the given upper data.

    Args:
    - n: Number of DP entities that have completed identity registration.
    - upper_data: Array storing eta_i values.

    Returns:
    - superincreasing_sequence: Super-increasing sequence.
    """
    length = len(upper_data)
    condition = 0
    superincreasing_sequence = [1]  # 初始值为1
    for j in range(2, 2*length+2):
        if j <= length + 1:
            condition += superincreasing_sequence[j-2] * upper_data[j-2] * n
            alpha_j = condition + 1
            superincreasing_sequence.append(alpha_j)

        elif length+1 < j <= 2 * length +1:
            # print(j,condition,superincreasing_sequence[j - 2])
            condition += superincreasing_sequence[j - 2] * (upper_data[j - (2 + length)] ** 2) * n
            alpha_j = condition + 1
            superincreasing_sequence.append(alpha_j)

        else:
            condition = sum(superincreasing_sequence)

            alpha_j = condition + 1
            superincreasing_sequence.append(alpha_j)
    return superincreasing_sequence


def gcd(a, b):
    """计算最大公约数"""
    while b:
        a, b = b, a % b
    return a

def generate_coprime_integers(n):
    """生成 n 个互质的正整数"""
    coprime_integers = []
    num = 10000
    while len(coprime_integers) < n:
        # 判断当前数字与已选数字是否互质
        is_coprime = all(gcd(num, prev) == 1 for prev in coprime_integers)
        if is_coprime:
            coprime_integers.append(num)
        num += 1
    return coprime_integers

def generate_decision_vector_sequence(n):
    """生成决策向量序列"""
    # 选择 n 个互质的正整数
    coprime_integers = generate_coprime_integers(n)
    # 计算 A = prod(a_j)
    A = math.prod(coprime_integers)
    decision_vector = []
    for j in range(n):
        # 计算 A_j = A / a_j
        A_j = A // coprime_integers[j]
        # 计算 beta_j = A_j * (A_j^-1) mod a_j
        beta_j = A_j * gmpy2.invert(A_j, coprime_integers[j])
        # print(beta_j % coprime_integers[j])
        decision_vector.append(beta_j)
    return coprime_integers, decision_vector
"""
# 生成 superincreasing sequence 和 decision vector sequence
n = 10
upper_data = [2, 3, 4]  # 假设 upper_data 中存储了 eta_i 的值
superincreasing_sequence = generate_superincreasing_sequence(n, upper_data)
coprime_integers_sequence, decision_vector_sequence = generate_decision_vector_sequence(n)
# print(sum(decision_vector_sequence) % coprime_integers_sequence[3])
print("Superincreasing Sequence:", superincreasing_sequence)
print("Decision Vector Sequence:", decision_vector_sequence)
"""
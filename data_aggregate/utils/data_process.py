import random
import phe.paillier


def data_generate(upper_data, m):
    """
    Generate m arrays D_i as health data parameters.

    Parameters:
    upper_data (list): The upper limits for each parameter.
    m (int): The number of D_i arrays to generate.

    Returns:
    list: A list of m D_i arrays.
    """
    D_i_arrays = []
    for _ in range(m):
        D_i = [random.choices([0, random.randint(upper_data[i] * 0.9, upper_data[i])], weights=[0.1, 0.9])[0] for i in range(len(upper_data))]
        D_i.extend([D_i[i] ** 2 for i in range(len(upper_data))])  # Extend the array with squared values
        D_i_arrays.append(D_i)
    return D_i_arrays

def decision_voctor_gen(D_seq,D_i_arrays):
    voc_seq = []
    Sum = 0
    length = len(D_i_arrays[0]) // 2
    for i in range(len(D_i_arrays)):
        for j in range(length):
            if D_i_arrays[i][j] == 0:
                Sum += 0
            else:
                Sum += D_seq[j]
        voc_seq.append(Sum)
        Sum = 0
    return voc_seq

def cti_process(S_seq, D_i_arrays):
    """
    Process composite data based on S_seq and D_i_arrays.

    Parameters:
    S_seq (list): The super increasing sequence.
    D_i_arrays (list of lists): A list containing arrays D_i.

    Returns:
    list: A list of composite data.
    """
    ct_i_seq = []
    for i in range(len(D_i_arrays)):
        ct_i = sum(D_i_arrays[i][j] * S_seq[j] for j in range(len(D_i_arrays[i])))
        R_i = random.randint(0, 10000)
        ct_i += R_i * S_seq[len(S_seq)-1]
        ct_i_seq.append([ct_i, R_i])
    return ct_i_seq

def cti_separate(ct_i, S_seq):
    """
    Separate composite data based on ct_i_seq and S_seq.

    Parameters:
    ct_i_seq (list): The composite data of ct_i and R_i
    S_seq (list): A sequence of coefficients.

    Returns:
    list: A list of separated data.
    """
    result_test = []
    length = len(S_seq)
    for i in range(length):
        res = (ct_i - (ct_i% S_seq[length-i-1])) // S_seq[length-i-1]
        ct_i = ct_i - res * S_seq[length-i-1]
        result_test.append(res)
        # result_test.reverse()
        # result_test = result_test[::-1]
    return result_test



"""
# Example usage:
upper_data = [100, 200, 300]  # Example upper limits
m = 10  # Example number of arrays to generate
result = data_generate(upper_data, m)
print(result)
"""
from phe import paillier  # paillier库测试
import math
import sys
import phe.encoding
import time  # 时间开销测试
from utils import seq_get  # 超增长序列， 决策向量生成
from utils import data_process  # 实验数据模拟生成， 加密数据预处理
import web3
from solcx import set_solc_version, install_solc
from solcx import compile_source

install_solc('0.8.19')
set_solc_version('v0.8.19')
from sign_commit.ellipticcurve.ecdsa import Ecdsa
from sign_commit.ellipticcurve.privateKey import PrivateKey
from sign_commit.ellipticcurve.curve import secp256k1
from sign_commit.ellipticcurve.pedersen import Pedersen


# 编译合约
def compile_source_file(file_path):
    with open(file_path, 'r') as f:
        source = f.read()
    return compile_source(source)


# 部署合约
def deploy_contract(w3, contract_interface):
    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin'])
    accounts0 = w3.eth.accounts[0]
    transaction_hash = contract.constructor().transact({'from': accounts0})
    # 等待合约部署完成
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    # 获取部署后的合约地址
    contract_address = transaction_receipt['contractAddress']
    return contract_address


# 编译部署合约（返回调用对象）
def compile_deploy_file(w3, file_path):
    compiled_sol = compile_source_file(file_path)
    contract_id, contract_interface = compiled_sol.popitem()
    address1 = deploy_contract(w3, contract_interface)
    abi1 = contract_interface['abi']
    Contract = w3.eth.contract(address=address1, abi=abi1)
    return Contract


# 初始化web3
w3 = web3.Web3(web3.HTTPProvider('http://127.0.0.1:7545', request_kwargs={'timeout': 60 * 10}))

# 编译部署合约，获得合约对象
deployed_Contract = compile_deploy_file(w3, "ECDSA_pedersen.sol")


class ExampleEncodedNumber(phe.encoding.EncodedNumber):
    BASE = 64
    LOG2_BASE = math.log(BASE, 2)


print("默认私钥大小：", paillier.DEFAULT_KEYSIZE)  # 2048
# 生成paillier公私钥
public_key, private_key = paillier.generate_paillier_keypair()

# 设置实验参数
upper_data_sets = [[70, 100], [70, 100, 200, 50], [70, 100, 200, 50, 120, 110], [70, 100, 200, 50, 120, 110, 40, 60], [70, 100, 200, 50, 120, 110, 40, 60, 30, 60]]
participant_count = 100

DP_time_ecos = []
DP_time_ccos = []
DP_time_scos = []

for upper_data in upper_data_sets:
    print(f"Testing for upper data set: {upper_data}")
    print(f"Testing for {participant_count} participants:")

    # Generate decision vector sequence
    dim = len(upper_data)
    start_time_V_seq = time.time()
    mod_seq, D_seq = seq_get.generate_decision_vector_sequence(dim)
    end_time_V_seq = time.time()
    print(f"Time taken to generate decision vector sequence: {end_time_V_seq - start_time_V_seq} seconds")

    # Generate superincreasing sequence
    start_time_S_seq = time.time()
    S_seq = seq_get.generate_superincreasing_sequence(participant_count, upper_data)
    end_time_S_seq = time.time()
    print(f"Time taken to generate super-increasing sequence: {end_time_S_seq - start_time_S_seq} seconds")

    # Generate public and private keys for each DP
    DP_IDs = []  # 存储DP的伪身份ID
    mul_keypair = []  # DP对应的公私钥对
    for i in range(participant_count):
        # 生成公私钥对
        DP_IDs.append(f"DP{i}")
        privateKey = PrivateKey()
        publicKey = privateKey.publicKey()
        mul_keypair.append([privateKey, publicKey])

    # Data generation and preprocessing
    D_i_arrays = data_process.data_generate(upper_data, participant_count)
    start_time_decision_vector = time.time()
    Vector_seq = data_process.decision_voctor_gen(D_seq, D_i_arrays)
    ct_i_seq = data_process.cti_process(S_seq, D_i_arrays)
    end_time_decision_vector = time.time()
    print(
        f"Time taken to preprocess healthcare data for {participant_count} participants: {(end_time_decision_vector - start_time_decision_vector) / participant_count} seconds per participant")

    # Pedersen commitment
    curve = secp256k1
    H = curve.generate_random_point()
    D_i_ag = 0
    perdersen_cost = 0
    for i in range(len(ct_i_seq)):
        R_i = ct_i_seq[i][1]
        D_i = ct_i_seq[i][0] - R_i * S_seq[len(S_seq) - 1]
        D_i_ag += D_i
        start_time_pedersen = time.time()
        C = Pedersen.commit(D_i, R_i, H)
        end_time_pedersen = time.time()
        perdersen_cost += end_time_pedersen - start_time_pedersen

    print(
        f"Time taken to pedersen commitment for {participant_count} participants: {perdersen_cost / participant_count} seconds per DP")

    # Paillier encryption
    encoded_cts = [ExampleEncodedNumber.encode(public_key, m[0]) for m in ct_i_seq]
    start_time_encryption = time.time()
    encrypted_message_list = [public_key.encrypt(m) for m in encoded_cts]
    end_time_encryption = time.time()
    print(
        f"Time taken for Paillier encryption: {(end_time_encryption - start_time_encryption) / participant_count} seconds per participant")

    # Signature generation
    mul_message = []
    mul_signature = []
    public_keys = []
    sign_time = 0
    for i in range(participant_count):
        message = str(time.time()) + str(encrypted_message_list[i]) + str(Vector_seq[i])
        mul_message.append(message)
        start_time_sign = time.time()
        signature = Ecdsa.sign(message, mul_keypair[i][0])
        end_time_sign = time.time()
        sign_time += end_time_sign - start_time_sign
        mul_signature.append(signature)
        public_keys.append(mul_keypair[i][1])

    print(
        f"Time taken of sign for {participant_count} participants: {sign_time / participant_count} seconds per participant")

    # ECDSA verification
    start_time_mul_verify = time.time()
    print("The result of multiple ECDSA verifications:", Ecdsa.mul_verify(mul_message, mul_signature, public_keys))
    end_time_mul_verify = time.time()
    print(
        f"Time taken of multiple ECDSA verifications for {participant_count} participants: {end_time_mul_verify - start_time_mul_verify} seconds")

    # Paillier homomorphic encryption
    start_time_CT_aggregation = time.time()
    sum_CTi = sum(encrypted_message_list)
    end_time_CT_aggregation = time.time()
    print(
        f"Time cost of CT aggregation for {participant_count} participants: {end_time_CT_aggregation - start_time_CT_aggregation} seconds.")

    # Decrypt aggregated ciphertext
    start_time_CTAG = time.time()
    res_CTA = private_key.decrypt(sum_CTi)
    end_time_CTAG = time.time()
    print(f"Time cost of decrypt aggregated ciphertext: {end_time_CTAG - start_time_CTAG} seconds")

    R_ag = (res_CTA - (res_CTA % S_seq[len(S_seq) - 1])) // S_seq[len(S_seq) - 1]
    D_ag = res_CTA - R_ag * S_seq[len(S_seq) - 1]

    # pedersen_data = [curve.G.x, curve.G.y, H.x, H.y, R_ag, D_ag]
    # P_agg = deployed_Contract.functions.mul_pedersen(DP_IDs, pedersen_data).call({'from': w3.eth.accounts[0]})
    # print("Pedersen 聚合验证结果：", P_agg)

    Vector_all = sum(i for i in Vector_seq)
    RES = data_process.cti_separate(res_CTA, S_seq)

    avg = []
    var = []
    length_2 = len(upper_data)
    for i in range(length_2):
        avg_i = RES[(length_2 * 2) - i] // (Vector_all % mod_seq[i])
        avg.append(avg_i)
        var.append((RES[length_2 - i] // (Vector_all % mod_seq[i])) - (avg_i ** 2))

    print()
    print("Result of aggregation:")
    print("Average:", avg)
    print("Variance:", var)
    print()

print("encrypt cost: ", DP_time_ecos)
print("Commit cost ", DP_time_ccos)
print("Sign cost", DP_time_scos)

from phe import paillier  # paillier库测试
import math
import phe.encoding
import time  # 时间开销测试
from utils import seq_get # 超增长序列， 决策向量生成
from utils import data_process# 实验数据模拟生成， 加密数据预处理
import web3
from solcx import set_solc_version, install_solc
from solcx import compile_source
install_solc('0.8.19')
set_solc_version('v0.8.19')
from sign_commit.ellipticcurve.ecdsa import Ecdsa
from sign_commit.ellipticcurve.privateKey import PrivateKey
from sign_commit.ellipticcurve.curve import secp256k1
from sign_commit.ellipticcurve.math import Math
from sign_commit.ellipticcurve.pedersen import Pedersen

#编译合约
def compile_source_file(file_path):
   with open(file_path, 'r') as f:
      source = f.read()
   return compile_source(source)


#部署合约
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

#编译部署合约（返回调用对象）
def compile_deploy_file(w3, file_path):
    compiled_sol = compile_source_file(file_path)
    contract_id, contract_interface= compiled_sol.popitem()
    address1 = deploy_contract(w3, contract_interface)
    abi1 = contract_interface['abi']
    Contract = w3.eth.contract(address=address1, abi=abi1)
    return Contract

w3=web3.Web3(web3.HTTPProvider('http://127.0.0.1:7545', request_kwargs={'timeout': 60 * 10}))   #链接服务器，可以使用geth或者gnanche

#编译部署，获得合约对象
deployed_Contract=compile_deploy_file(w3,"ECDSA_pedersen.sol")   #contract_g16.sol为合约文件名称
class ExampleEncodedNumber(phe.encoding.EncodedNumber):
    BASE = 64
    LOG2_BASE = math.log(BASE, 2)

print("默认私钥大小：", paillier.DEFAULT_KEYSIZE)  # 2048
# 生成公私钥
public_key, private_key = paillier.generate_paillier_keypair()

# upper_data_sets = [[70, 100], [70, 100, 200, 50], [70, 100, 200, 50, 120, 110], [70, 100, 200, 50, 120, 110, 70, 80], [70, 100, 200, 50, 120, 110, 70, 80, 70, 90]]
upper_data = [70, 100]
participant_counts = [100, 200, 300, 400, 500]

# aggretime_FN = [0, 0, 0, 0, 0]
# BV_FN = [0, 0, 0, 0, 0]
# sign_uplord = [0, 0, 0, 0, 0]
print(f"Testing for upper data set: {upper_data}")
for n in participant_counts:
    print(f"Testing for {n} participants:")
    # start_time = time.time()

    # Generate decision vector sequence
    dim = len(upper_data)
    start_time_V_seq = time.time()
    mod_seq, D_seq = seq_get.generate_decision_vector_sequence(dim)
    end_time_V_seq = time.time()
    # print(f"Time taken to generate decision vector sequence: {end_time_V_seq - start_time_V_seq} seconds")

    # Generate superincreasing sequence
    start_time_S_seq = time.time()
    S_seq = seq_get.generate_superincreasing_sequence(n, upper_data)
    end_time_S_seq = time.time()
    # print(f"Time taken to generate super-increasing sequence: {end_time_S_seq - start_time_S_seq} seconds")

    # Generate public and private keys
    # public_key, private_key = paillier.generate_paillier_keypair()
    DP_IDs = []  # 存储DP的伪身份ID
    mul_message = []  # 存储DP的签名消息
    mul_signature = []  # 存储签名
    mul_keypair = []  # DP对应的公私钥对
    for i in range(n):
        # 生成公私钥对
        DP_IDs.append(f"DP{i}")
        privateKey = PrivateKey()
        publicKey = privateKey.publicKey()
        mul_keypair.append([privateKey, publicKey])

    # Data generation and preprocessing
    D_i_arrays = data_process.data_generate(upper_data, n)
    start_time_decision_vector = time.time()
    Vector_seq = data_process.decision_voctor_gen(D_seq, D_i_arrays)
    ct_i_seq = data_process.cti_process(S_seq, D_i_arrays, public_key)
    end_time_decision_vector = time.time()
    # print(f"Time taken to preprocess healthcare data for {n} participants: {(end_time_decision_vector - start_time_decision_vector) / n} seconds per participant")

    curve = secp256k1
    H = curve.generate_random_point()
    D_i_ag = 0
    C_mul = []
    perdersen_cost = 0
    for i in range(len(ct_i_seq)):
        R_i = ct_i_seq[i][1]
        D_i = ct_i_seq[i][0] - R_i * S_seq[len(S_seq) - 1]
        D_i_ag += D_i
        start_time_pedersen = time.time()
        C = Pedersen.commit(D_i, R_i, H)
        C_mul.append(C["commit"])
        end_time_pedersen = time.time()
        perdersen_cost += end_time_pedersen - start_time_pedersen

    # print(f"Time taken to pedersen commitment for {n} participants: {perdersen_cost / n} seconds per DP")
        data = [C["G"].x, C["G"].y, C["H"].x, C["H"].y, C["commit"].x, C["commit"].y, C["m_hash"]]
        deployed_Contract.functions.UploadUser_pedersen(DP_IDs[i], data).transact({'from': w3.eth.accounts[0]})


    # Test Paillier encryption and decryption
    encoded_cts = [ExampleEncodedNumber.encode(public_key, m[0]) for m in ct_i_seq]
    # start_time_encryption = time.time()
    encrypted_message_list = [public_key.encrypt(m) for m in encoded_cts]
    # end_time_encryption = time.time()
    # print(f"Time taken for Paillier encryption: {(end_time_encryption - start_time_encryption) / n} seconds per participant")
    # decrypted_message_list = [private_key.decrypt_encoded(c, ExampleEncodedNumber) for c in encrypted_message_list]

    # start_time_CT_aggregation = time.time()
    sum_CTi = sum(encrypted_message_list)
    Vector_all = sum(i for i in Vector_seq)
    # print("type of encode data", type(sum_CTi))
    # end_time_CT_aggregation = time.time()
    # print(f"Time cost of CT aggregation for {n} participants: {end_time_CT_aggregation - start_time_CT_aggregation} seconds.")
    # homomorphism_result = private_key.decrypt(sum_CTi) == sum(m.decode() for m in decrypted_message_list)
    # print("Homomorphism of Paillier:", homomorphism_result)
    fn_privateKey = PrivateKey()
    fn_publicKey = fn_privateKey.publicKey()

    start_time_sign = time.time()
    message = str(time.time()) + str(sum_CTi) + str(Vector_all[i])
    signature = Ecdsa.sign(message, fn_privateKey)
    data = [signature.s, signature.r.x, signature.r.y, signature.m_hash, fn_publicKey.point.x, fn_publicKey.point.y, fn_publicKey.curve.N]
    deployed_Contract.functions.UploadUser_ECDSA("FN", data).transact({'from': w3.eth.accounts[0]})
    gas_estimate_ecdsa = deployed_Contract.functions.verify_ECDSA("FN").estimate_gas({'from': w3.eth.accounts[0]})
    print("The gas cost of verify FN's mes:", gas_estimate_ecdsa)
    end_time_sign = time.time()
    # print("Time Taken of FN for sign and uplord:", end_time_sign - start_time_sign)

    # Data separation
    start_time_CTAG = time.time()
    res_CTA = private_key.decrypt(sum_CTi)
    end_time_CTAG = time.time()
    # print(f"Time cost of decrypt aggregated ciphertext: {end_time_CTAG - start_time_CTAG} seconds")

    R_ag = (res_CTA - (res_CTA % S_seq[len(S_seq) - 1])) // S_seq[len(S_seq) - 1]
    # R_ag2 = sum(ct_i_seq[i][1] for i in range(len(ct_i_seq)))
    # print(R_ag == R_ag2)
    D_ag = res_CTA - R_ag * S_seq[len(S_seq) - 1]
    # print(D_ag == D_i_ag)

    pedersen_data = [curve.G.x, curve.G.y, H.x, H.y, R_ag, D_ag]
    aggregated_C = Pedersen.commit_agg(C_mul)
    commit_verify_cost = deployed_Contract.functions.mulverify_pedersen(aggregated_C.x, pedersen_data).estimate_gas({'from': w3.eth.accounts[0]})
    print("Gas cost of perdersen mul_verify：", commit_verify_cost)





#print(BV_FN)
#print(aggretime_FN)
#print(sign_uplord)







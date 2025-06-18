import web3
from solcx import set_solc_version, install_solc
from solcx import compile_source
install_solc('0.8.19')
set_solc_version('v0.8.19')
import json,base64
from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.curve import secp256k1
from ellipticcurve.math import Math
from ellipticcurve.pedersen import Pedersen

     
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

#与服务器连接
w3=web3.Web3(web3.HTTPProvider('http://127.0.0.1:7545', request_kwargs={'timeout': 60 * 10}))   #链接服务器，可以使用geth或者gnanche

#编译部署，获得合约对象
deployed_Contract=compile_deploy_file(w3,"ECDSA_pedersen.sol")   #contract_g16.sol为合约文件名称

#生成公私钥对
privateKey = PrivateKey()
publicKey = privateKey.publicKey()
#消息
message = "My test message1"
#签名
signature = Ecdsa.sign(message, privateKey)
data = [signature.s, signature.r.x, signature.r.y, signature.m_hash, publicKey.point.x, publicKey.point.y, publicKey.curve.N]
"上传ECDSA"
deployed_Contract.functions.UploadUser_ECDSA("a",data).transact({'from':w3.eth.accounts[0]})
"验证ECDSA"
result = deployed_Contract.functions.verify_ECDSA("a").call({'from':w3.eth.accounts[0]})
gas_estimate_ecdsa = deployed_Contract.functions.verify_ECDSA("a").estimate_gas({'from': w3.eth.accounts[0]})
print("单项ECDSA链上验证的结果是：",result)
print("单项 ECDSA 操作所消耗的 gas 值是：", gas_estimate_ecdsa)

n=4 #用户数量
user=[]
for i in range(n):
    #生成公私钥对
    privateKey = PrivateKey()
    publicKey = privateKey.publicKey()
    #消息
    # 消息替换为hash(CTi||MΩi ||Ti)
    message = "My test message1"
    #签名
    signature = Ecdsa.sign(message, privateKey)
    data = [signature.s, signature.r.x, signature.r.y, signature.m_hash, publicKey.point.x, publicKey.point.y, publicKey.curve.N]
    deployed_Contract.functions.UploadUser_ECDSA(str(i),data).transact({'from':w3.eth.accounts[0]})
    user.append(str(i))
#多项验证
result1 = deployed_Contract.functions.mul_verify_ECDSA(user).call({'from':w3.eth.accounts[0]})
gas_estimate_mulverify = deployed_Contract.functions.mul_verify_ECDSA(user).estimate_gas({'from': w3.eth.accounts[0]})
print("多项ECDSA链上验证的结果为：",result1, gas_estimate_mulverify)

#pedersen
curve = secp256k1
H = curve.generate_random_point()
#message = "My test message1"
C = Pedersen.commit(100, 50, H)
data = [C["G"].x, C["G"].y, C["H"].x, C["H"].y, C["commit"].x, C["commit"].y,C["m_hash"]]
deployed_Contract.functions.UploadUser_pedersen("a",data).transact({'from':w3.eth.accounts[0]})

C2 = Pedersen.commit(100, 50, H)
data2 = [C2["G"].x, C2["G"].y, C2["H"].x, C2["H"].y, C2["commit"].x, C2["commit"].y,C2["m_hash"]]
deployed_Contract.functions.UploadUser_pedersen("b",data2).transact({'from':w3.eth.accounts[0]})

user_list = ["a", "b"]
pedersen_data = [curve.G.x, curve.G.y, H.x, H.y, 100, 200]
P_agg = deployed_Contract.functions.mul_pedersen(user_list, pedersen_data).call({'from':w3.eth.accounts[0]})
# print(P_agg)
# mulp_result = deployed_Contract.functions.mulverify_pedersen(P_agg, curve.G, H, 50, 100).transact({'from':w3.eth.accounts[0]})
print("Pedersen 聚合验证结果：", P_agg)
"验证ECDSA"
gas_estimate_pedersen = deployed_Contract.functions.verify_pedersen("a", C["r"]).estimate_gas({'from': w3.eth.accounts[0]})
P_result = deployed_Contract.functions.verify_pedersen("a", C["r"]).call({'from':w3.eth.accounts[0]})
print("pedersen的链上验证结果为：", P_result)
print("Pedersen 操作所消耗的 gas 值是：", gas_estimate_pedersen)
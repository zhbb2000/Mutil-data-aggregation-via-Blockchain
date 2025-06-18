from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.curve import secp256k1
from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.math import Math
from ellipticcurve.pedersen import Pedersen
#生成公私钥对
privateKey = PrivateKey()
publicKey = privateKey.publicKey()
#消息
message = "My test message1"
#签名
signature = Ecdsa.sign(message, privateKey)
#单项验证
print("单项ECDSA验证的结果为：",Ecdsa.verify(message, signature, publicKey))
curve = secp256k1
H = curve.generate_random_point()
Commit1 = Pedersen.commit(100, 50, H)
Commit2 = Pedersen.commit(10, 20, H)
Commit3 = Pedersen.commit(90, 30, H)
commits = [Commit1["commit"], Commit2["commit"], Commit3["commit"]]
Commit = Pedersen.commit_agg(commits)
P_result = Pedersen.verify(200, Commit, 100, H)
print("pederson聚合验证的结果为：",P_result)

mul_message = []
mul_signature = []
mul_publicKey = []
n=4 #用户数量
for i in range(n):
    #生成公私钥对
    privateKey = PrivateKey()
    publicKey = privateKey.publicKey()
    mul_publicKey.append(publicKey)
    #消息
    message = "My test message1"
    mul_message.append(message)
    #签名
    signature = Ecdsa.sign(message, privateKey)
    mul_signature.append(signature)
#多项验证
print("多项ECDSA验证的结果为：",Ecdsa.mul_verify(mul_message, mul_signature, mul_publicKey))


from hashlib import sha256
from .signature import Signature
from .math import Math
from .utils.integer import RandomInteger
from .utils.binary import numberFromByteString
from .utils.compatibility import *
from .point import Point

class Ecdsa:

    @classmethod
    def sign(cls, message, privateKey, hashfunc=sha256):
        byteMessage = hashfunc(toBytes(message)).digest()
        numberMessage = numberFromByteString(byteMessage)
        curve = privateKey.curve

        r, s, randSignPoint = 0, 0, None
        while r == 0 or s == 0:
            randNum = RandomInteger.between(1, curve.N - 1)
            randSignPoint = Math.multiply(curve.G, n=randNum, A=curve.A, P=curve.P, N=curve.N)
            point_r = randSignPoint
            r = point_r.x % curve.N
            s = ((numberMessage + r * privateKey.secret) * (Math.inv(randNum, curve.N))) % curve.N
        recoveryId = randSignPoint.y & 1
        if randSignPoint.y > curve.N:
            recoveryId += 2

        return Signature(r=point_r, s=s, m_hash=numberMessage, recoveryId=recoveryId)
    #单项验证
    @classmethod
    def verify(cls, message, signature, publicKey, hashfunc=sha256):
        byteMessage = hashfunc(toBytes(message)).digest()
        numberMessage = numberFromByteString(byteMessage)
        curve = publicKey.curve
        r = signature.r.x % curve.N
        s = signature.s
        if not 1 <= r <= curve.N - 1:
            return False
        if not 1 <= s <= curve.N - 1:
            return False
        inv = Math.inv(s, curve.N)
        u1 = Math.multiply(curve.G, n=(numberMessage * inv) % curve.N, N=curve.N, A=curve.A, P=curve.P)
        u2 = Math.multiply(publicKey.point, n=(r * inv) % curve.N, N=curve.N, A=curve.A, P=curve.P)
        v = Math.add(u1, u2, A=curve.A, P=curve.P)
        if v.isAtInfinity():
            return False
        return v.x % curve.N == r

    #批量验证
    @classmethod
    def mul_verify(cls, mul_message: list, mul_signature: list, mul_publicKey: list, hashfunc=sha256):
        if len(mul_message) == len(mul_signature)== len(mul_publicKey):
            amount=len(mul_message)
            a = Point(0, 0)
            b = Point(0, 0) 
            for n in range(amount):
                byteMessage = hashfunc(toBytes(mul_message[n])).digest()
                numberMessage = numberFromByteString(byteMessage)
                curve = mul_publicKey[n].curve
                point_r = mul_signature[n].r   
                a = Math.add(a, point_r, A=curve.A, P=curve.P)
                r = point_r.x                           
                s = mul_signature[n].s
                if not 1 <= r <= curve.N - 1:
                    return False
                if not 1 <= s <= curve.N - 1:
                    return False
                inv = Math.inv(s, curve.N)
                u1 = Math.multiply(curve.G, n=(numberMessage * inv) % curve.N, N=curve.N, A=curve.A, P=curve.P)
                u2 = Math.multiply(mul_publicKey[n].point, n=(r * inv) % curve.N, N=curve.N, A=curve.A, P=curve.P)
                v = Math.add(u1, u2, A=curve.A, P=curve.P) 
                b = Math.add(b, v, A=curve.A, P=curve.P) 
            if b.isAtInfinity():
                return False
            return b.x % curve.N == a.x % curve.N
        else:
            return False

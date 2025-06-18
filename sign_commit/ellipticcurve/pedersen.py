from .curve import secp256k1
from hashlib import sha256
from .math import Math
from .utils.integer import RandomInteger
from .utils.binary import numberFromByteString
from .utils.compatibility import *


class Pedersen:

    @classmethod
    def commit(cls, message, r, H, hashfunc=sha256):
        # byteMessage = hashfunc(toBytes(message)).digest()
        # m_hash = numberFromByteString(byteMessage)
        curve = secp256k1
        # H = curve.generate_random_point()
        # r = RandomInteger.between(1, curve.N - 1)
        u1 = Math.multiply(curve.G, r, A=curve.A, P=curve.P, N=curve.N)
        u2 = Math.multiply(H, message, A=curve.A, P=curve.P, N=curve.N)
        Commit = Math.add(u1, u2 , A=curve.A, P=curve.P)
        return {"commit": Commit, "m_hash": message,"r": r,"H": H,"G": curve.G}

    @classmethod
    def commit_agg(cls, Commits):
        curve = secp256k1
        add_commit = Math.add(Commits[0], Commits[1], A=curve.A, P=curve.P)
        for i in range(len(Commits)-2):
            add_commit = Math.add(add_commit, Commits[i+2], A=curve.A, P=curve.P)
        return add_commit


    @classmethod
    def verify(cls, message, Commit, r, H, hashfunc=sha256):
        # byteMessage = hashfunc(toBytes(message)).digest()
        # m_hash = numberFromByteString(byteMessage)
        curve = secp256k1
        u1 = Math.multiply(curve.G, r, A=curve.A, P=curve.P, N=curve.N)
        u2 = Math.multiply(H, message, A=curve.A, P=curve.P, N=curve.N)
        Commit1 = Math.add(u1, u2 , A=curve.A, P=curve.P)
        if Commit1.isAtInfinity():
            return False
        if Commit.x % curve.N == Commit1.x % curve.N:
            return True
        else:
            return False
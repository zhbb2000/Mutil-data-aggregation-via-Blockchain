from .point import Point


class Math:

    @classmethod
    def modularSquareRoot(cls, value, prime):
        return pow(value, (prime + 1) // 4, prime)

    @classmethod
    def multiply(cls, p, n, N, A, P):
        """
        快速乘法：用于椭圆曲线上点与标量的乘法
        
        :param p: 要乘的第一个点
        :param n: 要乘的标量
        :param N: 椭圆曲线的阶
        :param P: 方程Y^2 = X^3 + A*X + B (mod p)中的质数模
        :param A: 方程Y^2 = X^3 + A*X + B (mod p)中一次项的系数
        :return: 表示第一和第二点和的点
        """
        return cls._fromJacobian(
            cls._jacobianMultiply(cls._toJacobian(p), n, N, A, P), P
        )
    @classmethod
    def __neg__(cls, p, P):
        # 对于secp256k1，相反点是(x, -y mod p)
        # 确保使用曲线的p值进行模运算
        return Point(p.x, -p.y % P)
    
    @classmethod
    def add(cls, p, q, A, P):
        """
        快速加法：用于椭圆曲线上两点的相加
        
        :param p: 想要相加的第一个点
        :param q: 想要相加的第二个点
        :param P: 方程Y^2 = X^3 + A*X + B (mod p)中的质数模
        :param A: 方程Y^2 = X^3 + A*X + B (mod p)中一次项的系数
        :return: 表示第一和第二点和的点
        """
        return cls._fromJacobian(
            cls._jacobianAdd(cls._toJacobian(p), cls._toJacobian(q), A, P), P,
        )

    @classmethod
    def inv(cls, x, n):
        """
        扩展欧几里得算法。它是椭圆曲线上的‘除法’
        
        :param x: 除数
        :param n: 除法的模
        :return: 表示除法结果的值
        """
        if x == 0:
            return 0

        lm = 1
        hm = 0
        low = x % n
        high = n

        while low > 1:
            r = high // low
            nm = hm - lm * r
            nw = high - low * r
            high = low
            hm = lm
            low = nw
            lm = nm

        return lm % n

    @classmethod
    def _toJacobian(cls, p):
        """
        将点转换为雅可比坐标
        
        :param p: 想要加的第一个点
        :return: 雅可比坐标中的点
        """
        return Point(p.x, p.y, 1)

    @classmethod
    def _fromJacobian(cls, p, P):
        """
        从雅可比坐标转换点回来
        
        :param p: 雅可比坐标中的点
        :param P: 方程Y^2 = X^3 + A*X + B (mod p)中的质数模
        :return: 默认坐标中的点
        """
        z = cls.inv(p.z, P)
        x = (p.x * z ** 2) % P
        y = (p.y * z ** 3) % P

        return Point(x, y, 0)

    @classmethod
    def _jacobianDouble(cls, p, A, P):
        """
        在椭圆曲线上加倍一个点
        
        :param p: 想要加倍的点
        :param P: 方程Y^2 = X^3 + A*X + B (mod p)中的质数模
        :param A: 方程Y^2 = X^3 + A*X + B (mod p)中一次项的系数
        :return: 表示加倍后的点
        """
        if p.y == 0:
            return Point(0, 0, 0)

        ysq = (p.y ** 2) % P
        S = (4 * p.x * ysq) % P
        M = (3 * p.x ** 2 + A * p.z ** 4) % P
        nx = (M**2 - 2 * S) % P
        ny = (M * (S - nx) - 8 * ysq ** 2) % P
        nz = (2 * p.y * p.z) % P

        return Point(nx, ny, nz)

    @classmethod
    def _jacobianAdd(cls, p, q, A, P):
        """
        在椭圆曲线上加两个点
        
        :param p: 想要相加的第一个点
        :param q: 想要相加的第二个点
        :param P: 方程Y^2 = X^3 + A*X + B (mod p)中的质数模
        :param A: 方程Y^2 = X^3 + A*X + B (mod p)中一次项的系数
        :return: 表示两点和的点
        """
        if p.y == 0:
            return q
        if q.y == 0:
            return p

        U1 = (p.x * q.z ** 2) % P
        U2 = (q.x * p.z ** 2) % P
        S1 = (p.y * q.z ** 3) % P
        S2 = (q.y * p.z ** 3) % P

        if U1 == U2:
            if S1 != S2:
                return Point(0, 0, 1)
            return cls._jacobianDouble(p, A, P)

        H = U2 - U1
        R = S2 - S1
        H2 = (H * H) % P
        H3 = (H * H2) % P
        U1H2 = (U1 * H2) % P
        nx = (R ** 2 - H3 - 2 * U1H2) % P
        ny = (R * (U1H2 - nx) - S1 * H3) % P
        nz = (H * p.z * q.z) % P

        return Point(nx, ny, nz)

    @classmethod
    def _jacobianMultiply(cls, p, n, N, A, P):
        """
        在椭圆曲线上将点和标量进行乘法运算

        :param p: 要相乘的第一个点
        :param n: 要相乘的标量
        :param N: 椭圆曲线的阶
        :param P: 方程Y^2 = X^3 + A*X + B (mod p)中模数的质数
        :param A: 方程Y^2 = X^3 + A*X + B (mod p)中一次项的系数
        :return: 表示第一点和第二点之和的点
        """
        if p.y == 0 or n == 0:
            return Point(0, 0, 1)   # 如果点的y坐标为0或标量n为0，则返回无穷远点

        if n == 1:
            return p    # 如果标量n为1，直接返回原点

        if n < 0 or n >= N:
            return cls._jacobianMultiply(p, n % N, N, A, P) # 如果n为负数或大于等于N，进行模N运算后递归调用

        if (n % 2) == 0:
            # 如果n是偶数，首先将n除以2，对结果递归调用_jacobianMultiply得到点，然后对该点进行加倍
            return cls._jacobianDouble(
                cls._jacobianMultiply(p, n // 2, N, A, P), A, P 
            )
# 如果n是奇数，首先将n除以2向下取整，对结果递归调用_jacobianMultiply并加倍，然后将结果与原点相加
        return cls._jacobianAdd(
            cls._jacobianDouble(cls._jacobianMultiply(p, n // 2, N, A, P), A, P), p, A, P
        )

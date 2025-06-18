// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract ECDSA_pedersen{
    //点
    struct point{
        uint256 x;
        uint256 y;
    }
    //ECDSA每个用户存储的结构体
    struct user_ECDSA{
        uint256 s;
        point r;
        uint256 m_hash; 
        point pk;
        uint256 p;
    }
    //pedersen每个用户存储的结构体
    struct user_pedersen{
        point G;
        point H;
        point C;
        uint256 m_hash; 
    }
    //存储多个用户的ECDSA
    mapping (string => user_ECDSA) public User_ECDSA;
    //存储多个用户的pedersen
    mapping (string => user_pedersen) public User_pedersen;
    //根据ID存储ECDSA
    function UploadUser_ECDSA(string memory ID, uint256[7] memory ECDSA_data)  public returns (bool) {
        point memory R = point(ECDSA_data[1], ECDSA_data[2]);
        point memory PK = point(ECDSA_data[4], ECDSA_data[5]);        
        user_ECDSA memory C = user_ECDSA(ECDSA_data[0], R, ECDSA_data[3], PK, ECDSA_data[6]);
        User_ECDSA[ID] = C;      
        return true;
    }
    //单个验证
    function verify_ECDSA(string memory ID) view public returns (bool) {
        user_ECDSA memory U = User_ECDSA[ID];
        //求逆元
        uint256 inv_s = InvMod(U.s,U.p);
        uint256 u1 = mulmod(U.m_hash, inv_s, U.p);
        uint256 v1 = mulmod(U.r.x, inv_s, U.p);
        (uint256 x1,uint256 y1) = DerivePubKey(u1);        
        (uint256 x2,uint256 y2) = Mul(U.pk.x, U.pk.y, v1);
        (uint256 x3,) = Add(x1,y1,x2,y2);
        if (x3 == U.r.x) {
            return true;
        } else {
            return false;
        }
    }  
    //批量验证
    function mul_verify_ECDSA(string[] memory All_ID) view public returns (bool) {
        point memory Q;
        point memory W;
        uint256[6] memory E;
        for (uint i = 0; i < All_ID.length; i++) {
            string memory ID = All_ID[i];
            user_ECDSA memory U = User_ECDSA[ID];
            uint256 inv_s = InvMod(U.s,U.p);
            uint256 u1 = mulmod(U.m_hash, inv_s, U.p);
            uint256 v1 = mulmod(U.r.x, inv_s, U.p);
            (E[0],E[1]) = DerivePubKey(u1);        
            (E[2],E[3]) = Mul(U.pk.x, U.pk.y, v1);
            (E[4],E[5]) = Add(E[0],E[1],E[2],E[3]);
            (Q.x, Q.y) = Add(E[4],E[5], Q.x,Q.y);
            (W.x, W.y) = Add(U.r.x, U.r.y, W.x, W.y);            
        }    
        if (Q.x == W.x) {
            return true;
        } else {
            return false;
        }
    }  
    //根据ID存储pederesen
    function UploadUser_pedersen(string memory ID, uint256[7] memory pederson_data)  public returns (bool) {
        point memory G = point(pederson_data[0], pederson_data[1]);
        point memory H = point(pederson_data[2], pederson_data[3]);    
        point memory C = point(pederson_data[4], pederson_data[5]);       
        user_pedersen memory Commit = user_pedersen(G, H, C, pederson_data[6]);
        User_pedersen[ID] = Commit;      
        return true;
    }

    // pedersen commitment aggregation
    function mul_pedersen(string[] memory All_ID, uint256[6] memory pederson_data) public returns (bool) {
    point memory C_ag;
    for (uint i = 0; i < All_ID.length; i++) {
        string memory ID = All_ID[i];
        user_pedersen memory U = User_pedersen[ID];
        (C_ag.x, C_ag.y) = Add(U.C.x, U.C.y, C_ag.x, C_ag.y);
    }
    bool result_ag = mulverify_pedersen(C_ag.x, pederson_data);
    return result_ag;
}

    function mulverify_pedersen(uint256 C_ag, uint256[6] memory pederson_data) view public returns (bool) {
        uint256[6] memory E;
        (E[0], E[1]) = Mul(pederson_data[0], pederson_data[1], pederson_data[4]);
        (E[2], E[3]) = Mul(pederson_data[2], pederson_data[3], pederson_data[5]);
        (E[4], E[5]) = Add(E[0], E[1], E[2], E[3]);
        if (C_ag == E[4]) {
            return true;
    }
        else {
            return false;
    }
}
    //验证pesersen  
    function verify_pedersen(string memory ID, uint256 r) view public returns (bool) {
        user_pedersen memory U = User_pedersen[ID];
        uint256[6] memory E;              
        (E[0],E[1]) = Mul(U.G.x, U.G.y, r);
        (E[2],E[3]) = Mul(U.H.x, U.H.y, U.m_hash);
        (E[4],E[5]) = Add(E[0],E[1],E[2],E[3]); 
        if (U.C.x == E[4]) {
            return true;
        } else {
            return false;
        }

    }            
    uint256 public constant GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
    uint256 public constant GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
    uint256 public constant AA = 0;
    uint256 public constant BB = 7;
    uint256 public constant PP = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;

    // (求数的逆元)计算模p的val逆元
    function InvMod(uint256 val, uint256 p) pure public returns (uint256)
    {
        return invMod(val,p);
    }
    // （求数的幂）计算模p下val的e次幂
    function ExpMod(uint256 val, uint256 e, uint256 p) pure public returns (uint256)
    {
        return expMod(val,e,p);
    }
    // （求）根据给定的x坐标和前缀，推导出y坐标
    function GetY(uint8 prefix, uint256 x) pure public returns (uint256)
    {
        return deriveY(prefix,x,AA,BB,PP);
    }
    // 判断给定的点(x, y)是否在椭圆曲线上
    function OnCurve(uint256 x, uint256 y) pure public returns (bool)
    {
        return isOnCurve(x,y,AA,BB,PP);
    }
    // 计算给定点(x, y)的逆点
    // 在椭圆曲线加法中，点的逆是其关于x轴的对称点
    function Inverse(uint256 x, uint256 y) pure public returns (uint256, 
    uint256) {
        return ecInv(x,y,PP);
    }
    // 计算两个椭圆曲线上的点的差（即一个点加上另一个点的逆）
    function Subtract(uint256 x1, uint256 y1,uint256 x2, uint256 y2 ) pure public returns (uint256, uint256) {
        return ecSub(x1,y1,x2,y2,AA,PP);
    }
    // 计算两个椭圆曲线上的点的和
    function Add(uint256 x1, uint256 y1,uint256 x2, uint256 y2 ) pure public returns (uint256, uint256) {
        return ecAdd(x1,y1,x2,y2,AA,PP);
    }
    //计算k*(x1,y1)
    function Mul(uint256 x1, uint256 y1,uint256 k) pure public returns (uint256, uint256) {
        return ecMul(k,x1,y1,AA,PP);
    }
    // 根据给定的私钥计算出相应的公钥
    // 这里的公钥是椭圆曲线上的一个点(x, y)
    function DerivePubKey(uint256 privKey) pure public returns (uint256, uint256) {
        return ecMul(privKey,GX,GY,AA,PP);
    }


    // Pre-computed constant for 2 ** 255
    uint256 constant private U255_MAX_PLUS_1 = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

    /// @dev Modular euclidean inverse of a number (mod p).
    /// @param _x The number
    /// @param _pp The modulus
    /// @return q such that x*q = 1 (mod _pp)
    function invMod(uint256 _x, uint256 _pp) internal pure returns (uint256) {
        require(_x != 0 && _x != _pp && _pp != 0, "Invalid number");
        uint256 q = 0;
        uint256 newT = 1;
        uint256 r = _pp;
        uint256 t;
        while (_x != 0) {
        t = r / _x;
        (q, newT) = (newT, addmod(q, (_pp - mulmod(t, newT, _pp)), _pp));
        (r, _x) = (_x, r - t * _x);
        }

        return q;
    }

    /// @dev Modular exponentiation, b^e % _pp.
    /// Source: https://github.com/androlo/standard-contracts/blob/master/contracts/src/crypto/ECCMath.sol
    /// @param _base base
    /// @param _exp exponent
    /// @param _pp modulus
    /// @return r such that r = b**e (mod _pp)
    function expMod(uint256 _base, uint256 _exp, uint256 _pp) internal pure returns (uint256) {
        require(_pp!=0, "Modulus is zero");

        if (_base == 0)
        return 0;
        if (_exp == 0)
        return 1;

        uint256 r = 1;
        uint256 bit = U255_MAX_PLUS_1;
        assembly {
        for { } gt(bit, 0) { }{
            r := mulmod(mulmod(r, r, _pp), exp(_base, iszero(iszero(and(_exp, bit)))), _pp)
            r := mulmod(mulmod(r, r, _pp), exp(_base, iszero(iszero(and(_exp, div(bit, 2))))), _pp)
            r := mulmod(mulmod(r, r, _pp), exp(_base, iszero(iszero(and(_exp, div(bit, 4))))), _pp)
            r := mulmod(mulmod(r, r, _pp), exp(_base, iszero(iszero(and(_exp, div(bit, 8))))), _pp)
            bit := div(bit, 16)
        }
        }

        return r;
    }

    /// @dev Converts a point (x, y, z) expressed in Jacobian coordinates to affine coordinates (x', y', 1).
    /// @param _x coordinate x
    /// @param _y coordinate y
    /// @param _z coordinate z
    /// @param _pp the modulus
    /// @return (x', y') affine coordinates
    function toAffine(
        uint256 _x,
        uint256 _y,
        uint256 _z,
        uint256 _pp)
    internal pure returns (uint256, uint256)
    {
        uint256 zInv = invMod(_z, _pp);
        uint256 zInv2 = mulmod(zInv, zInv, _pp);
        uint256 x2 = mulmod(_x, zInv2, _pp);
        uint256 y2 = mulmod(_y, mulmod(zInv, zInv2, _pp), _pp);

        return (x2, y2);
    }

    /// @dev Derives the y coordinate from a compressed-format point x [[SEC-1]](https://www.secg.org/SEC1-Ver-1.0.pdf).
    /// @param _prefix parity byte (0x02 even, 0x03 odd)
    /// @param _x coordinate x
    /// @param _aa constant of curve
    /// @param _bb constant of curve
    /// @param _pp the modulus
    /// @return y coordinate y
    function deriveY(
        uint8 _prefix,
        uint256 _x,
        uint256 _aa,
        uint256 _bb,
        uint256 _pp)
    internal pure returns (uint256)
    {
        require(_prefix == 0x02 || _prefix == 0x03, "Invalid compressed EC point prefix");

        // x^3 + ax + b
        uint256 y2 = addmod(mulmod(_x, mulmod(_x, _x, _pp), _pp), addmod(mulmod(_x, _aa, _pp), _bb, _pp), _pp);
        y2 = expMod(y2, (_pp + 1) / 4, _pp);
        // uint256 cmp = yBit ^ y_ & 1;
        uint256 y = (y2 + _prefix) % 2 == 0 ? y2 : _pp - y2;

        return y;
    }

    /// @dev Check whether point (x,y) is on curve defined by a, b, and _pp.
    /// @param _x coordinate x of P1
    /// @param _y coordinate y of P1
    /// @param _aa constant of curve
    /// @param _bb constant of curve
    /// @param _pp the modulus
    /// @return true if x,y in the curve, false else
    function isOnCurve(
        uint _x,
        uint _y,
        uint _aa,
        uint _bb,
        uint _pp)
    internal pure returns (bool)
    {
        if (0 == _x || _x >= _pp || 0 == _y || _y >= _pp) {
        return false;
        }
        // y^2
        uint lhs = mulmod(_y, _y, _pp);
        // x^3
        uint rhs = mulmod(mulmod(_x, _x, _pp), _x, _pp);
        if (_aa != 0) {
        // x^3 + a*x
        rhs = addmod(rhs, mulmod(_x, _aa, _pp), _pp);
        }
        if (_bb != 0) {
        // x^3 + a*x + b
        rhs = addmod(rhs, _bb, _pp);
        }

        return lhs == rhs;
    }

    /// @dev Calculate inverse (x, -y) of point (x, y).
    /// @param _x coordinate x of P1
    /// @param _y coordinate y of P1
    /// @param _pp the modulus
    /// @return (x, -y)
    function ecInv(
        uint256 _x,
        uint256 _y,
        uint256 _pp)
    internal pure returns (uint256, uint256)
    {
        return (_x, (_pp - _y) % _pp);
    }

    /// @dev Add two points (x1, y1) and (x2, y2) in affine coordinates.
    /// @param _x1 coordinate x of P1
    /// @param _y1 coordinate y of P1
    /// @param _x2 coordinate x of P2
    /// @param _y2 coordinate y of P2
    /// @param _aa constant of the curve
    /// @param _pp the modulus
    /// @return (qx, qy) = P1+P2 in affine coordinates
    function ecAdd(
        uint256 _x1,
        uint256 _y1,
        uint256 _x2,
        uint256 _y2,
        uint256 _aa,
        uint256 _pp)
        internal pure returns(uint256, uint256)
    {
        uint x = 0;
        uint y = 0;
        uint z = 0;

        // Double if x1==x2 else add
        if (_x1==_x2) {
        // y1 = -y2 mod p
        if (addmod(_y1, _y2, _pp) == 0) {
            return(0, 0);
        } else {
            // P1 = P2
            (x, y, z) = jacDouble(
            _x1,
            _y1,
            1,
            _aa,
            _pp);
        }
        } else {
        (x, y, z) = jacAdd(
            _x1,
            _y1,
            1,
            _x2,
            _y2,
            1,
            _pp);
        }
        // Get back to affine
        return toAffine(
        x,
        y,
        z,
        _pp);
    }

    /// @dev Substract two points (x1, y1) and (x2, y2) in affine coordinates.
    /// @param _x1 coordinate x of P1
    /// @param _y1 coordinate y of P1
    /// @param _x2 coordinate x of P2
    /// @param _y2 coordinate y of P2
    /// @param _aa constant of the curve
    /// @param _pp the modulus
    /// @return (qx, qy) = P1-P2 in affine coordinates
    function ecSub(
        uint256 _x1,
        uint256 _y1,
        uint256 _x2,
        uint256 _y2,
        uint256 _aa,
        uint256 _pp)
    internal pure returns(uint256, uint256)
    {
        // invert square
        (uint256 x, uint256 y) = ecInv(_x2, _y2, _pp);
        // P1-square
        return ecAdd(
        _x1,
        _y1,
        x,
        y,
        _aa,
        _pp);
    }

    /// @dev Multiply point (x1, y1, z1) times d in affine coordinates.
    /// @param _k scalar to multiply
    /// @param _x coordinate x of P1
    /// @param _y coordinate y of P1
    /// @param _aa constant of the curve
    /// @param _pp the modulus
    /// @return (qx, qy) = d*P in affine coordinates
    function ecMul(
        uint256 _k,
        uint256 _x,
        uint256 _y,
        uint256 _aa,
        uint256 _pp)
    internal pure returns(uint256, uint256)
    {
        // Jacobian multiplication
        (uint256 x1, uint256 y1, uint256 z1) = jacMul(
        _k,
        _x,
        _y,
        1,
        _aa,
        _pp);
        // Get back to affine
        return toAffine(
        x1,
        y1,
        z1,
        _pp);
    }

    /// @dev Adds two points (x1, y1, z1) and (x2 y2, z2).
    /// @param _x1 coordinate x of P1
    /// @param _y1 coordinate y of P1
    /// @param _z1 coordinate z of P1
    /// @param _x2 coordinate x of square
    /// @param _y2 coordinate y of square
    /// @param _z2 coordinate z of square
    /// @param _pp the modulus
    /// @return (qx, qy, qz) P1+square in Jacobian
    function jacAdd(
        uint256 _x1,
        uint256 _y1,
        uint256 _z1,
        uint256 _x2,
        uint256 _y2,
        uint256 _z2,
        uint256 _pp)
    internal pure returns (uint256, uint256, uint256)
    {
        if (_x1==0 && _y1==0)
        return (_x2, _y2, _z2);
        if (_x2==0 && _y2==0)
        return (_x1, _y1, _z1);

        // We follow the equations described in https://pdfs.semanticscholar.org/5c64/29952e08025a9649c2b0ba32518e9a7fb5c2.pdf Section 5
        uint[4] memory zs; // z1^2, z1^3, z2^2, z2^3
        zs[0] = mulmod(_z1, _z1, _pp);
        zs[1] = mulmod(_z1, zs[0], _pp);
        zs[2] = mulmod(_z2, _z2, _pp);
        zs[3] = mulmod(_z2, zs[2], _pp);

        // u1, s1, u2, s2
        zs = [
        mulmod(_x1, zs[2], _pp),
        mulmod(_y1, zs[3], _pp),
        mulmod(_x2, zs[0], _pp),
        mulmod(_y2, zs[1], _pp)
        ];

        // In case of zs[0] == zs[2] && zs[1] == zs[3], double function should be used
        require(zs[0] != zs[2] || zs[1] != zs[3], "Use jacDouble function instead");

        uint[4] memory hr;
        //h
        hr[0] = addmod(zs[2], _pp - zs[0], _pp);
        //r
        hr[1] = addmod(zs[3], _pp - zs[1], _pp);
        //h^2
        hr[2] = mulmod(hr[0], hr[0], _pp);
        // h^3
        hr[3] = mulmod(hr[2], hr[0], _pp);
        // qx = -h^3  -2u1h^2+r^2
        uint256 qx = addmod(mulmod(hr[1], hr[1], _pp), _pp - hr[3], _pp);
        qx = addmod(qx, _pp - mulmod(2, mulmod(zs[0], hr[2], _pp), _pp), _pp);
        // qy = -s1*z1*h^3+r(u1*h^2 -x^3)
        uint256 qy = mulmod(hr[1], addmod(mulmod(zs[0], hr[2], _pp), _pp - qx, _pp), _pp);
        qy = addmod(qy, _pp - mulmod(zs[1], hr[3], _pp), _pp);
        // qz = h*z1*z2
        uint256 qz = mulmod(hr[0], mulmod(_z1, _z2, _pp), _pp);
        return(qx, qy, qz);
    }

    /// @dev Doubles a points (x, y, z).
    /// @param _x coordinate x of P1
    /// @param _y coordinate y of P1
    /// @param _z coordinate z of P1
    /// @param _aa the a scalar in the curve equation
    /// @param _pp the modulus
    /// @return (qx, qy, qz) 2P in Jacobian
    function jacDouble(
        uint256 _x,
        uint256 _y,
        uint256 _z,
        uint256 _aa,
        uint256 _pp)
    internal pure returns (uint256, uint256, uint256)
    {
        if (_z == 0)
        return (_x, _y, _z);

        // We follow the equations described in https://pdfs.semanticscholar.org/5c64/29952e08025a9649c2b0ba32518e9a7fb5c2.pdf Section 5
        // Note: there is a bug in the paper regarding the m parameter, M=3*(x1^2)+a*(z1^4)
        // x, y, z at this point represent the squares of _x, _y, _z
        uint256 x = mulmod(_x, _x, _pp); //x1^2
        uint256 y = mulmod(_y, _y, _pp); //y1^2
        uint256 z = mulmod(_z, _z, _pp); //z1^2

        // s
        uint s = mulmod(4, mulmod(_x, y, _pp), _pp);
        // m
        uint m = addmod(mulmod(3, x, _pp), mulmod(_aa, mulmod(z, z, _pp), _pp), _pp);

        // x, y, z at this point will be reassigned and rather represent qx, qy, qz from the paper
        // This allows to reduce the gas cost and stack footprint of the algorithm
        // qx
        x = addmod(mulmod(m, m, _pp), _pp - addmod(s, s, _pp), _pp);
        // qy = -8*y1^4 + M(S-T)
        y = addmod(mulmod(m, addmod(s, _pp - x, _pp), _pp), _pp - mulmod(8, mulmod(y, y, _pp), _pp), _pp);
        // qz = 2*y1*z1
        z = mulmod(2, mulmod(_y, _z, _pp), _pp);

        return (x, y, z);
    }

    /// @dev Multiply point (x, y, z) times d.
    /// @param _d scalar to multiply
    /// @param _x coordinate x of P1
    /// @param _y coordinate y of P1
    /// @param _z coordinate z of P1
    /// @param _aa constant of curve
    /// @param _pp the modulus
    /// @return (qx, qy, qz) d*P1 in Jacobian
    function jacMul(
        uint256 _d,
        uint256 _x,
        uint256 _y,
        uint256 _z,
        uint256 _aa,
        uint256 _pp)
    internal pure returns (uint256, uint256, uint256)
    {
        // Early return in case that `_d == 0`
        if (_d == 0) {
        return (_x, _y, _z);
        }

        uint256 remaining = _d;
        uint256 qx = 0;
        uint256 qy = 0;
        uint256 qz = 1;

        // Double and add algorithm
        while (remaining != 0) {
        if ((remaining & 1) != 0) {
            (qx, qy, qz) = jacAdd(
            qx,
            qy,
            qz,
            _x,
            _y,
            _z,
            _pp);
        }
        remaining = remaining / 2;
        (_x, _y, _z) = jacDouble(
            _x,
            _y,
            _z,
            _aa,
            _pp);
        }
        return (qx, qy, qz);
    }
    }
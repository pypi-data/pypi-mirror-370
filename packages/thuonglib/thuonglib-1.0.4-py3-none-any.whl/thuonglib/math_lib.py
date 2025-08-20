def gcd(a, b):
    '''
    Hàm tính ước chung lớn nhất (GCD) của hai số nguyên a và b.
    Sử dụng thuật toán Euclid.
    :param a: Số nguyên thứ nhất
    :param b: Số nguyên thứ hai
    :return: GCD của a và b
    '''
    while b != 0:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    '''
    Hàm tính ước chung lớn nhất (GCD) của hai số nguyên a và b,
    đồng thời tìm hai số x, y sao cho ax + by = gcd(a, b).
    Sử dụng thuật toán Euclid mở rộng.

    Áp dụng thuật toán trong tìm hệ số d trong RSA.
    Thay a = e, b = phi_n, ta sẽ tìm được d sao cho ed ≡ 1 (mod phi_n).
    Example:
        gcd, d, y = extended_gcd(e, phi_n)

    :param a: Số nguyên thứ nhất
    :param b: Số nguyên thứ hai
    :return: Tuple (gcd, x, y) với gcd là ước chung lớn nhất của a và b,
                x và y là các số thỏa mãn ax + by = gcd(a, b)
    '''
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

def is_prime(n):
    '''
    Hàm kiểm tra xem một số nguyên n có phải là số nguyên tố hay không.
    Một số nguyên tố là số lớn hơn 1 và chỉ chia hết cho 1 và chính nó.

    :param n: Số nguyên cần kiểm tra
    :return: True nếu n là số nguyên tố, False nếu không phải
    '''
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def gf4_mul(a: int, b: int) -> int:
    """
    Nhân hai phần tử a, b trong GF(2^4) với đa thức mũ x^4 + x + 1.
    a, b: số nguyên 0..15 biểu diễn đa thức bậc <4.
    Trả về kết quả cũng trong 0..15.
    """
    # Đa thức mũ P(x) = x^4 + x + 1 -> 0x13
    IRRED_POLY = 0x13
    result = 0
    # Nhân carry-less
    for i in range(4):
        if (b >> i) & 1:
            result ^= a << i
    # Rút gọn modulo P(x)
    # result có thể lên đến 7 bit, ta rút gọn từ bậc cao
    for shift in range(7, 3, -1):  # kiểm tra bit 6..4
        if (result >> shift) & 1:
            # dịch IRRED_POLY lên đúng bậc và XOR
            result ^= IRRED_POLY << (shift - 4)
    # giữ lại 4 bit thấp nhất
    return result & 0xF

def gf_mul(x, y):
    '''
    Multiply two elements in GF(2^128) using carry-less multiplication.
    x, y: 128-bit integers (0 <= x, y < 2^128)
    Returns: 128-bit integer result of multiplication mod R.
    x, y should be in range [0, 2^128 - 1].
    Raises ValueError if x or y is out of range.
    using in AES-GCM for GHASH computation.
    '''
    R = 0xE1000000000000000000000000000000
    # carry-less multiplication
    z = 0
    for i in range(128):
        if (y >> (127 - i)) & 1:
            z ^= x << (127 - i)
    # reduce mod x^128 + x^7 + x^2 + x + 1
    # z can be up to 255 bits
    for i in reversed(range(128, z.bit_length())):
        if (z >> i) & 1:
            z ^= R << (i - 128)
    return z

if __name__ == "__main__":
    gcd, d, y = extended_gcd(3, 20)
    print(f"GCD: {gcd}, d: {d}, y: {y}")
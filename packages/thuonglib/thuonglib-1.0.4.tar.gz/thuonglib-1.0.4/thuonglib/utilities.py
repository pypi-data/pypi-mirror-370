def build_config(config, separator='.'):
    """
    Chuyển cấu trúc lồng nhau (dict, list, tuple) thành một flat dict.
    Mỗi key trong kết quả sẽ bắt đầu bằng separator, theo từng bước xuống sâu.

    Ví dụ:
    config = {'a': {'b': 1}, 'c': [2, 3]}
    build_config(config) =>
        {
        '.a': {'b': 1},
        '.a.b': 1,
        '.c': [2, 3],
        '.c.0': 2,
        '.c.1': 3
        }
    """
    flat_dict = {}

    # 1) Nếu là dict: đệ quy flatten từng giá trị, rồi ghi sub-keys với prefix là tên key hiện tại
    if isinstance(config, dict):
        for k, v in config.items():
            sub = build_config(v, separator)
            # merge các kết quả con (nếu có)
            if sub:
                for sub_key, sub_val in sub.items():
                    # sub_key đã bắt đầu bằng separator, nên nối: .k + sub_key
                    flat_dict[f"{separator}{k}{sub_key}"] = sub_val
            # bản thân node hiện tại cũng được lưu
            flat_dict[f"{separator}{k}"] = v

    # 2) Nếu là list hoặc tuple: tương tự, dùng index làm key
    elif isinstance(config, (list, tuple)):
        for idx, v in enumerate(config):
            sub = build_config(v, separator)
            if sub:
                for sub_key, sub_val in sub.items():
                    flat_dict[f"{separator}{idx}{sub_key}"] = sub_val
            flat_dict[f"{separator}{idx}"] = v

    # 3) Nếu là kiểu cơ bản (int, str, v.v.), không flatten tiếp
    else:
        # Trả về {} để biểu thị “không có dict con”
        return {}

    return flat_dict

def split_bytes(data: bytes, separator: bytes = b'\xfd#nA\x8c?\x964\xae\x06\xfc\x0f\x1cM\xc4"', **options) -> list[bytes]:
    """
    Tách dữ liệu bytes thành các đoạn con dựa trên separator.
    Trả về danh sách các đoạn bytes.

    Example:
        data = b'data1\xfd#nA\x8c?\x964\xae\x06\xfc\x0f\x1cM\xc4"data2'
        split_bytes(data, split_numbers=2) => [b'data1', b'data2'] 
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be of type bytes")
    if not isinstance(separator, bytes):
        raise TypeError("separator must be of type bytes")
    segments = data.split(separator)
    if options:
        if options.get("split_numbers") != len(segments):
            raise ValueError(f"Expected {options['split_numbers']} segments, but got {len(segments)}")
    else:
        raise ValueError("split_numbers option is required")
    return segments

def jonin_bytes(data: list[bytes], separator: bytes = b'\xfd#nA\x8c?\x964\xae\x06\xfc\x0f\x1cM\xc4"') -> bytes:
    """
    Nối các đoạn bytes lại với nhau, sử dụng separator.
    Trả về dữ liệu bytes đã nối.

    Example:
        data = [b'data1', b'data2']
        joined_data = jonin_bytes(data) => b'data1\xfd#nA\x8c?\x964\xae\x06\xfc\x0f\x1cM\xc4"data2'
    """
    if not isinstance(data, list):
        raise TypeError("data must be of type list")
    if not all(isinstance(item, bytes) for item in data):
        raise TypeError("All items in data must be of type bytes")
    return separator.join(data)

def bytes_to_binary(data: bytes) -> str:
    """
    Chuyển đổi dữ liệu bytes thành chuỗi nhị phân.
    Mỗi byte sẽ được biểu diễn dưới dạng 8 bit.

    Example:
        data = b'\x08-\xd6ahds'
        binary_str = bytes_to_binary(data)
        # binary_str sẽ là '00001000 00101101 11010110 01100001 01101000 01100100 01110011'
    """
    return ' '.join(format(byte, '08b') for byte in data)

def bytes_to_hex(data: bytes) -> str:
    """
    Chuyển đổi dữ liệu bytes thành chuỗi hexa.
    Mỗi byte sẽ được biểu diễn dưới dạng 2 ký tự hexa.

    Example:
        data = b'\x08-\xd6ahds'
        hex_str = bytes_to_hex(data)
        hex_str sẽ là '08 2d d6 61 68 64 73'
    """
    return ' '.join(format(byte, '02x') for byte in data)

def bytes_to_int_list(data: bytes) -> list[int]:
    """
    Chuyển đổi dữ liệu bytes thành danh sách các số nguyên.
    Mỗi byte sẽ được chuyển đổi thành một số nguyên.

    Example:
        data = b'\x08-\xd6ahds'
        int_list = bytes_to_int_list(data)
        # int_list sẽ là [8, 45, 214, 97, 104, 100, 115]
    """
    return [byte for byte in data]

def bytes_to_base64(data: bytes) -> str:
    """
    Chuyển đổi dữ liệu bytes thành chuỗi Base64.
    
    Example:
        data = b'\x08-\xd6ahds'
        base64_str = bytes_to_base64(data)
        base64_str sẽ là 'CDst1mFoZHNz'
    """
    import base64
    return base64.b64encode(data).decode('utf-8')

def base64_to_bytes(base64_str: str) -> bytes:
    """
    Chuyển đổi chuỗi Base64 thành dữ liệu bytes.
    
    Example:
        base64_str = 'CDst1mFoZHNz'
        data = base64_to_bytes(base64_str)
        data sẽ là b'\x08-\xd6ahds'
    """
    import base64
    return base64.b64decode(base64_str.encode('utf-8'))

def bytes_distance_bytes(b1: bytes, b2: bytes, algorithm: int = 1) -> int:
    """
    Tính khoảng cách giữa hai chuỗi bytes.\n
    algorithm = 1 (default) sử dụng hàm hamming_distance, hàm tính khoảng cách Hamming (số bit khác nhau).\n
    algorithm = 0 sử dụng hàm byte_diff_sum, hàm tính tổng độ lệch tuyệt đối trên từng byte.
    
    Example:
        b1 = b'\x08-\xd6ahds'
        b2 = b'\x08-\xd6ahds'
        distance = bytes_distance_bytes(b1, b2)
        distance sẽ là 0 vì hai chuỗi giống nhau
    """
    if len(b1) != len(b2):
        raise ValueError("Both byte sequences must have the same length")
    if algorithm:
        print(f"Using algorithm hamming_distance for distance calculation.")
        return sum(bin(x ^ y).count('1') for x, y in zip(b1, b2))
    print(f"Using algorithm byte_diff_sum for distance calculation.")
    return sum(abs(x - y) for x, y in zip(b1, b2))

def convert_to_base(x: int, base: int) -> list[int]:
    '''
    Convert an integer to a list of digits in a given base.

    :param x: The integer to convert.
    :param base: The base to convert to (e.g., 2 for binary).
    :return: A list of digits representing the number in the specified base.

    Example:
    >>> convert_to_base(545785, 2)
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1]
    '''
    res = []
    quotient, remainder = divmod(x, base)
    res.append(remainder)
    while quotient != 0:
        quotient, remainder = divmod(quotient, base)
        res.append(remainder)
    res.reverse()
    return res

class cipher_utilities:

    @staticmethod
    def ghash(H, A, C):
        '''
        Compute GHASH for AES-GCM.
        H: 128-bit integer subkey for GHASH
        A: list of 128-bit integers (AAD blocks)
        C: list of 128-bit integers (ciphertext blocks)
        Returns: 128-bit integer result of GHASH.
        Raises ValueError if H is not a 128-bit integer or A/C contain invalid values.
        Uses carry-less multiplication and reduction by polynomial R.
        using constant R = 0xE1000000000000000000000000000000 for reduction.
        Example usage:
        H = 0x66e94bd4ef8a2c3b884cfa59ca342b2e  # example subkey
        A = [0xfeedfacedeadbeeffeedfacedeadbeef]  # example AAD block
        C = [0x42831ec2217774244b7221b784d0d49c]  # example ciphertext block
        gh = ghash(H, A, C)
        hex_gh = f"{gh:032x}"  # format as hex string
        print(f"GHASH: {hex_gh}")
        '''
        from thuonglib.math_lib import gf_mul
        # A and C are lists of 128-bit ints
        # length bits
        lenA = len(A)*128
        lenC = len(C)*128
        # form X blocks: A blocks + C blocks + length block
        X = A + C + [ (lenA << 64) | lenC ]
        Y = 0
        for Xi in X:
            Y = gf_mul(Y ^ Xi, H)
        return Y

    @staticmethod
    def rotr(x, n, w=32):
        '''
        Rotate right x by n bits in a w-bit word.
        x: integer to rotate
        n: number of bits to rotate
        w: word size in bits (default 32)
        Returns: rotated integer.

        Example usage:
        x = 0x12345678
        n = 4
        rotated = rotr(x, n)
        hex_rotated = f"{rotated:08x}"
        print(f"Rotated: {hex_rotated}")
        Output: Rotated: 81234567
        '''
        return ((x >> n) | (x << (w-n))) & (2**w-1)
    
    @staticmethod
    def sigma0(x):
        '''
        Compute the SHA-256 sigma0 function.
        x: 32-bit integer input
        Returns: 32-bit integer result of sigma0.

        Example usage:
        x = 0x12345678
        result = sigma0(x)
        hex_result = f"{result:08x}"
        print(f"Sigma0: {hex_result}")
        '''
        return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)

    @staticmethod
    def sigma1(x):
        '''
        Compute the SHA-256 sigma1 function.
        x: 32-bit integer input
        Returns: 32-bit integer result of sigma1.

        Example usage:
        x = 0x12345678
        result = sigma1(x)
        hex_result = f"{result:08x}"
        print(f"Sigma1: {hex_result}")
        '''
        return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)
    
    @staticmethod
    def SHA_256(message: bytes | str) -> str:
        print("\nĐang sử dụng my hash, SHA_256.")
        import struct

        # Hằng số ban đầu (8 giá trị băm ban đầu - lấy từ căn bậc hai của các số nguyên tố đầu tiên)
        H = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]

        # Hằng số K cho 64 vòng lặp (lấy từ căn bậc ba của các số nguyên tố đầu tiên)
        K = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]

        def right_rotate(x, n):
            """Hàm xoay phải n bit trên số 32-bit."""
            return (x >> n) | (x << (32 - n)) & 0xFFFFFFFF

        def prepare_message(message):
            """Chuẩn bị dữ liệu đầu vào theo đặc tả SHA-256."""
            # Chuyển chuỗi thành bytes nếu chưa phải bytes
            if isinstance(message, str):
                message = message.encode()
            
            # Độ dài ban đầu của message (tính bằng bit)
            original_bit_len = len(message) * 8
            
            # Thêm bit '1' (byte 0x80)
            message += b'\x80'
            
            # Thêm các bit '0' để độ dài là bội số của 512, trừ 64 bit cuối
            while (len(message) * 8 + 64) % 512 != 0:
                message += b'\x00'
            
            # Thêm độ dài ban đầu dưới dạng số 64-bit (big-endian)
            message += struct.pack('>Q', original_bit_len)
            
            return message

        def sha256(message):
            """Hàm chính tính giá trị băm SHA-256."""
            # Chuẩn bị dữ liệu
            padded_message = prepare_message(message)
            
            # Khởi tạo các giá trị băm ban đầu
            h0, h1, h2, h3, h4, h5, h6, h7 = H
            
            # Chia dữ liệu thành các khối 512-bit
            for i in range(0, len(padded_message), 64):
                block = padded_message[i:i+64]
                
                # Mở rộng khối thành 64 từ 32-bit
                w = [0] * 64
                for j in range(16):
                    w[j] = struct.unpack('>I', block[j*4:j*4+4])[0]
                for j in range(16, 64):
                    s0 = right_rotate(w[j-15], 7) ^ right_rotate(w[j-15], 18) ^ (w[j-15] >> 3)
                    s1 = right_rotate(w[j-2], 17) ^ right_rotate(w[j-2], 19) ^ (w[j-2] >> 10)
                    w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFF
                
                # Khởi tạo các biến cho vòng lặp
                a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
                
                # 64 vòng lặp chính
                for j in range(64):
                    S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
                    ch = (e & f) ^ ((~e) & g)
                    temp1 = (h + S1 + ch + K[j] + w[j]) & 0xFFFFFFFF
                    S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
                    maj = (a & b) ^ (a & c) ^ (b & c)
                    temp2 = (S0 + maj) & 0xFFFFFFFF
                    
                    h = g
                    g = f
                    f = e
                    e = (d + temp1) & 0xFFFFFFFF
                    d = c
                    c = b
                    b = a
                    a = (temp1 + temp2) & 0xFFFFFFFF
                
                # Cập nhật giá trị băm
                h0 = (h0 + a) & 0xFFFFFFFF
                h1 = (h1 + b) & 0xFFFFFFFF
                h2 = (h2 + c) & 0xFFFFFFFF
                h3 = (h3 + d) & 0xFFFFFFFF
                h4 = (h4 + e) & 0xFFFFFFFF
                h5 = (h5 + f) & 0xFFFFFFFF
                h6 = (h6 + g) & 0xFFFFFFFF
                h7 = (h7 + h) & 0xFFFFFFFF
            
            # Tạo giá trị băm cuối cùng dưới dạng chuỗi hex
            return ''.join(format(x, '08x') for x in [h0, h1, h2, h3, h4, h5, h6, h7])
        
        # Gọi hàm tính SHA-256
        return sha256(message)
    
    @staticmethod
    # Tạo chữ ký cho file
    def my_sign_file(M = None,file_out = None, salt_len=32, hash_func=SHA_256):
        """
        Sign a file using RSA-PSS
        salt_len = 32 bytes.
        """
        print("\nĐang chạy thuật toán my sign.")
        from Crypto.Random                      import get_random_bytes
        import math
        import asn1tools
        from pathlib                            import Path
        import os
        if M is None:
            file_path = r"{}".format(input("Nhap duong dan file can ký: "))
        n  = int(input("Nhập số n: ").strip())
        d  = int(input("Nhập số d: ").strip())
        private_key = (d, n)
        if M is None:
            with open(file_path, 'rb') as f:
                M = f.read()  # Đọc nội dung file
        salt = get_random_bytes(salt_len)  # Sinh salt ngẫu nhiên
        M_salt = M + salt
        m_salt_hash = hash_func(M_salt)
        m_salt_hash = bytes.fromhex(m_salt_hash)
        m_int = int.from_bytes(m_salt_hash, 'big')
        s = cipher_utilities.rsa_decrypt(m_int, *private_key)  # Tạo chữ ký bằng khóa riêng
        signature = int.to_bytes(s, math.ceil((s.bit_length()) / 8), 'big')
        spec = asn1tools.compile_files('file_asn.asn', codec='der')
        try:
            path = Path(file_path)
            filename = path.stem
        except:
            filename = "filename"
        file_M = {
            'namefile':  filename,
            'datafile':   M,
        }
        file_salt = {
            'namefile':  'salt',
            'datafile':   salt,
        }
        file_sign = {
            'namefile':  'sign',
            'datafile':   signature,
        }
        files = [file_M, file_salt, file_sign]
        der_files = spec.encode('FileList', files)
        if file_out is None:
            file_path += '.signed'
            with open(file_path, 'wb') as f:
                f.write(der_files)
            print('Đã ký file.')
            print(f"file đã ký lưu tại: {file_path}")
            os.remove(file_path[:-7])
            print(f"Đã xóa file: {file_path[:-7]}")
        else:
            file_out += '.signed'
            with open(file_out, 'wb') as f:
                f.write(der_files)
            print('Đã ký file.')
            print(f"file đã ký lưu tại: {file_out}")
        return
    
    @staticmethod
    def my_verify_signature(hash_func=SHA_256):
        """Verify a signature using RSA-PSS"""
        print("\nĐang chạy thuật toán my sign.")
        import math
        import asn1tools
        from pathlib                            import Path
        import os
        file_path = r"{}".format(input("\nNhap duong dan file can xác minh chữ ký: "))
        n  = int(input("\nNhập số n: ").strip())
        e  = int(input("\nNhập số e: ").strip())
        public_key = (e, n)
        with open(file_path, 'rb') as f:
            data = f.read()  # Đọc nội dung file
        spec = asn1tools.compile_files('file_asn.asn', codec='der')
        decoded_files = spec.decode('FileList', data)
        M = decoded_files[0]['datafile']
        salt = decoded_files[1]['datafile']
        signature = decoded_files[2]['datafile']
        M_salt = M + salt
        m_salt_hash = hash_func(M_salt)
        m_salt_hash = bytes.fromhex(m_salt_hash)
        s = int.from_bytes(signature, 'big')
        m = cipher_utilities.rsa_encrypt(s, *public_key)  # Giải mã chữ ký bằng khóa công khai
        m_salt_hash_sign = int.to_bytes(m, math.ceil((m.bit_length()) / 8), 'big')
        if m_salt_hash == m_salt_hash_sign:
            with open(f'{file_path[:-7]}', 'wb') as f:
                f.write(M)
            print("\nChữ ký số hợp lệ.")
            print(f"Đã tạo file: {file_path[:-7]}")
            choice = input(f"\nBạn có muốn xóa file {file_path} không? (y/n): ").strip().lower()
            while choice not in ('y', 'n'):
                choice = input("Khong hop le. Vui long nhap 'y' hoac 'n': ").strip().lower()
            if choice == 'y':
                os.remove(file_path)
                print(f"\nFile {file_path} da duoc xoa.")
            else:
                print(f"\nKhong xoa file {file_path}")
            return file_path[:-7]
        print("\nChữ ký số không hợp lệ.")
        return False
    
    @staticmethod
    # Sinh cặp khóa RSA
    def generate_rsa_keys(bits=2048):
        """
        Generate RSA keys.
        bits = 2048, độ dài modulus n bằng 2048 bits, n được biểu diển ra số nhị phân dùng 2048 bits.
        """
        from Crypto.Util.number                 import getPrime
        p = getPrime(bits // 2)
        q = getPrime(bits // 2)
        while p == q:  # Đảm bảo p và q khác nhau
            cipher_utilities.generate_rsa_keys(bits)
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 65537  # Giá trị phổ biến cho e
        d = pow(e, -1, phi)  # Tính d
        return (e, n), (d, n)  # Trả về khóa công khai (e, n) và khóa riêng (d, n)

    @staticmethod
    # Mã hóa RSA (dùng khóa công khai)
    def rsa_encrypt(m, e, n):
        """RSA encryption"""
        return pow(m, e, n)
    @staticmethod
    # Giải mã RSA (dùng khóa riêng)
    def rsa_decrypt(c, d, n):
        """RSA decryption"""
        return pow(c, d, n)

    @staticmethod
    def enc_hash_sign(my_sign_file = my_sign_file, hash_func=SHA_256):
        from thuonglib.encrypt_decrypt_file         import encrypt_file
        from Crypto.Random                          import get_random_bytes
        import math
        import asn1tools
        from pathlib                                import Path
        import os
        print("\nĐang chạy thuật toán my.")
        # Mã hóa file.
        output_file = encrypt_file()
        # Tạo file hash + enc.
        with open(output_file, 'rb') as f:
            data = f.read()
        hash = hash_func(data)
        hash = bytes.fromhex(hash)
        enc_hash = hash + data
        del data, hash
        # Tạo file enc + hash + sign.
        my_sign_file(M = enc_hash,file_out = output_file)
        os.remove(output_file)
        return
    
    @staticmethod
    def Vsign_Chash_def(my_verify_signature = my_verify_signature, hash_func=SHA_256):
        from Crypto.Random                          import get_random_bytes
        import math
        import asn1tools
        from pathlib                                import Path
        import os
        import base64
        print("\nĐang chạy thuật toán my.")
        # Xác minh chữ ký số, xác minh nguồn gốc.
        file_path = my_verify_signature()
        if file_path:
            print("\nChữ ký số hợp lệ.")
        else:
            print("\nChữ ký số không hợp lệ.")
            return
        # Kiểm tra tra tính toàn vẹn của dữ liệu.
        with open(file_path, 'rb') as f:
            raw = f.read()
        value_hash = raw[:32]
        data = raw[32:]
        del raw
        hash = hash_func(data)
        hash = bytes.fromhex(hash)
        if hash == value_hash:
            print("\nDữ liệu toàn vẹn.")
            del hash, value_hash
        else:
            print("\nDữ liệu không toàn vẹn.")
            return
        # Giải mã file bằng thuật toán XOR.
        print("\nĐang chạy thuật toán my_XOR.")
        key = input("Nhap khoa giai ma data: ").encode('utf-8')
        cipher_data_level1 = base64.b64decode(data)
        decrypted_data = bytes(p ^ key[i % len(key)] for i, p in enumerate(cipher_data_level1))
        output_file = file_path[:-4]  # Loại bỏ phần mở rộng .enc

        with open(output_file, 'wb') as f:
            f.write(decrypted_data)

        print("**********************************************************************")
        print(f"File da duoc giai ma va luu tai: {output_file}")
        print("**********************************************************************")
        return

    @staticmethod
    def sign_file(file_path: str, private_key_path: str, passworld_key: bool = True) -> bool:
        """
        Tạo chữ ký số cho file sử dụng khóa riêng RSA.
        Chương trình sử dụng thư viện pycryptodome.
        Cấu trúc file .sig: "4 bytes đầu là chiều dài của signature, tính bằng bytes | signature | file"

        :param file_path: Đường dẫn đến file cần ký (chuỗi).
        :param private_key_path: Đường dẫn đến file .pem chứa khóa riêng RSA.
        """
        from Crypto.PublicKey           import RSA
        from Crypto.Signature           import pss
        from Crypto.Hash                import SHA256
        import getpass
        import struct
        import os
        
        print("\nĐang chạy thuật toán tạo chữ ký số, sử dụng thư viện pycryptodome.")
        hash_obj = SHA256.new()
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hash_obj.update(chunk)
        # Nhập khóa riêng tư từ file ".PEM".
        if passworld_key:
            passphrase = getpass.getpass("Nhập chuỗi mật khẩu được sử dụng để bảo vệ khóa riêng tư: ").strip()
        with open(private_key_path, 'rb') as f:
            private_key = RSA.import_key(f.read(), passphrase = f'{passphrase}' if passworld_key else None)
        signer = pss.new(private_key)
        signature = signer.sign(hash_obj)
        with open(file_path, 'rb') as fr, open(file_path + '.sig', 'wb') as fw:
            fw.write(struct.pack('>I', len(signature)))
            fw.write(signature)
            while chunk := fr.read(4096):
                fw.write(chunk)
            del chunk
        file_path += ".sig"
        print("\nĐã tạo chữ ký số.")
        print(f"Đã lưu file {file_path}.")
        os.remove(file_path[:-4])
        print(f"Đã xóa file {file_path[:-4]}")
        return

    @staticmethod
    def verify_signature(file_path: str, public_key_path: str) -> bool:
        """
        Xác minh chữ ký số của file .sig, sử dụng khóa công khai RSA.
        Cấu trúc file .sig: "4 bytes đầu là chiều dài của signature, tính bằng bytes | signature | file"

        :param file_path: Đường dẫn đến file cần xác minh (chuỗi).
        :return: True nếu chữ ký hợp lệ, False nếu không.
        """
        from Crypto.PublicKey       import RSA
        from Crypto.Signature       import pss
        from Crypto.Hash            import SHA256
        import struct
        import os

        print("\nĐang chạy thuật toán xác minh chữ ký số, sử dụng thư viện pycryptodome.")
        hash_obj = SHA256.new()
        # Nhập khóa công khai từ file ".PEM".
        with open(public_key_path, 'rb') as f:
            public_key = RSA.import_key(f.read())
        with open(file_path, 'rb') as f, open(file_path[:-4], 'wb') as fw:
            # Đọc độ dài signature (bytes).
            signature_len = struct.unpack('>I', f.read(4))[0]
            signature = f.read(signature_len)
            while chunk := f.read(4096):
                hash_obj.update(chunk)
                fw.write(chunk)
        verifier = pss.new(public_key)
        try:
            verifier.verify(hash_obj, signature)
            print("\nChữ ký số hợp lệ.")
            choice = input(f"Ban co muon xoa file {file_path} khong? (y/n): ").strip().lower()
            while choice not in ('y', 'n'):
                choice = input("Khong hop le. Vui long nhap 'y' hoac 'n': ").strip().lower()
            if choice == 'y':
                os.remove(file_path)
                print("**********************************************************************")
                print(f"File {file_path} da duoc xoa.")
                print("**********************************************************************")
            else:
                print("**********************************************************************")
                print(f"Khong xoa file {file_path}.")
                print("**********************************************************************")
            return True
        except (ValueError, TypeError):
            print("\nChữ ký số không hợp lệ.")
            return False

class bit_utilities:

    @staticmethod
    def bit_status(value: int, bit_pos: int) -> bool:
        """
        Kiểm tra trạng thái của bit thứ bit_pos (tính từ 1) trong giá trị value.
        Độ rộng của value là 8 bit (int).
        Trả về True nếu bit được bật (1), ngược lại trả về False (0).
        """
        if not isinstance(value, int):
            raise TypeError("value must be an integer")
        if bit_pos < 1 or bit_pos > 8:
            raise ValueError("bit_pos must be between 1 and 8")
        # Kiểm tra bit thứ bit_pos (tính từ 1)
        return (value & (1 << (bit_pos - 1))) != 0
    
    @staticmethod
    def change_bit(value: int, bit_pos: int) -> int:
        """
        Thay đổi trạng thái của bit thứ bit_pos (tính từ 1, one-based) trong giá trị value.
        Độ rộng của value là 8 bit (int).
        Trả về giá trị mới sau khi thay đổi bit.
        """
        if not isinstance(value, int):
            raise TypeError("value must be an integer")
        if bit_pos < 1 or bit_pos > 8:
            raise ValueError("bit_pos must be between 1 and 8")
        if bit_utilities.bit_status(value, bit_pos):
            # Nếu bit đang bật (1), tắt nó
            return value & ~(1 << (bit_pos - 1))
        else:
            # Nếu bit đang tắt (0), bật nó
            return value | (1 << (bit_pos - 1))

    @staticmethod
    def toggle_bit(x: int, k: int, w: int) -> int:
        """
        Toggle (đảo) trạng thái bit thứ k (one-based) của x, với độ rộng w bit.
        
        Tham số:
        x (int): số nguyên gốc (có thể lớn hơn w bit, nhưng chúng ta chỉ quan tâm w bit thấp nhất).
        k (int): vị trí bit (1 ≤ k ≤ w), đếm từ 1 (bit 1 là LSB).
        w (int): độ rộng bit, phải ≥ 1.
        
        Trả về:
        int: số nguyên mới sau khi đã toggle bit thứ k và cắt về đúng w bit.
        """
        if not (1 <= k <= w):
            raise ValueError(f"k phải nằm trong [1, {w}], nhưng k={k}")
        
        # Tạo mask có duy nhất bit thứ k (one-based) = 1
        mask = 1 << (k - 1)
        
        # XOR để lật bit; AND với (2**w - 1) để giữ đúng w bit thấp
        return (x ^ mask) & ((1 << w) - 1)


if __name__ == "__main__":
    import sys
    sys.path.pop(0)

    # cipher_utilities.sign_file(r"D:\Phanmem\test\LICENSE-3RD-PARTY.txt", r"G:\My Drive\backup\RSA_USE\private.pem")
    cipher_utilities.verify_signature(r"D:\Phanmem\test\LICENSE-3RD-PARTY.txt.sig", r"G:\My Drive\backup\RSA_USE\public.pem")
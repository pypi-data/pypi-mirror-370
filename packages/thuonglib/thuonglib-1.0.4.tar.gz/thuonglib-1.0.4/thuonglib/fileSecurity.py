from Crypto.Cipher                  import AES
from Crypto.Random                  import get_random_bytes
import os
import getpass
from Crypto.PublicKey               import RSA
from Crypto.Cipher                  import PKCS1_OAEP
import getpass
from Crypto.Hash                    import SHA3_512
import struct
from Crypto.Signature               import pss

# 1.1. Mã hóa file bằng AES_GCM.
def AES_GCM(file_path):
    print("\nĐang chạy thuật toán mã hóa file bằng AES_GCM.")
    # Tự sinh ngẫu nhiên key 256-bit (32 bytes).
    key_AES = get_random_bytes(32)
    # GCM mặc định sử dụng nonce 12 byte.
    nonce_size = 12
    tag_size   = 16
    # Khởi tạo nonce, nonce chỉ dùng 1 lần.
    nonce = get_random_bytes(nonce_size)
    if not os.path.exists(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin'):
        print("\nTao file nonce.bin de luu nonce...")
        open(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin', "w").close()
        print("\nFile nonce.bin da duoc tao thanh cong.")
    with open(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin', 'rb') as f:
        existing_nonce = f.read()
    while nonce in existing_nonce:
        print("\nNonce đã tồn tại, tạo nonce mới...")
        nonce = get_random_bytes(nonce_size)
    with open(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin', 'ab') as f:
        f.write(nonce)
    del existing_nonce
    # Mã hóa file bằng AES_GCM.
    with open(file_path, 'rb') as f:
        data = f.read()
    """
    Mã hoá toàn bộ data, trả về bytes:
    [nonce(12)][tag(16)][ciphertext]
    """
    cipher = AES.new(key_AES, AES.MODE_GCM, nonce = nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return key_AES, nonce + tag + ciphertext

# 1.2. Mã hóa key AES_GCM bằng RSA_OAEP.
def RSA_OAEP(key_AES: str, data: bytes, public_key_path: str, passworld_key: bool = False):
    print("\nĐang chạy thuật toán RSA_OAEP để mã hóa khóa key_AES.")
    # Nhập khóa công khai từ file ".PEM".
    if passworld_key:
        passphrase = getpass.getpass("Nhập chuỗi mật khẩu được sử dụng để bảo vệ khóa: ").strip()
    with open(public_key_path, 'rb') as f:
        public_key = RSA.import_key(f.read(), passphrase = f'{passphrase}' if passworld_key else None)
    # Mã hóa key_AES (bytes) với khóa công khai, trả về bytes.
        cipher = PKCS1_OAEP.new(public_key)
        cipher_key_AES = cipher.encrypt(key_AES)
        # Tạo 8 bytes lưu trữ chiều dài khóa mã hóa AES.
        len_cipher_key_AES =  struct.pack('>Q', len(cipher_key_AES))
    return len_cipher_key_AES + cipher_key_AES + data
# Kết quả của mã hóa file_path: len_cipher_key_AES (8 bytes) | cipher_key_AES | nonce (12 bytes) | tag (16 bytes) | ciphertext.

# 2. Tạo mã băm hash lên kết quả của mã hóa.
# data = len_cipher_key_AES (8 bytes) | cipher_key_AES | nonce (12 bytes) | tag (16 bytes) | ciphertext.
def hash_512(data: bytes) -> bytes:
    print("\nĐang chạy thuật toán băm SHA3_512.")
    sha3_512_hash = SHA3_512.new()
    sha3_512_hash.update(data)
    return sha3_512_hash.digest() + data
# kết quả hash là chuỗi bytes dài 64 bytes.
# Dữ liệu cho thuật toán tạo chữ ký số, data = hash (64bytes) | len_cipher_key_AES (8 bytes) | cipher_key_AES | nonce (12 bytes) | tag (16 bytes) | ciphertext.

# 3. Tạo chữ ký số.
# data = hash (64bytes) | len_cipher_key_AES (8 bytes) | cipher_key_AES | nonce (12 bytes) | tag (16 bytes) | ciphertext.
def sign_file(file_path: str, data: bytes, private_key_path: str, passworld_key: bool = True) -> bool:
    print("\nĐang chạy thuật toán tạo chữ ký số, sử dụng thư viện pycryptodome.")
    sha3_512_hash = SHA3_512.new()
    sha3_512_hash.update(data)
    # Nhập khóa riêng tư từ file ".PEM".
    if passworld_key:
        passphrase = getpass.getpass("Nhập chuỗi mật khẩu được sử dụng để bảo vệ khóa riêng tư: ").strip()
    with open(private_key_path, 'rb') as f:
        private_key = RSA.import_key(f.read(), passphrase = f'{passphrase}' if passworld_key else None)
    signer = pss.new(private_key)
    signature = signer.sign(sha3_512_hash)
    with open(file_path + '.enc.sig', 'wb') as f:
        '''
        Tạo 8 bytes lưu chiều dài signature (bytes).
        Cấu trúc file .sig:
        len_signature (8 bytes) | signature | hash (64bytes) | len_cipher_key_AES (8 bytes) | cipher_key_AES | nonce (12 bytes) | tag (16 bytes) | ciphertext.
        '''
        f.write(struct.pack('>Q', len(signature)))
        f.write(signature)
        f.write(data)
    print("\nĐã tạo chữ ký số.")
    print(f"\nĐã lưu file {file_path}.enc.sig")
    os.remove(file_path)
    print(f"\nĐã xóa file {file_path}")
    return True

def file_Security(file_path: str, private_key_path: str, pass_key_private: bool, public_key_path: str, pass_key_public: bool) -> bool:
    enc_AES = AES_GCM(file_path)
    enc_RSA = RSA_OAEP(enc_AES[0], enc_AES[1], public_key_path, pass_key_public)
    hash_data = hash_512(enc_RSA)
    sign_file(file_path, hash_data, private_key_path, pass_key_private)
    return True

def unFileSecurity(file_path: str, private_key_path: str, pass_key_private: bool, public_key_path: str, pass_key_public: bool) -> bool:
    # 1. Xác minh chữ ký số.
    print("\nĐang chạy thuật toán xác minh chữ ký số, sử dụng thư viện pycryptodome.")
    with open(file_path, 'rb') as f:
        # Đọc độ dài signature (bytes).
        signature_len = struct.unpack('>Q', f.read(8))[0]
        signature = f.read(signature_len)
        data = f.read()
    # Nhập khóa công khai từ file ".PEM".
    with open(public_key_path, 'rb') as f:
        public_key = RSA.import_key(f.read())
    # Tạo mã băm từ data.
    sha3_512_hash = SHA3_512.new()
    sha3_512_hash.update(data)
    # Xác minh chữ ký số.
    verifier = pss.new(public_key)
    try:
        verifier.verify(sha3_512_hash, signature)
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

        del signature_len, signature
        # 2. Xác minh dữ liệu không bị thay đổi.
        with open(file_path, 'rb') as f:
            # Đọc độ dài signature (bytes).
            signature_len = struct.unpack('>Q', f.read(8))[0]
            signature = f.read(signature_len)
            hash_enc = f.read(64)
            len_cipher_key_AES = f.read(8)
            len_cipher_key_AES2 = struct.unpack('>Q', len_cipher_key_AES)[0]
            cipher_key_AES = f.read(len_cipher_key_AES2)
            nonce = f.read(12)
            tag = f.read(16)
            ciphertext = f.read()
        del signature_len, signature
        sha3_512_hash = SHA3_512.new()
        sha3_512_hash.update(len_cipher_key_AES + cipher_key_AES + nonce + tag + ciphertext)
        if hash_enc == sha3_512_hash.digest():
            print("\nDữ liệu không bị thay đổi.")
        else:
            print("\nDữ liệu đã bị thay đổi.")
            return False
        del hash_enc
        # 3. Giải mã khóa AES bằng RSA_OAEP.
        # Nhập khóa riêng tư từ file ".PEM".
        if pass_key_private:
            passphrase = getpass.getpass("Nhập chuỗi mật khẩu được sử dụng để bảo vệ khóa riêng tư: ").strip()
        with open(private_key_path, 'rb') as f:
            private_key = RSA.import_key(f.read(), passphrase = f'{passphrase}' if pass_key_private else None)
        cipher = PKCS1_OAEP.new(private_key)
        key_AES =  cipher.decrypt(cipher_key_AES)
        del len_cipher_key_AES, len_cipher_key_AES2, cipher_key_AES
        # 4. Giải mã ciphertext bằng key_AES.
        if not os.path.exists(r'D:\Duan\20publish_pypi\thuongcli\nonce_receive.bin'):
            open(r'D:\Duan\20publish_pypi\thuongcli\nonce_receive.bin', "w").close()
        with open(r'D:\Duan\20publish_pypi\thuongcli\nonce_receive.bin', 'rb') as f:
            existing_nonce_receive = f.read()
        if nonce in existing_nonce_receive:
            print("\nNonce_receive đã tồn tại, file không an toàn.")
            return False
        with open(r'D:\Duan\20publish_pypi\thuongcli\nonce_receive.bin', 'ab') as f:
            f.write(nonce)
        cipher = AES.new(key_AES, AES.MODE_GCM, nonce = nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        with open(file_path[:-8], 'wb') as f:
            f.write(plaintext)
        print("**********************************************************************")
        print(f"File da duoc giai ma va luu tai: {file_path[:-8]}")
        print("**********************************************************************")
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
        print("success !".upper())
        return True
    except (ValueError, TypeError):
        print("\nChữ ký số không hợp lệ.")
        return False
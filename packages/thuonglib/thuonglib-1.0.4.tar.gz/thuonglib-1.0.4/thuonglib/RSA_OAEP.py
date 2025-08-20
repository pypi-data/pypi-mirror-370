from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from thuonglib.utilities import build_config
import yaml
import getpass
from thuonglib.AES_CBC import encrypt_file_AES_CBC, decrypt_file_AES_CBC
import os

class RSA_OAEP_Cipher:
    def __init__(self, init_key: int = 1, key_size: int = 2048):
        if init_key:
            # Sinh cặp khóa RSA với kích thước key_size bit
            self.key = RSA.generate(key_size)
            self.public_key = self.key.publickey()
        else:
            key, public_key = import_keys_RSA_OAEP()
            self.key = key
            self.public_key = public_key

    def export_keys(self, priv_path: str = 'private.pem', pub_path: str = 'public.pem', passphrase: str = None):
        # Xuất khóa riêng và khóa công khai ra file PEM
        private_bytes = self.key.export_key(passphrase=passphrase, pkcs=8,
                                           protection="scryptAndAES128-CBC" if passphrase else None)
        with open(priv_path, 'wb') as f:
            f.write(private_bytes)
        with open(pub_path, 'wb') as f:
            f.write(self.public_key.export_key())

    def load_keys(self, priv_path: str, pub_path: str, passphrase: str = None):
        # Đọc khóa từ file PEM
        with open(priv_path, 'rb') as f:
            self.key = RSA.import_key(f.read(), passphrase=passphrase)
        with open(pub_path, 'rb') as f:
            self.public_key = RSA.import_key(f.read())

    def encrypt(self, plaintext: bytes, public_key) -> bytes:
        # Mã hóa plaintext (bytes) với khóa công khai, trả về bytes
        cipher = PKCS1_OAEP.new(public_key)
        ciphertext = cipher.encrypt(plaintext)
        return ciphertext
    def decrypt(self, ciphertext: bytes) -> bytes:
        # Giải mã ciphertext với khóa riêng, trả về plaintext bytes
        cipher = PKCS1_OAEP.new(self.key)
        return cipher.decrypt(ciphertext)

def export_keys_RSA_OAEP(path_config = 'config.yaml'):
    print("**********************************************************************")
    data_print = """
1. Tạo file cấu hình config.yaml với nội dung:
export_keys:
    priv_path: G:\My Drive\backup\RSA_OAEP\private.pem
    pub_path: G:\My Drive\backup\RSA_OAEP\public.pem
2. Tạo thư mục G:\My Drive\backup\RSA_OAEP
3. Di chuyển đến thư mục chứa file config.yaml
4. Chạy lệnh: python RSA_OAEP.py"""
    print(data_print)
    del data_print
    print("**********************************************************************")

    # Khởi tạo đối tượng, sinh khóa
    rsa_cipher = RSA_OAEP_Cipher(key_size=2048)

    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Chuyển đổi cấu hình thành dạng phẳng
    flat_config = build_config(config)

    priv_path = flat_config.get('.export_keys.priv_path')
    pub_path = flat_config.get('.export_keys.pub_path')

    passphrase = getpass.getpass("Nhập chuỗi mật khẩu được sử dụng để bảo vệ khóa riêng tư: ")
    passphrase_confirm = getpass.getpass("Xác nhận chuỗi mật khẩu: ")
    passphrase_confirm2 = getpass.getpass("Xác nhận lại chuỗi mật khẩu: ")

    while passphrase != passphrase_confirm or passphrase != passphrase_confirm2:
        print("Chuỗi mật khẩu không khớp, vui lòng thử lại.")
        passphrase = getpass.getpass("Nhập chuỗi mật khẩu được sử dụng để bảo vệ khóa riêng tư: ")
        passphrase_confirm = getpass.getpass("Xác nhận chuỗi mật khẩu: ")
        passphrase_confirm2 = getpass.getpass("Xác nhận lại chuỗi mật khẩu: ")

    del passphrase_confirm, passphrase_confirm2

    # Xuất khóa ra file
    rsa_cipher.export_keys(priv_path=priv_path, pub_path=pub_path, passphrase=passphrase)
    print("**********************************************************************")
    print(f"Khóa riêng đã được lưu tại: {priv_path}")
    print(f"Khóa công khai đã được lưu tại: {pub_path}")
    print("**********************************************************************")
    return

def import_keys_RSA_OAEP(path_config = 'config.yaml'):
    '''
    Trả về đối tượng khóa riêng và khóa công khai RSA đã được nhập từ file PEM.

    In ra khóa riêng và khóa công khai dưới dạng chuỗi.
    print("Private Key:", key.export_key().decode('utf-8'))
    print("Public Key:", public_key.export_key().decode('utf-8'))
    '''
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Chuyển đổi cấu hình thành dạng phẳng
    flat_config = build_config(config)

    priv_path = flat_config.get('.export_keys.priv_path')
    pub_path = flat_config.get('.export_keys.pub_path')

    passphrase = getpass.getpass("Nhập chuỗi mật khẩu được sử dụng để bảo vệ khóa riêng tư: ")

    # Đọc khóa từ file PEM
    with open(priv_path, 'rb') as f:
        key = RSA.import_key(f.read(), passphrase=passphrase)
    with open(pub_path, 'rb') as f:
        public_key = RSA.import_key(f.read())
    return key, public_key

def encrypt_file():
    '''
    1. Sinh khóa đối xứng AES - 128 (Note: khi xuất hiện dòng chữ "Nhap khoa AES 16 bytes: " thì nhấn Enter để tự động sinh khóa AES-128).
    2. Mã hóa file bằng AES-CBC với khóa AES đã sinh.
    3. Mã hóa khóa đối xứng AES - 128 bằng RSA-OAEP với khóa công khai.
    '''

    print("Note: khi xuất hiện dòng chữ (Nhap khoa AES 16 bytes: ) thì nhấn Enter để tự động sinh khóa AES-128")
    key_AES, output_file, input_file = encrypt_file_AES_CBC(del_input_file = 0)

    rsa_cipher = RSA_OAEP_Cipher(init_key = 0)
    cipher_key_AES = rsa_cipher.encrypt(key_AES, rsa_cipher.public_key)

    output_file = output_file + ".enc_key_rsa"
    with open(output_file, 'wb') as f:
        f.write(cipher_key_AES)
    print(f"Khóa AES - 128 đã được mã hóa bằng RSA - OAEP và lưu tại: {output_file}")
    print("**********************************************************************")
    os.remove(input_file)
    print(f"File goc {input_file} da duoc xoa.")
    print("**********************************************************************")
    return

def decrypt_file():
    '''
    1. Dùng RSA - OAEP và khóa riêng để giải mã AES - 128 key.
    2. Dùng AES - 128 key để giải mã file.
    '''

    # 1. Dùng RSA - OAEP và khóa riêng để giải mã AES - 128 key.
    rsa_cipher = RSA_OAEP_Cipher(init_key=0)

    input_file_AES = r"{}".format(input("Nhập đường dẫn khóa AES - 128 key: "))
    with open(input_file_AES, 'rb') as f:
        enc_key_rsa = f.read()
    key_AES = rsa_cipher.decrypt(enc_key_rsa)
    # 2. Dùng AES - 128 key để giải mã file.
    decrypt_file_AES_CBC(key_AES)

    choice = input(f"Ban co muon xoa file {input_file_AES} khong? (y/n): ").strip().lower()
    while choice not in ('y', 'n'):
        choice = input("Khong hop le. Vui long nhap 'y' hoac 'n': ").strip().lower()
    if choice == 'y':
        os.remove(input_file_AES)
        print("**********************************************************************")
        print(f"File ma hoa {input_file_AES} da duoc xoa.")
        print("**********************************************************************")
    else:
        print("**********************************************************************")
        print(f"Khong xoa file {input_file_AES}.")
        print("**********************************************************************")

if __name__ == '__main__':
    # export_keys_RSA_OAEP()

    # encrypt_file()

    # decrypt_file()

    key = RSA.generate(2048)
    public_key = key.publickey()
    print(f"\nn: {key.n}")
    print(f"\nd: {key.d}")
    print(f"\ne: {key.e}")
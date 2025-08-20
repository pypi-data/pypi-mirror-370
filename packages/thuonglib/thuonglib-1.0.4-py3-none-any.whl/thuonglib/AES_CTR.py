from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import getpass
from thuonglib.utilities import bytes_distance_bytes

class AESCipherCTR:
    def __init__(self, key: bytes = None, key_size: int = 128, is_Confirm = True):
        """
        Khởi tạo đối tượng AES-CTR.
        - key: khóa đã cho (bytes). Nếu None, tự sinh khóa ngẫu nhiên.
        - key_size: kích thước khóa (128, 192, 256 bit).
        """
        self.is_Confirm = is_Confirm
        if key:
            self.key = key
        else:
            self.key = self.__set_key()
        self.nonce_size = 8
        self.nonce = None

    def __set_key(self) -> bytes | None:
        key = getpass.getpass("Nhap khoa AES 16 bytes: ").encode('utf-8')
        if self.is_Confirm:
            key_confirm = getpass.getpass("Xac nhan khoa AES 16 bytes: ").encode('utf-8')
            key_confirm2 = getpass.getpass("Xac nhan lai khoa AES 16 bytes: ").encode('utf-8')
            while key != key_confirm or key != key_confirm2:
                key = getpass.getpass("Nhap khoa AES 16 bytes: ").encode('utf-8')
                key_confirm = getpass.getpass("Xac nhan khoa AES 16 bytes: ").encode('utf-8')
                key_confirm2 = getpass.getpass("Xac nhan lai khoa AES 16 bytes: ").encode('utf-8')
            del key_confirm, key_confirm2
        # Điều chỉnh độ dài của key để đảm bảo đủ 16 bytes
        if len(key) < 16:
            key = (key * (16 // len(key) + 1))[:16]  # Lặp lại chuỗi và cắt cho đủ 16 bytes
        elif len(key) > 16:
            key = key[:16]  # Cắt chuỗi cho đủ 16 bytes
        return key
    
    def init_nonce(self) -> bytes:
        self.nonce = get_random_bytes(self.nonce_size)
        if not os.path.exists(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin'):
            print("Tao file nonce.bin de luu nonce...")
            open(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin', "w").close()
            print("File nonce.bin da duoc tao thanh cong.")
        with open(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin', 'rb') as f:
            existing_nonce = f.read()
        while self.nonce in existing_nonce:
            print("Nonce đã tồn tại, tạo nonce mới...")
            self.nonce = get_random_bytes(self.nonce_size)
        while not bytes_distance_bytes(self.nonce, self.key[0:8]) >= 28:
            print("Khoảng cách giữa nonce và key quá lớn, tạo nonce mới...")
            self.init_nonce()
        with open(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin', 'ab') as f:
            f.write(self.nonce)
        del existing_nonce
        return self.nonce

    def encrypt(self, data: bytes) -> bytes:
        """
        Mã hóa dữ liệu (bytes) với AES-CTR.
        Trả về chuỗi bytes: nonce + ciphertext.
        """
        self.nonce = self.init_nonce()
        cipher = AES.new(self.key, AES.MODE_CTR, nonce = self.nonce)
        ciphertext = cipher.encrypt(data)
        return self.nonce + ciphertext

    def decrypt(self, token: bytes) -> bytes:
        """
        Giải mã chuỗi (nonce + ciphertext) và trả về plaintext bytes.
        """
        nonce = token[:self.nonce_size]
        ciphertext = token[self.nonce_size:]
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(ciphertext)
    
def encrypt_file_AES_CTR() -> None:
    input_file = r"{}".format(input("Nhap duong dan file can ma hoa: "))
    aes = AESCipherCTR()

    with open(input_file, 'rb') as f:
        data = f.read()
    
    cipher_data = aes.encrypt(data)

    output_file = input_file + ".enc"
    
    with open(output_file, 'wb') as f:
        f.write(cipher_data)

    print("**********************************************************************")
    print(f"File da duoc ma hoa va luu tai: {output_file}")
    print("**********************************************************************")

    os.remove(input_file)
    print(f"File goc {input_file} da duoc xoa.")
    print("**********************************************************************")
    return

def decrypt_file_AES_CTR(key_AES: bytes = None) -> None:
    input_file = r"{}".format(input("Nhap duong dan file can giai ma: "))
    if key_AES:
        aes = AESCipherCTR(key=key_AES)
    else:
        aes = AESCipherCTR(is_Confirm = False)

    with open(input_file, 'rb') as f:
        cipher_data = f.read()

    decrypted_data = aes.decrypt(cipher_data)

    output_file = input_file[:-4]  # Loại bỏ phần mở rộng .enc

    with open(output_file, 'wb') as f:
        f.write(decrypted_data)

    print("**********************************************************************")
    print(f"File da duoc giai ma va luu tai: {output_file}")
    print("**********************************************************************")

    choice = input("Ban co muon xoa file ma hoa khong? (y/n): ").strip().lower()
    while choice not in ('y', 'n'):
        choice = input("Khong hop le. Vui long nhap 'y' hoac 'n': ").strip().lower()
    if choice == 'y':
        os.remove(input_file)
        print("**********************************************************************")
        print(f"File ma hoa {input_file} da duoc xoa.")
        print("**********************************************************************")
    else:
        print("**********************************************************************")
        print("Khong xoa file ma hoa.")
        print("**********************************************************************")

if __name__ == '__main__':
    aes = AESCipherCTR()
    message = "Đây là thông điệp bí mật với AES-CTR!".encode('utf-8')

    encrypted = aes.encrypt(message)
    print(f"Encrypted (nonce+ciphertext bytes): {encrypted}")

    decrypted = aes.decrypt(encrypted)
    print(f"Decrypted: {decrypted.decode('utf-8')}")
from Crypto.Cipher import AES
from Crypto.Random  import get_random_bytes
import os
import getpass
from thuonglib.utilities import bytes_distance_bytes

class AESGCMCipher:
    def __init__(self, key_AES: bytes = None, is_Confirm = True):
        """
        - Nếu key None, tự sinh ngẫu nhiên 256-bit (32 byte).
        - Nếu truyền vào, key phải là 16/24/32 byte.
        """
        self.is_Confirm = is_Confirm
        if key_AES:
            self.key = key_AES
        else:
            self.key = self.__set_key() or get_random_bytes(32)
        # GCM mặc định sử dụng nonce 12 byte
        self.nonce_size = 12
        self.tag_size   = 16
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
        while not bytes_distance_bytes(self.nonce, self.key[0:12]) >= 28:
            print("Khoảng cách giữa nonce và key quá lớn, tạo nonce mới...")
            self.init_nonce()
        with open(r'D:\Duan\20publish_pypi\thuongcli\nonce.bin', 'ab') as f:
            f.write(self.nonce)
        del existing_nonce
        return self.nonce

    def encrypt(self, data: bytes) -> bytes:
        """
        Mã hoá toàn bộ data, trả về bytes:
        [nonce(12)][tag(16)][ciphertext]
        """
        cipher = AES.new(self.key, AES.MODE_GCM, nonce = self.init_nonce())
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return self.nonce + tag + ciphertext

    def decrypt(self, cipher_data: bytes) -> bytes:
        """
        cipher_data định dạng:
        [nonce(12)][tag(16)][ciphertext]
        """
        nonce = cipher_data[:self.nonce_size]
        tag = cipher_data[self.nonce_size:self.nonce_size + self.tag_size]
        cipher_text = cipher_data[self.nonce_size + self.tag_size:]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce = nonce)
        plaintext = cipher.decrypt_and_verify(cipher_text, tag)
        return plaintext
    
def encrypt_file_AES_GCM() -> None:
    input_file = r"{}".format(input("Nhap duong dan file can ma hoa: "))
    aes = AESGCMCipher()

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

def decrypt_file_AES_GCM(key_AES: bytes = None, input_file: str = None) -> None:
    if not input_file:
        input_file = r"{}".format(input("Nhap duong dan file can giai ma: "))
    if key_AES:
        aes = AESGCMCipher(key_AES=key_AES)
    else:
        aes = AESGCMCipher(is_Confirm = False)

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
    return
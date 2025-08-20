from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os
import getpass

class AESCipherCBC:
    def __init__(self, key_AES: bytes = None, type_enc_return: str = 'bytes', type_decrypt_arg: str = 'bytes', is_Confirm = True):
        # Nếu không có key truyền vào, tự sinh khóa AES-256
        # Hỗ trợ 128 bit (16 byte), 192 bit (24 byte) và 256 bit (32 byte).
        self.is_Confirm = is_Confirm
        if key_AES:
            self.key = key_AES
        else:
            self.key = self.__set_key() or get_random_bytes(16)
        self.bs = AES.block_size  # 16 bytes
        self.__type_enc_return = type_enc_return  # Kiểu trả về khi mã hóa
        self.__type_decrypt_arg = type_decrypt_arg  # Kiểu dữ liệu đầu vào khi giải mã
    
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
        if len(key) == 0:
            return None
        # Điều chỉnh độ dài của key để đảm bảo đủ 16 bytes
        if len(key) < 16:
            key = (key * (16 // len(key) + 1))[:16]  # Lặp lại chuỗi và cắt cho đủ 16 bytes
        elif len(key) > 16:
            key = key[:16]  # Cắt chuỗi cho đủ 16 bytes
        return key

    def encrypt(self, data: bytes) -> bytes | str:
        """
        Nếu chọn 'bytes', trả về bytes: IV + ciphertext
        Nếu chọn 'str', trả về chuỗi Base64: IV + ciphertext
        """

        iv = get_random_bytes(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded = pad(data, self.bs)
        ct = cipher.encrypt(padded)
        if self.__type_enc_return == 'bytes':
            # Trả về bytes: IV + ciphertext
            return iv + ct
        # Trả về chuỗi Base64: IV + ciphertext
        return base64.b64encode(iv + ct).decode('utf-8')

    def decrypt(self, token: bytes | str) -> bytes:
        """
        Nếu token là bytes, giải mã trực tiếp
        Nếu token là str (chuỗi Base64), giải mã sau khi giải mã Base64
        """
        if self.__type_decrypt_arg != "bytes":
            # Giải mã chuỗi Base64
            raw = base64.b64decode(token)
        raw = token
        iv = raw[:self.bs]
        ct = raw[self.bs:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded = cipher.decrypt(ct)
        return unpad(padded, self.bs)
    
    @classmethod
    def load_key(cls, key_bytes: bytes):
        """Tạo instance từ key đã lưu."""
        return cls(key=key_bytes)
    
def encrypt_file_AES_CBC(del_input_file = 1) -> None:
    input_file = r"{}".format(input("Nhap duong dan file can ma hoa: "))
    aes = AESCipherCBC()

    with open(input_file, 'rb') as f:
        data = f.read()
    
    cipher_data = aes.encrypt(data)

    output_file = input_file + ".enc"
    
    with open(output_file, 'wb') as f:
        f.write(cipher_data)

    print("**********************************************************************")
    print(f"File da duoc ma hoa va luu tai: {output_file}")
    print("**********************************************************************")

    if del_input_file:
        os.remove(input_file)
        print(f"File goc {input_file} da duoc xoa.")
        print("**********************************************************************")
        return None
    return aes.key, output_file, input_file

def decrypt_file_AES_CBC(key_AES: bytes = None) -> None:
    input_file = r"{}".format(input("Nhap duong dan file can giai ma: "))
    if key_AES:
        aes = AESCipherCBC(key_AES=key_AES)
    else:
        aes = AESCipherCBC(is_Confirm = False)

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

# Ví dụ sử dụng
if __name__ == '__main__':
    
    aes = AESCipherCBC()
    message = "Đây là thông điệp cần mã hóa với AES-CBC!".encode('utf-8')

    # Mã hóa
    encrypted = aes.encrypt(message)
    print(f"Encrypted: {encrypted}")

    # Giải mã
    decrypted = aes.decrypt(encrypted)
    print(f"Decrypted: {decrypted.decode('utf-8')}")
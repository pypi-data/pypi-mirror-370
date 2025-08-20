import base64
import os
import sys

def xor_encrypt(plaintext: bytes, key: bytes) -> bytes:
        return bytes(p ^ key[i % len(key)] for i, p in enumerate(plaintext))
    
def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
# cùng phép XOR, vì tính chất đảo ngược
    return xor_encrypt(ciphertext, key)

def encrypt_file():
    print("\nĐang chạy thuật toán my_XOR.")
    input_file = r"{}".format(input("Nhap duong dan file can ma hoa: "))
    key = input("Nhap khoa ma hoa data: ").encode('utf-8')

    with open(input_file, 'rb') as f:
        data = f.read()
    
    cipher_data_level1 = xor_encrypt(data, key)
    cipher_data_level2 = base64.b64encode(cipher_data_level1)

    output_file = input_file + ".enc"
    
    with open(output_file, 'wb') as f:
        f.write(cipher_data_level2)

    print("**********************************************************************")
    print(f"File da duoc ma hoa va luu tai: {output_file}")
    print("**********************************************************************")

    os.remove(input_file)
    print(f"File goc {input_file} da duoc xoa.")
    print("**********************************************************************")
    return output_file

def decrypt_file() -> None:
    print("\nĐang chạy thuật toán my_XOR.")
    input_file = r"{}".format(input("Nhap duong dan file can giai ma: "))
    key = input("Nhap khoa giai ma data: ").encode('utf-8')

    with open(input_file, 'rb') as f:
        cipher_data_level2 = f.read()

    cipher_data_level1 = base64.b64decode(cipher_data_level2)
    decrypted_data = xor_decrypt(cipher_data_level1, key)

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
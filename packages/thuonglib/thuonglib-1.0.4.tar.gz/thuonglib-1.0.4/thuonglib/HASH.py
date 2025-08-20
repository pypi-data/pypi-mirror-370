from Crypto.Hash import SHA256, SHA512, SHA3_256, SHA3_512
from thuonglib.utilities import cipher_utilities
from thuonglib.AES_GCM import AESGCMCipher, encrypt_file_AES_GCM, decrypt_file_AES_GCM
import os

def my_hash(data: bytes | str = None, file_write = 0) -> str:
    """
    Tạo giá trị băm SHA-256 từ dữ liệu đầu vào.
    Nếu dữ liệu là chuỗi, nó sẽ được mã hóa utf-8 trước khi băm.
    Nếu data = None, phải nhập đường dẫn đến file cần băm.

    :param data: Dữ liệu đầu vào (bytes hoặc str hoặc None)
    :return: Giá trị băm SHA-256 dưới dạng chuỗi hex, chứa 64 ký tự hex (32 bytes).
    """
    if data is None or data == '':
        input_file = r"{}".format(input("Nhập đường dẫn file cần hash: "))
        with open(input_file, 'rb') as file:
            data = file.read()
        hash_value = cipher_utilities.SHA_256(data)
        print("**********************************************************************")
        print(f"Giá trị băm SHA-256 của file {input_file} là: {hash_value}")
        print("**********************************************************************")
        if file_write:
            output_file = input_file + ".sha256"
            with open(output_file, 'w') as f:
                f.write(hash_value)
            print(f"Giá trị băm đã được lưu vào {output_file}")
        encrypt_file_AES_GCM()
        return hash_value
    else:
        hash_value = cipher_utilities.SHA_256(data)
        print("**********************************************************************")
        print(f"Giá trị băm SHA-256 của dữ liệu được tạo với hàm my_hash() là: {hash_value}")
        print("**********************************************************************")
        if 0:
            output_file = r"{}".format(input("Nhập đường dẫn file cần lưu giá trị băm: "))
            file_name = r'{}'.format(input("Nhập tên file lưu giá trị băm (không cần đuôi): "))
            output_file += file_name + ".sha256"
            with open(output_file, 'w') as f:
                f.write(hash_value)
            print(f"Giá trị băm đã được lưu vào {output_file}")
        return hash_value
    
def sha256(data: bytes | str = None, file_write = 1) -> str:
    """
    Tạo giá trị băm SHA-256 từ dữ liệu đầu vào.
    Nếu dữ liệu là chuỗi, nó sẽ được mã hóa utf-8 trước khi băm.
    Nếu data = None, phải nhập đường dẫn đến file cần băm.
    
    :param data: Dữ liệu đầu vào (bytes hoặc str hoặc None)
    :return: Giá trị băm SHA-256 dưới dạng chuỗi hex, chứa 64 ký tự hex (32 bytes).
    """
    if data is None or data == '':
        input_file = r"{}".format(input("Nhập đường dẫn file cần hash: "))
        with open(input_file, 'rb') as file:
            data = file.read()
        sha256_hash = SHA256.new()
        sha256_hash.update(data)
        sha256_digest = sha256_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA-256 của file {input_file} là: {sha256_digest}")
        print("**********************************************************************")
        # print(f"giá trị hash được tạo từ hàm my_hash() và sha256() là {'bằng nhau' if sha256_digest == my_hash(data, file_write) else 'khác nhau'}")
        if file_write:
            output_file = input_file + ".sha256"
            with open(output_file, 'w') as f:
                f.write(sha256_digest)
            print(f"Giá trị băm đã được lưu vào {output_file}")
        encrypt_file_AES_GCM()
        return sha256_digest
    else:
        # Nếu data là chuỗi, mã hóa nó thành bytes
        sha256_hash = SHA256.new()
        sha256_hash.update(data.encode('utf-8') if isinstance(data, str) else data)
        sha256_digest = sha256_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA-256 của data là: {sha256_digest}")
        print("**********************************************************************")
        print(f"giá trị hash được tạo từ hàm my_hash() và sha256() là {'bằng nhau' if sha256_digest == my_hash(data, file_write) else 'khác nhau'}")
        return sha256_digest
    
def sha512(data: bytes | str = None, file_write = 1) -> str:
    """
    Tạo giá trị băm SHA-512 từ dữ liệu đầu vào.
    Nếu dữ liệu là chuỗi, nó sẽ được mã hóa utf-8 trước khi băm.
    Nếu data = None, phải nhập đường dẫn đến file cần băm.

    :param data: Dữ liệu đầu vào (bytes hoặc str hoặc None)
    :return: Giá trị băm SHA-512 dưới dạng chuỗi hex (128 ký tự hex, 64 bytes).
    """
    if data is None or data == '':
        input_file = r"{}".format(input("Nhập đường dẫn file cần hash: "))
        with open(input_file, 'rb') as file:
            data = file.read()
        sha512_hash = SHA512.new()
        sha512_hash.update(data)
        sha512_digest = sha512_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA-512 của file {input_file} là: {sha512_digest}")
        print("**********************************************************************")
        if file_write:
            output_file = input_file + ".sha512"
            with open(output_file, 'w') as f:
                f.write(sha512_digest)
            print(f"Giá trị băm đã được lưu vào {output_file}")
        encrypt_file_AES_GCM()
        return sha512_digest
    else:
        sha512_hash = SHA512.new()
        sha512_hash.update(data.encode('utf-8') if isinstance(data, str) else data)
        sha512_digest = sha512_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA-512 của data là: {sha512_digest}")
        print("**********************************************************************")
        return sha512_digest
    
def sha3_256(data: bytes | str = None, file_write = 1) -> str:
    """
    Tạo giá trị băm SHA3-256 từ dữ liệu đầu vào.
    Nếu dữ liệu là chuỗi, nó sẽ được mã hóa utf-8 trước khi băm.
    Nếu data = None, phải nhập đường dẫn đến file cần băm.

    :param data: Dữ liệu đầu vào (bytes hoặc str hoặc None)
    :return: Giá trị băm SHA3-256 dưới dạng chuỗi hex (64 ký tự hex, 32 bytes).
    """
    if data is None or data == '':
        input_file = r"{}".format(input("Nhập đường dẫn file cần hash: "))
        with open(input_file, 'rb') as file:
            data = file.read()
        sha3_256_hash = SHA3_256.new()
        sha3_256_hash.update(data)
        sha3_256_digest = sha3_256_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA3-256 của file {input_file} là: {sha3_256_digest}")
        print("**********************************************************************")
        if file_write:
            output_file = input_file + ".sha3_256"
            with open(output_file, 'w') as f:
                f.write(sha3_256_digest)
            print(f"Giá trị băm đã được lưu vào {output_file}")
        encrypt_file_AES_GCM()
        return sha3_256_digest
    else:
        sha3_256_hash = SHA3_256.new()
        sha3_256_hash.update(data.encode('utf-8') if isinstance(data, str) else data)
        sha3_256_digest = sha3_256_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA3-256 của data là: {sha3_256_digest}")
        print("**********************************************************************")
        return sha3_256_digest

def sha3_512(data: bytes | str = None, file_write = 1) -> str:
    """
    Tạo giá trị băm SHA3-512 từ dữ liệu đầu vào.
    Nếu dữ liệu là chuỗi, nó sẽ được mã hóa utf-8 trước khi băm.
    Nếu data = None, phải nhập đường dẫn đến file cần băm.

    :param data: Dữ liệu đầu vào (bytes hoặc str hoặc None)
    :return: Giá trị băm SHA3-512 dưới dạng chuỗi hex (128 ký tự hex, 64 bytes).
    """
    if data is None or data == '':
        input_file = r"{}".format(input("Nhập đường dẫn file cần hash: "))
        with open(input_file, 'rb') as file:
            data = file.read()
        sha3_512_hash = SHA3_512.new()
        sha3_512_hash.update(data)
        sha3_512_digest = sha3_512_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA3-512 của file {input_file} là: {sha3_512_digest}")
        print("**********************************************************************")
        if file_write:
            output_file = input_file + ".sha3_512"
            with open(output_file, 'w') as f:
                f.write(sha3_512_digest)
            print(f"Giá trị băm đã được lưu vào {output_file}")
        encrypt_file_AES_GCM()
        return sha3_512_digest
    else:
        sha3_512_hash = SHA3_512.new()
        sha3_512_hash.update(data.encode('utf-8') if isinstance(data, str) else data)
        sha3_512_digest = sha3_512_hash.hexdigest()
        print("**********************************************************************")
        print(f"Giá trị băm SHA3-512 của data là: {sha3_512_digest}")
        print("**********************************************************************")
        return sha3_512_digest
    
class Hash:
    """
    Class để tính toán giá trị băm của file.
    Sử dụng các thuật toán SHA-256, SHA-512, SHA3-256, SHA3-512.
    """
    @staticmethod
    def C_sha256(data: bytes) -> str:
        """
        Tính toán giá trị băm SHA-256 của dữ liệu.
        
        :param data: Dữ liệu đầu vào (bytes).
        :return: Giá trị băm SHA-256 dưới dạng chuỗi hex.
        """
        sha256_hash = SHA256.new()
        sha256_hash.update(data)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def C_sha512(data: bytes) -> str:
        """
        Tính toán giá trị băm SHA-512 của dữ liệu.
        
        :param data: Dữ liệu đầu vào (bytes).
        :return: Giá trị băm SHA-512 dưới dạng chuỗi hex.
        """
        sha512_hash = SHA512.new()
        sha512_hash.update(data)
        return sha512_hash.hexdigest()
    
    @staticmethod
    def C_sha3_256(data: bytes) -> str:
        """
        Tính toán giá trị băm SHA3-256 của dữ liệu.
        
        :param data: Dữ liệu đầu vào (bytes).
        :return: Giá trị băm SHA3-256 dưới dạng chuỗi hex.
        """
        sha3_256_hash = SHA3_256.new()
        sha3_256_hash.update(data)
        return sha3_256_hash.hexdigest()
    
    @staticmethod
    def C_sha3_512(data: bytes) -> str:
        """
        Tính toán giá trị băm SHA3-512 của dữ liệu.
        
        :param data: Dữ liệu đầu vào (bytes).
        :return: Giá trị băm SHA3-512 dưới dạng chuỗi hex.
        """
        sha3_512_hash = SHA3_512.new()
        sha3_512_hash.update(data)
        return sha3_512_hash.hexdigest()
    
def check_hash() -> bool:
    """
    Kiểm tra giá trị băm của file so với giá trị băm đã cho (được nhập từ bàn phím hoặc đọc từ file).

    :return: True nếu giá trị băm khớp, False nếu không.
    """

    # Danh sách thuật toán băm
    algorithms = ['sha256', 'sha512', 'sha3_256', 'sha3_512']
    
    # Hiển thị và chọn thuật toán băm
    print("Chọn thuật toán băm:")
    for i, algo in enumerate(algorithms, 1):
        print(f"{i}. {algo.upper()}")
    choice = int(input("Nhập số thứ tự của thuật toán: "))
    while choice not in [1, 2, 3, 4]:
        print("Lựa chọn không hợp lệ.")
        choice = int(input("Nhập số thứ tự của thuật toán (1-4): "))
    hash_algorithm = algorithms[choice - 1]
    print(f"Thuật toán băm đã chọn: {hash_algorithm.upper()}")
    # Nhập đường dẫn file cần xác nhận có bị thay đổi hay không
    file_path = input("Nhập đường dẫn đến file cần xác nhận có bị thay đổi hay không: ")
    if not os.path.exists(file_path):
        print("File không tồn tại.")
        return
    
    # Chọn cách nhập mã hash
    print("\nChọn cách nhập mã hash:")
    print("1. Nhập từ bàn phím")
    print("2. Đọc từ file mã hóa hash .enc")
    while (hash_choice := int(input("Nhập lựa chọn (1 hoặc 2): "))) not in [1, 2]:
        print("Lựa chọn không hợp lệ. Vui lòng nhập 1 hoặc 2.")
    print(f"Bạn đã chọn: {'Nhập từ bàn phím' if hash_choice == 1 else 'Đọc từ file mã hóa hash .enc'}")
    if hash_choice == 1:
        provided_hash = input("Nhập mã hash: ").strip()
    else:
        try:
            file_hash_enc = r"{}".format(input("Nhập đường dẫn file mã hóa hash .enc: "))
            decrypt_file_AES_GCM(input_file=file_hash_enc)
            with open(file_hash_enc[:-4], 'r') as f:
                provided_hash = f.read().strip()
            os.remove(file_hash_enc[:-4])  # Xóa file giải mã tạm thời
        except:
            print("File mã hóa hash .enc không tồn tại hoặc lỗi giải mã file hash.")
            return
        
    # Tính toán mã hash của file
    hash_func = getattr(Hash, f'C_{hash_algorithm}')
    with open(file_path, 'rb') as f:
        file_data = f.read()
        calculated_hash = hash_func(file_data)
    print(f"\nMã hash đã tính toán: {calculated_hash}")
    print(f"Mã hash đã cung cấp: {provided_hash}")
    # So sánh mã hash và hiển thị kết quả
    if calculated_hash == provided_hash:
        print(f"Kết quả: File {file_path} không bị thay đổi.")
        return True
    else:
        print(f"Kết quả: File {file_path} đã bị thay đổi.")
        return False

if __name__ == "__main__":
    import sys
    sys.path.pop(0)

    data = 'Hello, World!'
    my_hash(data, file_write=1)
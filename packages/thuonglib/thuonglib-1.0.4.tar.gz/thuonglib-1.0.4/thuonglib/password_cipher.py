def p_cipher():
    import os
    import getpass
    import base64

    def xor_encrypt(plaintext: bytes, key: bytes) -> bytes:
        return bytes(p ^ key[i % len(key)] for i, p in enumerate(plaintext))
    
    def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    # cùng phép XOR, vì tính chất đảo ngược
        return xor_encrypt(ciphertext, key)

    FLAG_ENCRYPT = 0b0001
    FLAG_DECRYPT = 0b0010
    OPTION = 0b0000

    print("Chon 1 trong 2:")
    print("M. Ma hoa")
    print("G. Giai ma")
    choice = input("Nhap lua chon cua ban: ").lower()

    while choice not in ['m', 'g']:
            choice = input("Nhap M de ma hoa, G de giai ma: ").lower()
    if choice == 'm':
        OPTION |= FLAG_ENCRYPT
    else:
        OPTION |= FLAG_DECRYPT
    # Thuc hien ma hoa ********************************************************************************
    if OPTION & FLAG_ENCRYPT:

        key = getpass.getpass("Nhap khoa mat khau: ").encode('utf-8')
        key_confirm = getpass.getpass("Xác nhận chuỗi mật khẩu: ").encode('utf-8')
        key_confirm2 = getpass.getpass("Xác nhận lại chuỗi mật khẩu: ").encode('utf-8')

        while key != key_confirm or key != key_confirm2:
            print("Chuỗi mật khẩu không khớp, vui lòng thử lại.")
            key = getpass.getpass("NNhap khoa mat khau: ").encode('utf-8')
            key_confirm = getpass.getpass("Xác nhận chuỗi mật khẩu: ").encode('utf-8')
            key_confirm2 = getpass.getpass("Xác nhận lại chuỗi mật khẩu: ").encode('utf-8')

        del key_confirm, key_confirm2

        plaintext = input("Nhap van ban can ma hoa: ").encode('utf-8')

        add_note = input("Nhap them ghi chu cho password: ")

        ciphertext = xor_encrypt(plaintext, key)
        ciphertext_base64 = base64.b64encode(ciphertext)
        ciphertext_base64_string = ciphertext_base64.decode('utf-8')
        print(f"Van ban da ma hoa (Base64): {ciphertext_base64.decode('utf-8')}")

        # Đọc đường dẫn từ dòng số 2 trong tệp config.txt
        config_file = "config.txt"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    password_dir = lines[1].strip()  # Lấy dòng số 2 và loại bỏ khoảng trắng
                else:
                    print("Tệp config.txt không có đủ dòng.")
                    return
        else:
            print(f"Tệp cấu hình '{config_file}' không tồn tại.")
            return
        # Kiểm tra và tạo thư mục nếu chưa tồn tại
        if not os.path.exists(password_dir):
            os.makedirs(password_dir)
            print(f"Đã tạo thư mục: {password_dir}")
        else:
            print(f"Thư mục đã tồn tại: {password_dir}")
        # Sử dụng đường dẫn để lưu tệp
        file_path = os.path.join(password_dir, "ciphertext.txt")
        file_path_note = os.path.join(password_dir, "ciphertext_note.txt")
        with open(file_path, "a") as f:
            f.write(f"{ciphertext_base64_string}\n")

        print(f"Van ban da duoc ghi vao tep '{file_path}'.")
        with open(file_path_note, "a") as f:
            f.write(f"{add_note}\n")
        print(f"Ghi chu da duoc ghi vao tep '{file_path_note}'.")

    # Ket thuc ma hoa *******************************************************************************
    # Thuc hien giai ma ****************************************************************************

    if OPTION & FLAG_DECRYPT:
        key = getpass.getpass("Nhap khoa mat khau: ").encode('utf-8')
        line_number = input("Nhap so dong can giai ma: ")
        try:
            line_number = int(line_number)
        except ValueError:
            print("So dong khong hop le. Vui long nhap mot so nguyen.")
            return
        # Đọc đường dẫn từ dòng số 2 trong tệp config.txt
        config_file = "config.txt"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    password_dir = lines[1].strip()  # Lấy dòng số 2 và loại bỏ khoảng trắng
                else:
                    print("Tệp config.txt không có đủ dòng.")
                    return
        else:
            print(f"Tệp cấu hình '{config_file}' không tồn tại.")
            return
        
        # Sử dụng đường dẫn để đọc tệp
        file_path = os.path.join(password_dir, "ciphertext.txt")
        file_path_note = os.path.join(password_dir, "ciphertext_note.txt")
        try:
            with open(file_path, "rb") as f:
                lines = f.readlines()
            if line_number <= 0 or line_number > len(lines):
                print("So dong vuot qua pham vi cua tep.")
                return
            ciphertext = lines[line_number - 1].strip()
            ciphertext = base64.b64decode(ciphertext)
            plaintext = xor_decrypt(ciphertext, key)
            print(f"VAN BAN DA GIAI MA: {plaintext.decode('utf-8')}")
        except FileNotFoundError:
            print(f"Tep '{file_path}' khong ton tai.")
        except Exception as e:
            print(f"Loi khi doc tep: {e}")

    # ket thuc giai ma ****************************************************************************
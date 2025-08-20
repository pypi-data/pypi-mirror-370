import base64
import os

def divide_file():
    input_file = r"{}".format(input("Nhap duong dan file can chia: "))
    chunk_size = int(input("Nhap kich thuoc moi phan (byte, mac dinh 12MB): ") or 12 * 1024 * 1024)
    print(f"Kich thuoc moi phan: {chunk_size / (1024 * 1024):.2f} MB")
    chunks = []
    with open(input_file, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    
    print("*********************************************************************")
    for i, chunk in enumerate(chunks):
        chunk_input_file = f"{input_file}.part_{i + 1}"
        with open(chunk_input_file, 'wb') as chunk_file:
            chunk_file.write(chunk)
        print(f"Da luu phan {i + 1} tai: {chunk_input_file}")
    print("Da chia xong cac phan cua file.")
    print("*********************************************************************")
    os.remove(input_file)
    print(f"Da xoa file goc: {input_file}")
    print("**********************************************************************")

def merge_file():
    input_file = r"{}".format(input("Nhap duong dan file can ghep: "))
    input_file = input_file[:-7]
    chunks = []
    
    i = 1
    while True:
        chunk_input_file = input_file + f".part_{i}"
        if not os.path.exists(chunk_input_file):
            break
        else:
            with open(chunk_input_file, 'rb') as chunk_file:
                chunks.append(chunk_file.read())
            os.remove(chunk_input_file)
            print(f"Da xoa phan {i} tai: {chunk_input_file}")
            i += 1
    
    with open(input_file, 'wb') as output:
        for chunk in chunks:
            output.write(chunk)
    
    print(f"Da ghep cac phan thanh: {input_file}")
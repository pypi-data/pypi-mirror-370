def d_folder(path_folder):
    import os
    if path_folder and os.path.exists(path_folder):
        for root, dirs, files in os.walk(path_folder, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete file {file_path}: {e}")
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    # Only remove empty directories
                    os.rmdir(dir_path)
                    print(f"Deleted directory: {dir_path}")
                except Exception as e:
                    print(f"Failed to clean {path_folder}: {e}")

def clean_files_temp():
    import os
    from thuonglib.recycleBin import empty_recycle_bin
    temp_folder = os.path.join(os.getenv('SystemRoot'), 'TEMP')
    print("-" * 50)
    print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
    print("Nhan y de xoa, nhan n de bo qua.")
    user_input = input("Ban co muon xoa khong? (y/n): ").lower()
    while user_input not in ['y', 'n']:
        user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
    if user_input == 'y':
        d_folder(temp_folder)
    else:
        print("Bo qua viec xoa tep tam thoi.")
    print("-" * 50)
    
    temp_folder = os.getenv("TEMP")
    print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
    print("Nhan y de xoa, nhan n de bo qua.")
    user_input = input("Ban co muon xoa khong? (y/n): ").lower()
    while user_input not in ['y', 'n']:
        user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
    if user_input == 'y':
        d_folder(temp_folder)
    else:
        print("Bo qua viec xoa tep tam thoi.")
    print("-" * 50)
    
    temp_folder = os.getenv("TMP")
    print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
    print("Nhan y de xoa, nhan n de bo qua.")
    user_input = input("Ban co muon xoa khong? (y/n): ").lower()
    while user_input not in ['y', 'n']:
        user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
    if user_input == 'y':
        d_folder(temp_folder)
    else:
        print("Bo qua viec xoa tep tam thoi.")
    print("-" * 50)

    print(f"Xac nhan xoa thung rac Recycle Bin")
    print("Nhan y de xoa, nhan n de bo qua.")
    user_input = input("Ban co muon xoa khong? (y/n): ").lower()
    while user_input not in ['y', 'n']:
        user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
    if user_input == 'y':
        empty_recycle_bin()
    else:
        print("Bo qua viec xoa thung rac Recycle Bin.")
    print("-" * 50)

def del_dir_downloads():
    import os
    temp_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    print("-" * 50)
    print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
    print("Nhan y de xoa, nhan n de bo qua.")
    user_input = input("Ban co muon xoa khong? (y/n): ").lower()
    while user_input not in ['y', 'n']:
        user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
    if user_input == 'y':
        d_folder(temp_folder)
    else:
        print("Bo qua viec xoa tep tam thoi.")
    print("-" * 50)
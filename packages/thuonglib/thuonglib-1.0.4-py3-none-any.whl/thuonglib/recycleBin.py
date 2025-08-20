import ctypes
from ctypes import wintypes

def empty_recycle_bin():
    """
    Hàm xoá sạch Recycle Bin trên Windows.
    Sử dụng hàm SHEmptyRecycleBinW từ thư viện shell32.dll.
    """
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)

    # Định nghĩa các cờ cho SHEmptyRecycleBinW
    SHERB_NOCONFIRMATION = 0x00000001
    SHERB_NOPROGRESSUI   = 0x00000002
    SHERB_NOSOUND        = 0x00000004

    # Gọi hàm SHEmptyRecycleBinW
    result = shell32.SHEmptyRecycleBinW(
        None,  # hwnd (không cần giao diện)
        None,  # pszRootPath (None = xoá ở tất cả ổ)
        SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
    )

    if result == 0:
        print("Da xoa sach Recycle Bin.")
    return

if __name__ == "__main__":
    empty_recycle_bin()
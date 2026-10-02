# === keygen.py ===
# CHẠY 1 LẦN DUY NHẤT trên máy admin: tạo private key (keys/private_key.pem)
# và in ra PUBLIC KEY để dán vào các phần mềm (vd: giapha-app/backend/license.py).
#
#   .venv\Scripts\python keygen.py           -> tạo key mới
#   .venv\Scripts\python keygen.py --show    -> in lại public key từ private key đang có
#
# Sau khi tạo: SAO LƯU private_key.pem ra USB / password manager. Mất file = không cấp key được nữa.

import sys

from utils.license_utils import create_keypair, load_private_key, private_key_path, public_key_hex


def main():
    if "--show" in sys.argv:
        pub = public_key_hex(load_private_key())
    else:
        pub = create_keypair()
        print(f"Đã tạo private key: {private_key_path()}")
        print("-> HÃY SAO LƯU file này ngay. Không commit, không gửi cho ai.\n")
    print("PUBLIC KEY (dán vào phần mềm):")
    print(pub)


if __name__ == "__main__":
    try:
        main()
    except (FileExistsError, FileNotFoundError) as e:
        print(f"Lỗi: {e}")
        sys.exit(1)

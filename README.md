# License Tool

Bộ công cụ cấp bản quyền (license) theo máy, **dùng chung cho mọi sản phẩm**. Chạy offline. Ký key bằng Ed25519 (thư viện `cryptography`).

| File | Dành cho | Chức năng |
|------|----------|-----------|
| `get_code.exe` | Khách hàng | Hiện **Code** (mã máy 32 ký tự, tạo từ địa chỉ MAC — trên giao diện chỉ ghi "Code") + nút Copy. Giống nhau cho mọi sản phẩm |
| `generate_license.exe` | Bạn (người bán) | Nhập Code + hạn dùng → tạo License Key |

> **Không gửi `generate_license.exe` cho khách.**

## Flow cấp bản quyền

1. Khách gửi **Code** (từ màn hình kích hoạt của phần mềm, hoặc `get_code.exe`).
2. Mở `generate_license.exe`, chọn **Sản phẩm**, dán Code, chọn hạn dùng → bấm **Tạo License Key** (key tự copy vào clipboard).
3. Gửi key cho khách, khách nhập vào màn hình kích hoạt của phần mềm.

## Cặp khóa Ed25519

| Khóa | Nằm ở đâu | Dùng để |
|------|-----------|---------|
| **Private key** | `keys/private_key.pem` — **chỉ trên máy admin** | Tạo (ký) License Key |
| **Public key** | Nhúng trong từng phần mềm | Kiểm tra key — lộ ra cũng không tạo được key |

- Tạo cặp khóa **một lần**: `.venv\Scripts\python keygen.py`. Xem lại public key: `keygen.py --show`.
- **Sao lưu `private_key.pem`** (USB, password manager). Mất file = không cấp key được nữa; lộ file = ai cũng tạo được key.
- Private key **không** được gói vào .exe. `generate_license.exe` đọc file ở `keys\private_key.pem` cạnh file .exe
  (hoặc đường dẫn trong biến môi trường `LICENSE_PRIVATE_KEY`).
- Một private key dùng cho mọi sản phẩm; key gắn **mã sản phẩm** (`PRODUCTS` trong `utils/license_utils.py`) nên không dùng chéo được.

## Tích hợp vào phần mềm mới

1. Thêm sản phẩm vào `PRODUCTS` trong `utils/license_utils.py`.
2. Chép `get_machine_id()` + `verify_license_key()` vào phần mềm, cài `cryptography`, nhúng public key:

```python
PUBLIC_KEY = "<kết quả của keygen.py --show>"
ok, message = verify_license_key(license_key_khach_nhap, PUBLIC_KEY, "MA_SAN_PHAM")
```

Định dạng key: `base64url(PRODUCT|machine_id|YYYY-MM-DD) . base64url(chữ ký Ed25519)`.
Ví dụ đã tích hợp: `D:\Project\WebApp\giapha-app\backend\license.py`.

## Chạy bằng Python

```bash
python get_machine_id.py
python generate_license.py
```

## Đóng gói .exe

Dùng môi trường build riêng `.venv` (Python 3.12 + PyInstaller):

```bat
python -m venv .venv
.venv\Scripts\python -m pip install pyinstaller cryptography
.venv\Scripts\python -m PyInstaller --noconfirm --clean get_machine_id.spec
.venv\Scripts\python -m PyInstaller --noconfirm --clean generate_license.spec
```

Mỗi tool là **1 file .exe duy nhất** (đã gói sẵn Python + Tkinter), chạy trên Windows 10/11 64-bit không cần cài Python.

## Cấu trúc

- `utils/license_utils.py` — danh sách sản phẩm, Code (mã máy), quản lý cặp khóa, tạo / kiểm tra key.
- `keygen.py` — tạo cặp khóa (chạy 1 lần).
- `keys/private_key.pem` — private key (KHÔNG chia sẻ, KHÔNG commit).
- `utils/ui_kit.py` — widget giao diện: ô nhập Outlined (nhãn nằm trên viền), ô chọn, nút bo góc, thanh tiêu đề, thông báo.
- `assets/logo.ico`, `assets/logo_48|72|96.png` — icon & logo (được gói vào .exe). `assets/logo.png` là ảnh gốc, không gói.

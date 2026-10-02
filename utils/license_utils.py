# === license_utils.py ===
# Phần lõi cấp / kiểm tra license theo máy — dùng chung cho mọi sản phẩm.
#
# Ký bằng Ed25519 (khóa bất đối xứng):
# - PRIVATE KEY: chỉ nằm trên máy admin (file keys/private_key.pem), dùng để TẠO key.
#   KHÔNG đóng gói vào .exe, KHÔNG gửi cho ai. Mất file này = không tạo được key mới.
# - PUBLIC KEY: nhúng vào mọi phần mềm, chỉ dùng để KIỂM TRA key. Lộ ra cũng không sao.
#
# License Key = base64url(PRODUCT|machine_id|YYYY-MM-DD) . base64url(chữ ký Ed25519)
# PRODUCT giúp key của sản phẩm này không mở được sản phẩm khác.

import base64
import hashlib
import os
import sys
import uuid
from datetime import date, datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

# Mã sản phẩm -> tên hiển thị. Thêm sản phẩm mới vào đây.
PRODUCTS = {
    "GIAPHA": "Gia Phả",
}


def tool_dir():
    """Thư mục chứa tool (cạnh file .exe khi đã đóng gói, hoặc thư mục dự án khi chạy .py)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def private_key_path():
    """Có thể đổi chỗ để private key bằng biến môi trường LICENSE_PRIVATE_KEY."""
    return os.environ.get("LICENSE_PRIVATE_KEY") or os.path.join(tool_dir(), "keys", "private_key.pem")


def get_machine_id():
    """Machine ID 32 ký tự tạo từ địa chỉ MAC (giống nhau cho mọi sản phẩm trên cùng 1 máy)."""
    try:
        raw = str(uuid.getnode())
        return hashlib.sha256(raw.encode()).hexdigest()[:32].upper()
    except Exception:
        return hashlib.sha256("fallback_machine".encode()).hexdigest()[:32].upper()


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


# ------------------------------------------------------------
# Quản lý cặp khóa (chỉ admin dùng)
# ------------------------------------------------------------
def create_keypair(path=None) -> str:
    """Tạo private key mới và lưu ra file. Trả về PUBLIC KEY (hex) để nhúng vào phần mềm.
    Không ghi đè key cũ (ghi đè = mọi key đã cấp mất hiệu lực)."""
    path = path or private_key_path()
    if os.path.exists(path):
        raise FileExistsError(f"Đã có private key tại {path}. Xóa thủ công nếu thật sự muốn tạo lại.")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption())
    with open(path, "wb") as f:
        f.write(pem)
    return public_key_hex(key)


def load_private_key(path=None) -> Ed25519PrivateKey:
    path = path or private_key_path()
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Không tìm thấy private key tại:\n{path}\n\n"
            "Chạy keygen.py một lần để tạo, hoặc chép file private_key.pem đã sao lưu vào đó.")
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def public_key_hex(private_key: Ed25519PrivateKey) -> str:
    return private_key.public_key().public_bytes(serialization.Encoding.Raw,
                                                 serialization.PublicFormat.Raw).hex()


# ------------------------------------------------------------
# Tạo / kiểm tra License Key
# ------------------------------------------------------------
def generate_license_key(product: str, machine_id: str, expiry_date: str, private_key: Ed25519PrivateKey) -> str:
    """Tạo License Key cho 1 máy + 1 sản phẩm, hết hạn ngày expiry_date (YYYY-MM-DD)."""
    payload = f"{product}|{machine_id}|{expiry_date}".encode()
    return f"{_b64e(payload)}.{_b64e(private_key.sign(payload))}"


def verify_license_key(license_key: str, public_key_hex_str: str, product: str, machine_id: str = None):
    """Kiểm tra key: (hợp_lệ, thông_báo). Mặc định so với Code của máy đang chạy.
    Phần mềm phía khách chép hàm này + get_machine_id() và nhúng PUBLIC KEY."""
    try:
        payload_b64, sig_b64 = license_key.strip().split(".")
        payload, sig = _b64d(payload_b64), _b64d(sig_b64)
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex_str)).verify(sig, payload)
    except InvalidSignature:
        return False, "License Key không hợp lệ"
    except Exception:
        return False, "License Key không đúng định dạng"
    parts = payload.decode().split("|")
    if len(parts) != 3:
        return False, "License Key không đúng định dạng"
    key_product, key_machine, expiry_str = parts
    if key_product != product:
        return False, "License Key không dành cho phần mềm này"
    if key_machine != (machine_id or get_machine_id()):
        return False, "License Key không đúng với Code của bạn"
    try:
        if date.today() > datetime.strptime(expiry_str, "%Y-%m-%d").date():
            return False, f"License Key đã hết hạn ({expiry_str})"
    except ValueError:
        return False, "License Key không hợp lệ (ngày hết hạn sai)"
    return True, "License Key hợp lệ"

# === generate_license.py ===
# Tool dành cho NGƯỜI BÁN (admin): nhập Code (mã máy) của khách + hạn dùng -> tạo License Key.
# KHÔNG gửi tool này cho khách hàng.

import calendar
import re
import tkinter as tk
from datetime import date, datetime, timedelta

from utils.license_utils import PRODUCTS, generate_license_key, load_private_key
from utils import ui_kit as ui

PERMANENT = "2099-12-31"
MACHINE_ID_LEN = 32


def add_months(d, months):
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def main():
    ui.enable_dpi_awareness()
    root = tk.Tk()
    ui.init_scale(root)
    ui.setup_window(root, "Tạo License Key", 640, 800, resizable=True)

    ui.HeaderBar(root, "Tạo License Key", "Cấp bản quyền phần mềm theo Code của khách hàng",
                 icon="key").pack(fill=tk.X)

    body = tk.Frame(root, bg=ui.BG, padx=ui.S(28), pady=ui.S(20))
    body.pack(fill=tk.BOTH, expand=True)

    # --- Hướng dẫn 3 bước ---
    steps = tk.Frame(body, bg=ui.SURFACE_SOFT, padx=ui.S(14), pady=ui.S(10))
    steps.pack(fill=tk.X, pady=(0, ui.S(20)))
    for i, text in enumerate([
        "Khách gửi Code (từ get_code.exe hoặc màn hình kích hoạt của phần mềm)",
        "Dán Code và chọn hạn dùng bên dưới",
        "Bấm Tạo License Key, rồi gửi key cho khách",
    ], start=1):
        row = tk.Frame(steps, bg=ui.SURFACE_SOFT)
        row.pack(fill=tk.X, pady=ui.S(2))
        tk.Label(row, text=str(i), bg=ui.ACCENT, fg="white", font=(ui.FONT, 8, "bold"),
                 width=2).pack(side=tk.LEFT)
        tk.Label(row, text=text, bg=ui.SURFACE_SOFT, fg=ui.INK_SOFT, font=(ui.FONT, 9),
                 anchor="w").pack(side=tk.LEFT, padx=(ui.S(8), 0))

    # --- Sản phẩm ---
    product_by_name = {name: code for code, name in PRODUCTS.items()}
    product_field = ui.OutlinedSelect(body, "Sản phẩm", list(product_by_name))
    product_field.pack(fill=tk.X, pady=(0, ui.S(16)))
    product_field.select(next(iter(product_by_name)))

    # --- Mã máy ---
    machine_field = ui.OutlinedField(body, "Code", mono=True,
                                     helper="Dán Code khách gửi (Ctrl+V)")
    machine_field.pack(fill=tk.X)
    machine_field.set_counter(f"0/{MACHINE_ID_LEN}")

    def normalized_machine_id():
        return re.sub(r"\s+", "", machine_field.get()).upper()

    def on_machine_change(event=None):
        mid = normalized_machine_id()
        machine_field.set_counter(f"{len(mid)}/{MACHINE_ID_LEN}", ok=len(mid) == MACHINE_ID_LEN)
        if machine_field._error:
            machine_field.set_helper("Dán Code khách gửi (Ctrl+V)")

    machine_field.input.bind("<KeyRelease>", on_machine_change)
    machine_field.input.bind("<<Paste>>", lambda e: root.after(10, on_machine_change))

    # --- Hạn dùng + nút chọn nhanh ---
    expiry_field = ui.OutlinedField(body, "Ngày hết hạn (YYYY-MM-DD)", helper="")
    expiry_field.pack(fill=tk.X, pady=(ui.S(16), 0))
    expiry_field.set(PERMANENT)

    chips_frame = tk.Frame(body, bg=ui.BG)
    chips_frame.pack(fill=tk.X, pady=(ui.S(8), 0), padx=(ui.S(2), 0))
    tk.Label(chips_frame, text="Chọn nhanh:", bg=ui.BG, fg=ui.INK_SOFT,
             font=(ui.FONT, 9)).pack(side=tk.LEFT, anchor=tk.N, pady=(ui.S(6), 0), padx=(0, ui.S(8)))
    chip_rows = tk.Frame(chips_frame, bg=ui.BG)
    chip_rows.pack(side=tk.LEFT, fill=tk.X)
    # Mỗi hàng 1 nhóm (ngày dùng thử / tháng-năm) để 8 nút không tràn khỏi cửa sổ
    preset_rows = [
        [
            ("1 ngày", lambda: date.today() + timedelta(days=1)),
            ("3 ngày", lambda: date.today() + timedelta(days=3)),
            ("7 ngày", lambda: date.today() + timedelta(days=7)),
            ("30 ngày", lambda: date.today() + timedelta(days=30)),
        ],
        [
            ("6 tháng", lambda: add_months(date.today(), 6)),
            ("1 năm", lambda: add_months(date.today(), 12)),
            ("3 năm", lambda: add_months(date.today(), 36)),
            ("Vĩnh viễn", lambda: datetime.strptime(PERMANENT, "%Y-%m-%d").date()),
        ],
    ]
    presets = [p for row in preset_rows for p in row]
    chips = []

    def describe_expiry():
        """Cập nhật dòng mô tả dưới ô ngày + làm nổi nút chọn nhanh tương ứng."""
        value = expiry_field.get() or PERMANENT
        for (label, fn), chip in zip(presets, chips):
            chip.set_variant("chip-active" if fn().isoformat() == value else "chip")
        try:
            d = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            expiry_field.set_helper("Ngày không hợp lệ — đúng định dạng: 2027-12-31", error=True)
            return None
        if value == PERMANENT:
            expiry_field.set_helper("Bản quyền vĩnh viễn")
        elif d < date.today():
            expiry_field.set_helper("Ngày này đã qua — key tạo ra sẽ hết hạn ngay", error=True)
        else:
            expiry_field.set_helper(f"Dùng được {(d - date.today()).days} ngày, đến {d.strftime('%d/%m/%Y')}")
        return value

    def pick(fn):
        expiry_field.set(fn().isoformat())
        describe_expiry()

    for i, row in enumerate(preset_rows):
        row_frame = tk.Frame(chip_rows, bg=ui.BG)
        row_frame.pack(fill=tk.X, pady=(ui.S(6) if i else 0, 0))
        for label, fn in row:
            chip = ui.RoundedButton(row_frame, label, command=lambda f=fn: pick(f), variant="chip",
                                    height=30, font_size=9, bold=False)
            chip.pack(side=tk.LEFT, padx=(0, ui.S(6)))
            chips.append(chip)
    expiry_field.input.bind("<KeyRelease>", lambda e: describe_expiry())
    describe_expiry()

    # --- Nút tạo ---
    create_btn = ui.RoundedButton(body, "Tạo License Key", height=46, font_size=11)
    create_btn.pack(fill=tk.X, pady=(ui.S(18), ui.S(18)))

    # --- Kết quả ---
    output_field = ui.OutlinedField(body, "License Key", multiline=True, lines=3, mono=True,
                                    readonly=True, font_size=10)
    output_field.pack(fill=tk.X)

    actions = tk.Frame(body, bg=ui.BG)
    actions.pack(fill=tk.X, pady=(ui.S(12), ui.S(12)))
    status_slot = tk.Frame(body, bg=ui.BG)
    status_slot.pack(fill=tk.X)
    status = ui.StatusBanner(status_slot)

    def generate():
        mid = normalized_machine_id()
        machine_field.set_counter(f"{len(mid)}/{MACHINE_ID_LEN}", ok=len(mid) == MACHINE_ID_LEN)
        if not mid:
            machine_field.set_helper("Vui lòng nhập Code", error=True)
            machine_field.focus()
            return
        if len(mid) != MACHINE_ID_LEN or not re.fullmatch(r"[0-9A-F]+", mid):
            machine_field.set_helper(
                f"Code phải gồm {MACHINE_ID_LEN} ký tự 0-9, A-F (hiện có {len(mid)} ký tự)", error=True)
            machine_field.focus()
            return
        machine_field.set(mid)
        on_machine_change()
        expiry = describe_expiry()
        if not expiry:
            expiry_field.focus()
            return
        try:
            private_key = load_private_key()
        except FileNotFoundError as e:
            status.show(str(e), "error")
            return
        product_name = product_field.value()
        key = generate_license_key(product_by_name[product_name], mid, expiry, private_key)
        output_field.set(key)
        ui.copy_to_clipboard(root, key)
        label = "vĩnh viễn" if expiry == PERMANENT else f"đến {datetime.strptime(expiry, '%Y-%m-%d').strftime('%d/%m/%Y')}"
        status.show(f"Đã tạo License Key {product_name} ({label}) và copy vào clipboard. Gửi key này cho khách.", "success")

    def copy_key():
        key = output_field.get()
        if not key:
            status.show("Chưa có License Key nào. Bấm \"Tạo License Key\" trước.", "info", auto_hide_ms=3000)
            return
        ui.copy_to_clipboard(root, key)
        copy_btn.set_text("Đã copy  ✓")
        root.after(2000, lambda: copy_btn.set_text("Copy License Key"))

    def reset():
        machine_field.set("")
        machine_field.set_helper("Dán Code khách gửi (Ctrl+V)")
        on_machine_change()
        expiry_field.set(PERMANENT)
        describe_expiry()
        output_field.set("")
        status.hide()
        machine_field.focus()

    create_btn._command = generate
    copy_btn = ui.RoundedButton(actions, "Copy License Key", command=copy_key, variant="secondary",
                                height=38, font_size=10)
    copy_btn.pack(side=tk.LEFT)
    ui.RoundedButton(actions, "Làm mới", command=reset, variant="ghost", height=38,
                     font_size=10, bold=False).pack(side=tk.LEFT, padx=(ui.S(8), 0))

    machine_field.input.bind("<Return>", lambda e: expiry_field.focus())
    expiry_field.input.bind("<Return>", lambda e: generate())
    machine_field.focus()
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        try:
            from tkinter import messagebox
            messagebox.showerror("Lỗi", f"Lỗi: {e}")
        except Exception:
            print(f"Lỗi: {e}")

# === get_machine_id.py ===
# Tool dành cho KHÁCH HÀNG: hiện Mã máy (Machine ID) để gửi cho nhà cung cấp
# nhận License Key kích hoạt phần mềm. Dùng chung cho mọi sản phẩm.
# Cách dùng: python get_machine_id.py  (hoặc chạy get_machine_id.exe)

import tkinter as tk

from utils.license_utils import get_machine_id
from utils import ui_kit as ui


def main():
    ui.enable_dpi_awareness()
    root = tk.Tk()
    ui.init_scale(root)
    ui.setup_window(root, "Lấy Code", 560, 380)

    machine_id = get_machine_id()

    ui.HeaderBar(root, "Code của bạn", "Dùng để nhận License Key kích hoạt phần mềm",
                 icon="monitor").pack(fill=tk.X)

    body = tk.Frame(root, bg=ui.BG, padx=ui.S(28), pady=ui.S(24))
    body.pack(fill=tk.BOTH, expand=True)

    field = ui.OutlinedField(body, "Code", mono=True, readonly=True,
                             font_size=13, justify="center")
    field.set(machine_id)
    field.pack(fill=tk.X)

    status_slot = tk.Frame(body, bg=ui.BG)
    status = ui.StatusBanner(status_slot)

    def copy_id():
        ui.copy_to_clipboard(root, machine_id)
        copy_btn.set_text("Đã copy  ✓")
        status.show("Đã copy Code. Dán (Ctrl+V) vào Zalo / email và gửi cho nhà cung cấp.", "success")
        root.after(2200, lambda: copy_btn.set_text("Copy Code"))

    copy_btn = ui.RoundedButton(body, "Copy Code", command=copy_id, height=44, font_size=11)
    copy_btn.pack(fill=tk.X, pady=(ui.S(18), ui.S(12)))
    status_slot.pack(fill=tk.X)

    tk.Label(
        body,
        text="Gửi Code này cho nhà cung cấp phần mềm để nhận License Key.\n"
             "Code chỉ dùng để cấp bản quyền, không chứa thông tin cá nhân.",
        bg=ui.BG, fg=ui.INK_FAINT, font=(ui.FONT, 9), justify="center",
    ).pack(side=tk.BOTTOM)

    root.bind("<Control-c>", lambda e: copy_id())
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            from tkinter import messagebox
            messagebox.showerror("Lỗi", f"Lỗi: {e}")
        except Exception:
            print(f"Lỗi: {e}")

"""フォーカスを奪わない全画面枠線オーバーレイのテスト"""
import tkinter as tk
import ctypes

# フォーカスを奪わないウィンドウにするための定数
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

BORDER_WIDTH = 30
BORDER_COLOR = "#FF4444"
DISPLAY_SECONDS = 5


def show_border_overlay():
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", "black")
    root.configure(bg="black")

    # 画面サイズ取得
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{sw}x{sh}+0+0")

    # 枠線を描画
    canvas = tk.Canvas(root, width=sw, height=sh, bg="black", highlightthickness=0)
    canvas.pack()
    b = BORDER_WIDTH
    # 上
    canvas.create_rectangle(0, 0, sw, b, fill=BORDER_COLOR, outline="")
    # 下
    canvas.create_rectangle(0, sh - b, sw, sh, fill=BORDER_COLOR, outline="")
    # 左
    canvas.create_rectangle(0, 0, b, sh, fill=BORDER_COLOR, outline="")
    # 右
    canvas.create_rectangle(sw - b, 0, sw, sh, fill=BORDER_COLOR, outline="")

    # ウィンドウハンドル取得してフォーカスを奪わないスタイルを設定
    root.update_idletasks()
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    # 数秒後に自動消去
    root.after(DISPLAY_SECONDS * 1000, root.destroy)
    root.mainloop()


if __name__ == "__main__":
    show_border_overlay()

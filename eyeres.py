"""
目の休憩リマインダー (Eye Rest Reminder)
=========================================
20分ごとにWindows通知で「画面から目を離して！」と知らせる常駐ツール。
システムトレイに常駐し、右クリックで一時停止・再開・終了ができます。

必要なパッケージ:
    pip install pystray Pillow plyer

使い方:
    python eye_rest_reminder.py
"""

import threading
import time
import sys
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow が必要です: pip install Pillow")

try:
    import pystray
    from pystray import MenuItem, Menu
except ImportError:
    sys.exit("pystray が必要です: pip install pystray")

# ---------- 設定 ----------
WORK_MINUTES = 20          # 通知間隔（分）
REMINDER_TITLE = "👁 目の休憩！"
REMINDER_MESSAGE = "画面から目を離して、6m先を20秒見よう"
NOTIFY_TIMEOUT = 10        # 通知の表示秒数
# ---------------------------

if "--debug" in sys.argv:
    WORK_SECONDS = 7
else:
    WORK_SECONDS = WORK_MINUTES * 60


class EyeRestReminder:
    def __init__(self):
        self.running = True       # アプリ全体の生存フラグ
        self.paused = False       # 一時停止フラグ
        self.seconds_left = WORK_SECONDS
        self.session_count = 0
        self.lock = threading.Lock()
        self.icon = None

    # --- トレイアイコン画像生成 ---
    def _create_icon_image(self, paused=False):
        """64x64 のシンプルな目のアイコンを生成"""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if paused:
            # 一時停止中: オレンジ
            bg_color = (255, 167, 38, 255)
            fg_color = (255, 255, 255, 255)
        else:
            # 動作中: ブルー
            bg_color = (79, 195, 247, 255)
            fg_color = (255, 255, 255, 255)

        # 背景の丸
        draw.ellipse([4, 4, 60, 60], fill=bg_color)

        # 目の形（楕円）
        draw.ellipse([14, 22, 50, 42], fill=fg_color)

        # 瞳
        draw.ellipse([27, 27, 37, 37], fill=bg_color)

        return img

    # --- Windows通知 ---
    def _notify(self):
        """OS通知を送る（フォーカスを奪わない）"""
        try:
            from plyer import notification
            notification.notify(
                title=REMINDER_TITLE,
                message=REMINDER_MESSAGE,
                timeout=NOTIFY_TIMEOUT,
                app_name="目の休憩リマインダー",
            )
        except Exception as e:
            # plyer が動かない場合のフォールバック
            print(f"通知エラー: {e}")
            print(f"[{REMINDER_TITLE}] {REMINDER_MESSAGE}")

    # --- タイマーループ（別スレッド） ---
    def _timer_loop(self):
        while self.running:
            time.sleep(1)

            with self.lock:
                if self.paused or not self.running:
                    continue
                self.seconds_left -= 1

                if self.seconds_left <= 0:
                    self.session_count += 1
                    self.seconds_left = WORK_SECONDS

            # メニュー表示を毎秒更新
            if self.icon:
                self.icon.update_menu()

            # ロック外で通知（ブロックする可能性があるため）
            if self.seconds_left == WORK_SECONDS and self.running:
                self._notify()
                self._update_icon()

    # --- アイコン更新 ---
    def _update_icon(self):
        if self.icon:
            self.icon.icon = self._create_icon_image(paused=self.paused)

    # --- メニューアクション ---
    def _toggle_pause(self, icon, item):
        with self.lock:
            self.paused = not self.paused
            if not self.paused:
                # 再開時はタイマーリセット
                self.seconds_left = WORK_SECONDS
        self._update_icon()

    def _reset_timer(self, icon, item):
        with self.lock:
            self.seconds_left = WORK_SECONDS
            self.paused = False
        self._update_icon()

    def _quit(self, icon, item):
        self.running = False
        icon.stop()

    def _get_pause_text(self, item):
        return "再開" if self.paused else "一時停止"

    def _get_status(self, item):
        with self.lock:
            if self.paused:
                return "⏸ 一時停止中"
            m, s = divmod(self.seconds_left, 60)
            return f"次の休憩まで {m:02d}:{s:02d}"

    # --- メイン ---
    def run(self):
        menu = Menu(
            MenuItem(self._get_status, None, enabled=False, default=False),
            Menu.SEPARATOR,
            MenuItem(self._get_pause_text, self._toggle_pause),
            MenuItem("タイマーリセット", self._reset_timer),
            MenuItem(f"休憩回数: {self.session_count}", None, enabled=False, default=False),
            Menu.SEPARATOR,
            MenuItem("終了", self._quit),
        )

        self.icon = pystray.Icon(
            name="eye_rest_reminder",
            icon=self._create_icon_image(),
            title="目の休憩リマインダー",
            menu=menu,
        )

        # タイマースレッド開始
        timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        timer_thread.start()

        print("目の休憩リマインダーを起動しました")
        print(f"  {WORK_SECONDS}秒ごとに通知します" if WORK_SECONDS < 60 else f"  {WORK_MINUTES}分ごとに通知します")
        print("  システムトレイのアイコンを右クリックで操作できます")
        print("  終了するにはトレイアイコン → 終了")

        # pystray のメインループ（ブロッキング）
        self.icon.run()


if __name__ == "__main__":
    app = EyeRestReminder()
    app.run()

# Eye Rest Reminder
20分ごとにWindows通知で休憩を促すシステムトレイ常駐ツール。  20-20-20ルール（20分ごとに6m先を20秒見る）の実践用。

## Requirements

- Python 3.8+
- Windows 10 / 11

```
pip install pystray Pillow plyer
```

## Usage

```
python eye_rest_reminder.py
```

タスクバー右下にアイコンが常駐する。20分経過でOS通知がポップアップし、約10秒で自動消去。以降ループ。

### トレイメニュー（右クリック）

| 項目 | 動作 |
|------|------|
| ステータス表示 | 次の休憩までの残り時間 |
| 一時停止 / 再開 | タイマーを止める・再開時にリセット |
| タイマーリセット | 20分に戻す |
| 終了 | アプリ終了 |

## Config

`eye_rest_reminder.py` 冒頭の定数を編集：

```python
WORK_MINUTES = 20          # 通知間隔（分）
REMINDER_TITLE = "👁 目の休憩！"
REMINDER_MESSAGE = "画面から目を離して、6m先を20秒見よう"
NOTIFY_TIMEOUT = 10        # 通知の表示秒数
```

## Architecture

```
メインスレッド ── pystray イベントループ（トレイアイコン + メニュー）
タイマースレッド ── 1秒刻みカウントダウン → 0到達で plyer.notification 発火
```

- 通知は `plyer.notification.notify()` 経由でWindowsトースト通知を使用。フォーカスを奪わない。
- アイコンは `Pillow` で動的生成（動作中: 青、一時停止: オレンジ）。
- スレッド間の状態共有は `threading.Lock` で保護。

## Dependencies

| Package | Role |
|---------|------|
| pystray | システムトレイ常駐 + メニュー |
| Pillow | トレイアイコン画像生成 |
| plyer | クロスプラットフォームOS通知 |

## License

MIT
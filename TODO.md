# poikatsu GitHub Actions 移行 TODO

## 完了済み
- `poikatsu_cli.py` — `--email`フラグ・`send_email()`追加
- `.github/workflows/daily.yml` — 毎朝7:00 JST cron
- `.gitignore` — `.env`除外
- `PLAN_anthropic_hybrid.md` — Gemini品質不足時の代替案メモ
- git init + 初回commit (daefd40) + remote設定

## 残タスク（順番通りに実施）

### 1. git push
```bash
cd /d/ramen26/poikatsu

# PAT使う場合（Termius等リモートから）
git remote set-url origin https://zenmashi249:YOUR_PAT@github.com/zenmashi249/poikatsu.git
git push -u origin master
git remote set-url origin https://github.com/zenmashi249/poikatsu.git  # PAT削除

# PC直接の場合
git push -u origin master
```

### 2. GitHub Secrets登録（ブラウザのみ、スマホ可）
URL: https://github.com/zenmashi249/poikatsu/settings/secrets/actions

| Secret名 | 値 |
|---|---|
| `GEMINI_API_KEY` | `.env`に記載のキー（`AQ.`始まり） |
| `GMAIL_USERNAME` | `hossyy924@gmail.com` |
| `GMAIL_APP_PASSWORD` | 下記手順で取得 |
| `EMAIL_TO` | `hossyy924@gmail.com` |

### 3. Gmail アプリパスワード取得
1. https://myaccount.google.com/security
2. 2段階認証 → アプリパスワード
3. アプリ名「poikatsu」で生成（16文字）→ `GMAIL_APP_PASSWORD`に設定

### 4. 動作確認
GitHub Actions画面で手動実行：
https://github.com/zenmashi249/poikatsu/actions
→ "Run workflow" → メール受信確認

## 自動実行スケジュール
毎朝7:00 JST（UTC 22:00）

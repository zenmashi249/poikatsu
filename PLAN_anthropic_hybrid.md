# Anthropic API ハイブリッド案

Gemini単体で品質不足の場合の代替プラン。

## 構成

```
Phase 1: Gemini 2.5 Flash + Google検索 → 生情報収集（整形なし）
Phase 2: Claude Haiku（Anthropic API）→ 推論・フィルタ・整形 → メール送信
```

## コスト

- Anthropic APIは**プリペイド制**、最低チャージ $5
- Claude Haiku 使用時: ~$0.2/月（$5チャージで約25ヶ月分）
- Gemini 2.5 Flash: 無料枠内

## 必要なもの

1. Anthropic APIキー取得: https://console.anthropic.com/
2. GitHub Secretsに追加: `ANTHROPIC_API_KEY`
3. `requirements.txt` に `anthropic` 追加

## 実装イメージ

```python
# Phase 1: Gemini（生情報収集）
gemini_raw = run_gemini_search(target_date)  # 現行のrun()を改修

# Phase 2: Claude（推論・整形）
import anthropic
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=2048,
    system="ポイ活専門家として、以下の生情報を分析・整形してください。",
    messages=[{"role": "user", "content": gemini_raw}],
)
result = response.content[0].text
```

## Gemini Phase 1 のプロンプト変更点

現行（整形あり）→ 生情報ダンプに変更:
- 「箇条書きで情報を羅列せよ、整形・選定はしない」
- Claudeに選定・優先順位付け・整形を任せる

## workflow変更点

```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}  # 追加
  GMAIL_USERNAME: ${{ secrets.GMAIL_USERNAME }}
  GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
  EMAIL_TO: ${{ secrets.EMAIL_TO }}
```

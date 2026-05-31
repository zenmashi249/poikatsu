#!/usr/bin/env python3
"""
ポイ活おすすめスキームCLI
Usage: python poikatsu_cli.py [-v] [--date YYYY-MM-DD] [--output text|json]
必要なもの: GEMINI_API_KEY のみ（無料、クレカ不要）
取得: https://aistudio.google.com/apikey
"""

import os
import sys
import json
import argparse
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

CARDS_FILE = Path(__file__).parent / "cards.json"


def load_cards() -> list[str]:
    if CARDS_FILE.exists():
        return json.loads(CARDS_FILE.read_text(encoding="utf-8"))
    return []

# ================================================================
# PROMPT TUNING SECTION - ここを編集してプロンプト調整
# ================================================================

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """\
あなたはポイント活動（ポイ活）の専門家アシスタントです。
今日の日付: {today}

## ユーザーの保有クレジットカード
{cards}

Google検索で最新情報を調査し、以下3カテゴリのおすすめポイ活スキームを報告してください。

## カテゴリ
1. クレカ・決済 — 上記保有カードのキャンペーン・ポイント還元・優待情報を優先。QRコード決済（PayPay等）も含む
2. ふるさと納税 — お得なキャンペーン・高還元サイト情報
3. ECサイト — 楽天・Amazon・Yahoo等のポイントアップ・セール情報

## 選定基準（優先順）
1. 現在実施中（今日から参加可能）かつ明確な終了日がある期間限定キャンペーン
2. 締め切りが近い（残り7日以内を優先）
3. ポイント還元率・特典の大きさ
4. 手軽さ

## 除外ルール（必須）
- 「常時開催」「いつでも」「期間なし」のキャンペーンは除外
- 終了日が今日より前のものは除外
- ただし、開始から1ヶ月以上経過している期間限定キャンペーンは「⚠️ 見逃し注意」として1件まで掲載可

## 出力形式
各カテゴリ2〜3件に絞り、以下を記載:
- サービス名・キャンペーン名
- 還元率 or 特典内容（具体的な数字）
- 期間（開始日〜終了日を明記）・条件
- 参加方法（1行で）
"""

USER_PROMPT = "今日（{today}）のポイ活おすすめ情報をまとめてください。クレカ・決済（保有カード優先）、ふるさと納税、ECサイトの3カテゴリで。"

# ================================================================
# END PROMPT TUNING SECTION
# ================================================================


def run(target_date: date, verbose: bool = False) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("[ERROR] GEMINI_API_KEY が未設定。.env を確認してください。")

    client = genai.Client(api_key=api_key)

    today_str = target_date.strftime("%Y年%m月%d日")
    cards = load_cards()
    cards_str = "\n".join(f"- {c}" for c in cards) if cards else "（未登録）"

    response = client.models.generate_content(
        model=MODEL,
        contents=USER_PROMPT.format(today=today_str),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT.format(today=today_str, cards=cards_str),
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.3,
        ),
    )

    if verbose:
        usage = response.usage_metadata
        print(
            f"[usage] in={usage.prompt_token_count} out={usage.candidates_token_count}",
            file=sys.stderr,
        )

    return response.text


def send_email(subject: str, body: str) -> None:
    gmail_user = os.environ["GMAIL_USERNAME"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    email_to = os.environ.get("EMAIL_TO", gmail_user)

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = email_to
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, email_to, msg.as_string())


def main():
    parser = argparse.ArgumentParser(
        description="毎朝のポイ活おすすめスキームCLI（Gemini無料枠）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="例: python poikatsu_cli.py -v\n    python poikatsu_cli.py --date 2026-06-01",
    )
    parser.add_argument("--date", help="対象日付 YYYY-MM-DD（省略時: 今日）")
    parser.add_argument("-v", "--verbose", action="store_true", help="トークン使用量を表示")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    parser.add_argument("--email", action="store_true", help="結果をGmailで送信（GMAIL_USERNAME/GMAIL_APP_PASSWORD/EMAIL_TO 必須）")
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date.today()

    if args.verbose:
        print(f"[start] {target_date} / {MODEL}", file=sys.stderr)

    result = run(target_date, verbose=args.verbose)

    if args.output == "json":
        print(json.dumps({"date": target_date.isoformat(), "content": result}, ensure_ascii=False, indent=2))
    else:
        print(result)

    if args.email:
        subject = f"【ポイ活】{target_date.strftime('%Y/%m/%d')} のおすすめ情報"
        send_email(subject, result)
        print("[email] 送信完了", file=sys.stderr)


if __name__ == "__main__":
    main()

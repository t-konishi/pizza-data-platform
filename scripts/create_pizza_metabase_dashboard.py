#!/usr/bin/env python3
"""Create the Pizza Order Analysis dashboard in a LOCAL Metabase instance.

Uses the existing saved question #40 as the daily order amount chart.
Additional questions and dashboard are created through Metabase's REST API.
Credentials are never persisted. Python standard library only (Python 3.8+).

Usage:
  python3 create_pizza_metabase_dashboard.py

The script requires the already-created mart tables in Pizza Data Warehouse.
By default, all newly created cards use 2026-09-20 through 2026-09-26.
Ensure saved question #40 also uses that date filter before running.
"""
import argparse
import datetime as dt
import getpass
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:3000"
DASHBOARD_NAME = "ピザ注文分析ダッシュボード"


class MetabaseAPI:
    def __init__(self, base, api_key=None):
        self.base = base.rstrip("/")
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if api_key:
            self.headers["x-api-key"] = api_key

    def request(self, method, path, body=None):
        url = self.base + path
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace")[:900]
            raise RuntimeError("{} {}: HTTP {} / {}".format(method, path, err.code, detail)) from err
        except urllib.error.URLError as err:
            raise RuntimeError("{}への接続に失敗しました: {}".format(url, err.reason)) from err


def unpack_collection(result):
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if isinstance(result.get("data"), list):
            return result["data"]
    return []


def question(name, database_id, sql, display, viz, collection_id):
    return {
        "name": name,
        "type": "question",
        "description": "ピザ注文分析デモ（2026年9月20日〜26日、注文金額ベース）",
        "dataset_query": {
            "database": database_id,
            "type": "native",
            "native": {"query": sql.strip(), "template-tags": {}},
        },
        "display": display,
        "visualization_settings": viz,
        "collection_id": collection_id,
    }


def main():
    parser = argparse.ArgumentParser(description="ローカルMetabaseにピザ注文分析ダッシュボードを作成")
    parser.add_argument("--url", default=DEFAULT_BASE)
    parser.add_argument("--existing-card-id", type=int, default=40,
                        help="保存済み『日別注文金額の推移』の質問ID（既定40）")
    parser.add_argument("--start", default="2026-09-20")
    parser.add_argument("--end", default="2026-09-26")
    args = parser.parse_args()

    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1"):
        parser.error("安全のためURLは http://localhost:3000 または http://127.0.0.1:3000 のみ対応")
    try:
        start = dt.date.fromisoformat(args.start)
        end = dt.date.fromisoformat(args.end)
        if start > end:
            parser.error("開始日は終了日以前にしてください")
    except ValueError as err:
        parser.error("日付は YYYY-MM-DD 形式で指定してください: {}".format(err))

    print("接続先：{}".format(args.url))
    print("集計期間：{} ～ {}".format(start, end))
    print("既存質問：#{}（日別注文金額の推移）".format(args.existing_card_id))
    print("注意：既存質問の期間は本スクリプトで変更しません。期間が一致していることを確認してください。")
    api_key = os.environ.get("METABASE_API_KEY")
    api = MetabaseAPI(args.url, api_key=api_key)
    if not api_key:
        email = input("Metabase管理者のメールアドレス: ").strip()
        password = getpass.getpass("Metabaseパスワード（表示されません）: ")
        if not email or not password:
            raise RuntimeError("メールアドレスとパスワードが必要です")
        session_data = api.request("POST", "/api/session", {"username": email, "password": password})
        api.headers["X-Metabase-Session"] = session_data["id"]
        del password
        print("Metabase認証成功")

    existing_card = api.request("GET", "/api/card/{}".format(args.existing_card_id))
    if existing_card.get("name") != "日別注文金額の推移":
        print("注意：既存質問#{}の名前は『{}』です。".format(args.existing_card_id, existing_card.get("name")))
        answer = input("この質問を流用しますか？ [y/N]: ").strip().lower()
        if answer != "y":
            print("中止しました。データの変更はありません。")
            return 1
    database_id = existing_card.get("database_id") or existing_card.get("dataset_query", {}).get("database")
    if not database_id:
        raise RuntimeError("既存質問からdatabase_idを取得できませんでした")
    collection_id = existing_card.get("collection_id")
    print("元の質問からデータベースID={}, コレクションID={}を取得".format(database_id, collection_id))

    dashboards = unpack_collection(api.request("GET", "/api/dashboard"))
    matching = [d for d in dashboards if d.get("name") == DASHBOARD_NAME and not d.get("archived")]
    if matching:
        existing_id = matching[0]["id"]
        existing_dash = api.request("GET", "/api/dashboard/{}".format(existing_id))
        existing_count = len(existing_dash.get("dashcards", []))
        print("同名のダッシュボードが既に存在します（カード{}件）。二重作成しません。".format(existing_count))
        print("{}/dashboard/{}".format(args.url, existing_id))
        if existing_count < 6:
            print("カードが6件未満です。必要ならMetabase画面で確認してください。")
        return 0

    start_literal = "DATE '{}'".format(start.isoformat())
    end_literal = "DATE '{}'".format(end.isoformat())
    filter_daily = "date_day BETWEEN {} AND {}".format(start_literal, end_literal)
    filter_fact = "f.order_date BETWEEN {} AND {}".format(start_literal, end_literal)
    prefix = "Pizza BI | "
    specs = [
        question(prefix + "注文金額合計", database_id,
                 "SELECT COALESCE(SUM(total_amount), 0) AS total_amount FROM analytics_marts.mart_daily_sales WHERE " + filter_daily,
                 "scalar", {}, collection_id),
        question(prefix + "注文件数", database_id,
                 "SELECT COALESCE(SUM(order_count), 0) AS order_count FROM analytics_marts.mart_daily_sales WHERE " + filter_daily,
                 "scalar", {}, collection_id),
        question(prefix + "注文数量合計", database_id,
                 "SELECT COALESCE(SUM(total_quantity), 0) AS total_quantity FROM analytics_marts.mart_daily_sales WHERE " + filter_daily,
                 "scalar", {}, collection_id),
        question(prefix + "日別注文数量の推移", database_id,
                 "SELECT date_day, total_quantity FROM analytics_marts.mart_daily_sales WHERE " + filter_daily + " ORDER BY date_day",
                 "line", {"graph.dimensions": ["date_day"], "graph.metrics": ["total_quantity"]}, collection_id),
        question(prefix + "商品別注文金額", database_id,
                 """SELECT p.pizza_name, SUM(f.quantity) AS total_quantity, SUM(f.subtotal) AS total_amount
                 FROM analytics_marts.fct_sales AS f
                 INNER JOIN analytics_marts.dim_pizzas AS p ON f.pizza_id = p.pizza_id
                 WHERE """ + filter_fact + """
                 GROUP BY p.pizza_name ORDER BY total_amount DESC""",
                 "bar", {"graph.dimensions": ["pizza_name"], "graph.metrics": ["total_amount"]}, collection_id),
    ]

    print("質問5件を作成します。")
    new_ids = []
    for spec in specs:
        c = api.request("POST", "/api/card", spec)
        new_ids.append(c["id"])
        print("  作成: #{} {}".format(c["id"], spec["name"]))

    dashboard = api.request("POST", "/api/dashboard", {
        "name": DASHBOARD_NAME,
        "description": "ピザ注文分析（{} ～ {}）。金額は注文明細の小計ベースであり確定売上ではありません。".format(start, end),
        "collection_id": collection_id,
        "parameters": [],
    })
    dash_id = dashboard["id"]
    cards = [
        # Layout on 24-column Metabase dashboard grid
        (new_ids[0], 0, 0, 8, 3),
        (new_ids[1], 0, 8, 8, 3),
        (new_ids[2], 0, 16, 8, 3),
        (args.existing_card_id, 3, 0, 12, 7),
        (new_ids[3], 3, 12, 12, 7),
        (new_ids[4], 10, 0, 24, 7),
    ]
    dashcards = []
    for index, (card_id, row, col, size_x, size_y) in enumerate(cards):
        dashcards.append({
            "id": -(index + 1),
            "card_id": card_id,
            "row": row,
            "col": col,
            "size_x": size_x,
            "size_y": size_y,
            "dashboard_tab_id": None,
            "parameter_mappings": [],
            "series": [],
            "visualization_settings": {},
        })
    try:
        api.request("PUT", "/api/dashboard/{}".format(dash_id), {"dashcards": dashcards})
    except Exception as err:
        print("ダッシュボード自体は作成されましたが、カード配置に失敗しました。", file=sys.stderr)
        print("手動で開いてカードを追加してください: {}/dashboard/{}".format(args.url, dash_id), file=sys.stderr)
        raise
    result = api.request("GET", "/api/dashboard/{}".format(dash_id))
    print("\n完了：{}".format(DASHBOARD_NAME))
    print("{}/dashboard/{}".format(args.url, dash_id))
    print("登録カード数：{}".format(len(result.get("dashcards", []))))
    print("※ダッシュボードには固定期間が設定されています。期間変更や共通の日付フィルターは次の演習で対応できます。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, KeyError) as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)

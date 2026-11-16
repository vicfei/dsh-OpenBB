#!/usr/bin/env python3
"""OpenBB 确定性桥：精选命令目录 + 一次性执行，给 DSH agent 的工具面。

OpenBB Platform (Apache-2.0) 是统一金融数据平台（equity/economy/etf/news/sec…，
多 provider）。本桥做三件事：
1. 目录（CATALOG）：精选 agent 高频命令 + 参数 schema（LLM 可据此规划）
2. 执行（run）：一次性调用 openbb Python API，输出 JSON（表格 + 来源 + 参数）
3. 纪律：来源/时间戳随数据返回——证据标签的数据端，延续家族血统

用法：
  python3 scripts/obb.py --list                       # 打印命令目录
  python3 scripts/obb.py --run equity.price.quote --params '{"symbol":"NVDA"}'
"""
import argparse, datetime as dt, json, sys

CATALOG = {
    "equity.price.quote": {"desc": "实时报价", "params": {"symbol": "str"}},
    "equity.price.historical": {"desc": "历史日线", "params": {"symbol": "str", "start_date": "YYYY-MM-DD(可省)", "provider": "可省(yfinance)"}},
    "equity.profile": {"desc": "公司概况", "params": {"symbol": "str"}},
    "equity.fundamental.metrics": {"desc": "关键财务比率", "params": {"symbol": "str"}},
    "equity.news": {"desc": "个股新闻", "params": {"symbol": "str", "limit": "int(可省)"}},
    "economy.snapshots": {"desc": "宏观快照（部分 provider 需 key）", "params": {}},
    "news.world": {"desc": "全球新闻", "params": {"limit": "int(可省)"}},
}


def run(cmd, params):
    from openbb import obb
    node = obb
    for part in cmd.split("."):
        node = getattr(node, part)
    res = node(**params)
    df = res.to_df()
    # 表格瘦身：超过 30 行只留头尾各 15；列宽截断
    if len(df) > 30:
        df = __import__("pandas").concat([df.head(15), df.tail(15)])
    return {"cmd": cmd, "params": params, "provider": getattr(res, "provider", None),
            "rows": int(len(df)), "warnings": getattr(res, "warnings", None),
            "data": json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso")),
            "fetched_at": dt.datetime.now().isoformat(timespec="seconds")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run")
    ap.add_argument("--params", default="{}")
    args = ap.parse_args()
    if args.list:
        for cmd, meta in CATALOG.items():
            print(f"{cmd:<32} {meta['desc']:<14} params={json.dumps(meta['params'], ensure_ascii=False)}")
        return
    if args.run:
        try:
            out = run(args.run, json.loads(args.params))
            print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
        except Exception as e:
            print(json.dumps({"cmd": args.run, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

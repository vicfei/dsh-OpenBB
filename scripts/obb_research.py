#!/usr/bin/env python3
"""dsh-OpenBB v0 — OpenBB 数据研究引擎（家族 2 调用模式）

LLM 从命令目录规划 → 确定性桥执行（数字出自 OpenBB）→ LLM 解读（[F#] 挂靠字段）。
与 vibe-trading 同血统：模型不产数、只解读；数据带 provider 与时间戳。

用法：
  python3 scripts/obb_research.py --question "NVDA 现在估值与动能什么状态？" --symbols NVDA --save
"""
import argparse, datetime as dt, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from obb import CATALOG, run as obb_run

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAILS = os.path.join(KIT, "trails")


def llm(sysmsg, user, json_out=False):
    key = subprocess.run(["bash", "-c", 'grep -m1 "^export DEEPSEEK_API_KEY=" ~/.bashrc | cut -d= -f2'],
                         capture_output=True, text=True).stdout.strip().strip('"')
    body = {"model": "deepseek-chat", "temperature": 0,
            "messages": [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]}
    if json_out:
        body["response_format"] = {"type": "json_object"}
    r = subprocess.run(["curl", "-s", "-m", "180", "https://api.deepseek.com/chat/completions",
                        "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
                        "-d", json.dumps(body)], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)["choices"][0]["message"]["content"]
    except Exception:
        raise SystemExit(f"LLM 调用失败: {r.stdout[:200]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--symbols", default="")
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()
    t0 = time.time()

    plan = llm(
        "你是数据规划员。从命令目录里选 1-3 条最相关的命令并给参数，"
        "输出 JSON {\"steps\":[{\"cmd\":\"...\",\"params\":{...}}]}。只规划。",
        f"问题：{args.question}\n关注标的：{args.symbols or '（问题内识别）'}\n"
        f"命令目录：\n{json.dumps(CATALOG, ensure_ascii=False)}", json_out=True)
    try:
        plan = json.loads(plan) if isinstance(plan, str) else plan
    except json.JSONDecodeError:
        import re
        plan = json.loads(re.sub(r"^```(json)?|```$", "", plan.strip(), flags=re.M).strip())

    results = []
    for step in plan.get("steps", []):
        try:
            out = obb_run(step["cmd"], step.get("params", {}))
            slim = {k: out[k] for k in ("cmd", "params", "provider", "rows", "fetched_at")}
            slim["data"] = out["data"][:12]
            results.append(slim)
        except Exception as e:
            results.append({"cmd": step["cmd"], "error": f"{type(e).__name__}: {e}"})
            print(f"⚠ {step['cmd']} 失败: {e}", file=sys.stderr)

    findings = llm(
        "你是投研解读员。纪律：只允许引用给定数据（[F#] 各挂靠某条 cmd 的具体字段），"
        "禁止编造数字；数据缺失或报错要如实说明。输出 markdown，不超过 6 条结论。",
        f"问题：{args.question}\n数据：\n{json.dumps(results, ensure_ascii=False, default=str)}")

    print(f"## 研究问题：{args.question}\n\n**plan**：{json.dumps(plan.get('steps'), ensure_ascii=False)}\n")
    for r in results:
        print(f"- `{r['cmd']}` → {r.get('provider', '?')} · {r.get('rows', '?')} 行 · {r.get('fetched_at', '?')}"
              + (f" · ⚠ {r['error'][:60]}" if "error" in r else ""))
    print(f"\n## 解读\n\n{findings}\n")
    print(f"── OpenBB 确定性数据层 · 耗时 {time.time()-t0:.0f}s")

    if args.save:
        os.makedirs(TRAILS, exist_ok=True)
        base = os.path.join(TRAILS, dt.datetime.now().strftime("%Y%m%d-%H%M"))
        json.dump({"question": args.question, "plan": plan, "results": results, "findings": findings},
                  open(base + ".json", "w"), ensure_ascii=False, indent=1, default=str)
        print(f"→ {base}.json", file=sys.stderr)


if __name__ == "__main__":
    main()

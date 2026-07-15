#!/usr/bin/env python3
"""
Fetch quotes for the tickers in tickers.json and write quotes.json.
Runs in GitHub Actions on a schedule (see .github/workflows/update-quotes.yml).
Contains market prices only — no position sizes, no cost bases.
"""
import json, os, time
from concurrent.futures import ThreadPoolExecutor

import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
US_PROXIES = {"ACWI", "GLD", "NOK", "IBB", "QTUM", "ARKX"}

cfg = json.load(open(os.path.join(HERE, "tickers.json"), encoding="utf-8"))

def fetch_one(sym):
    fi = yf.Ticker(sym).fast_info
    c, pc = fi.last_price, fi.previous_close
    if c and pc and c > 0 and pc > 0:
        try:
            cur = fi.currency or ""
        except Exception:
            cur = ""
        return float(c), float(pc), cur
    raise ValueError(f"no data for {sym}")

quotes, proxied, extra, fx = {}, [], {}, {}

def work_portfolio(item):
    tk, candidates = item
    for sym in candidates:
        try:
            c, pc, cur = fetch_one(sym)
            quotes[tk] = {"c": c, "pc": pc, "cur": cur, "sym": sym}
            if sym in US_PROXIES:
                proxied.append(tk)
            return
        except Exception:
            continue
    print(f"WARN: no quote for {tk}")

def work_extra(sym):
    try:
        c, pc, cur = fetch_one(sym)
        extra[sym] = {"c": c, "pc": pc, "cur": cur}
    except Exception:
        print(f"WARN: no quote for extra {sym}")

def work_fx(sym):
    try:
        c, pc, _ = fetch_one(sym)
        fx[sym.replace("=X", "")] = c
    except Exception:
        print(f"WARN: no fx for {sym}")

with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(work_portfolio, cfg["portfolio"].items()))
    list(ex.map(work_extra, cfg.get("extra", [])))
    list(ex.map(work_fx, cfg.get("fx", [])))

out = {
    "updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    "quotes": quotes,
    "proxied": sorted(proxied),
    "extra": extra,
    "fx": fx,
}
with open(os.path.join(HERE, "quotes.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"{len(quotes)}/{len(cfg['portfolio'])} portfolio quotes, "
      f"{len(extra)} extra, fx: {fx}")

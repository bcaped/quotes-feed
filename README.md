# quotes-feed

Automated market-price feed: `quotes.json` is refreshed every ~15 minutes during
US market hours (13–21 UTC, Mon–Fri) by a GitHub Action running yfinance.

Contains public market prices and FX rates only — no positions, quantities, or
cost bases. Consumed by a private portfolio dashboard.

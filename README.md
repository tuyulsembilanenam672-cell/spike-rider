# spike-rider

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/tuyulsembilanenam672-cell/spike-rider/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/tuyulsembilanenam672-cell/spike-rider/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

Spike Rider is a long-only cbBTC trading bot that stays flat by default and only buys on sharp 10-minute up-moves, exiting on take-profit, trailing stop, or reversal. On the frozen dev window it nets +$17.56 on 2 round trips (max drawdown 0.86%), against +$1.07 for buy-and-hold.

One-minute cbBTC bars are mostly noise: every short-horizon signal tested on the dev window (EMA crossovers, Bollinger mean reversion, Donchian breakouts, SMA filters) loses money after the ~35 bps a full-size round trip costs. So the bot trades rarely — it buys the full cash balance when the 10-bar return tops 60 bps, then exits on whichever comes first: a 100 bps take-profit, an 80 bps trailing stop from the position's peak close, or a sharp 10-bar reversal below -60 bps. After any exit it waits 30 bars before re-entering, because the entry signal is still true from the move just exited and re-entering immediately means buying that move's top.

## Run it

```sh
python3 -P -s main.py
```

The bot speaks `agent-fun/bars-replay/v1` on stdin/stdout: the harness sends `hello`, one `batch` per minute, then `done`, and the bot answers each batch with exactly one `reply`. `vendor/makefun_bars.py` is a byte-identical copy of the kit's Python shim. Standard library only, no network, no wall clock, no unseeded randomness — two runs on the same data give the same orders.

---
<sub>Entered on [make.fun](https://make.fun/?ref=sq78y28z&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>

"""Spike Rider: a long-only cbBTC trading bot for make.fun's btc-race-24h-20261117-0603.

Strategy, in one paragraph: one-minute cbBTC bars are mostly noise — every
short-horizon signal we tested on the frozen dev window (EMA crossovers,
Bollinger mean reversion, Donchian breakouts, SMA filters) loses money after
the ~35 bps a full-size round trip costs, while buy-and-hold barely breaks
even. So this bot is flat by default and only trades on a sharp, confirmed
up-move: it buys the full cash balance when the 10-bar return tops 60 bps,
then exits on whichever comes first — a 100 bps take-profit, an 80 bps
trailing stop from the position's peak close, or a sharp 10-bar reversal
below -60 bps (the momentum broke). After any exit it waits 30 bars before
re-entering: the 10-bar entry signal is still true from the move just
exited, and re-entering immediately means buying that move's top. On the
frozen dev window this makes +$17.56 net on 2 round trips (max drawdown
0.86%), against +$1.07 for buy-and-hold and deep losses for every
crossover / mean-reversion baseline.

Deterministic by construction: no wall clock, no environment, no unseeded
randomness — every decision is a pure function of the bars and the account
the harness reports, so two runs on the same data give the same orders.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
MAX_SLIPPAGE_BPS = 100          # 1% past the close the order was decided on
ENTRY_WINDOW = 10               # bars of the entry momentum window
ENTRY_BPS = 60                  # enter when the 10-bar return tops 60 bps
STOP_BPS = 80                   # trailing stop below the position's peak close
TAKE_BPS = 100                  # take-profit: position worth 100 bps over cost
REVERSAL_BPS = 60               # exit when the 10-bar return falls below -60 bps
COOLDOWN_BARS = 30              # bars to wait after an exit before re-entering
NO_ENTRY_AFTER = 1380            # no new buys in the last hour: both windows
                                # are 1,440 bars, and paying ~17 bps of entry
                                # cost for under an hour of exposure is
                                # negative expected value

closes = []                     # closes of every bar seen, oldest first
peak_close = None               # highest close since the current position opened
last_exit_seq = -10 ** 9        # seq of the batch where the last exit filled


def ten_bar_return():
    """The log return of the last ENTRY_WINDOW bars, in basis points."""
    if len(closes) <= ENTRY_WINDOW:
        return None
    return 10000 * math.log(closes[-1] / closes[-1 - ENTRY_WINDOW])


def on_batch(state, batch):
    for bar in batch["bars"]:
        if bar["symbol"] == SYMBOL:
            closes.append(int(bar["c"]))

    held = state.positions.get(SYMBOL)
    qty = held.qty if held is not None else 0

    global peak_close, last_exit_seq
    if qty > 0:
        close = closes[-1]
        peak_close = close if peak_close is None else max(peak_close, close)
        value = state.value(SYMBOL, qty)
        cost = held.cost
        ret10 = ten_bar_return()
        exit_now = (
            close * 10000 <= peak_close * (10000 - STOP_BPS)
            or value * 10000 >= cost * (10000 + TAKE_BPS)
            or (ret10 is not None and ret10 < -REVERSAL_BPS)
        )
        if exit_now:
            last_exit_seq = state.seq
            return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []

    # Flat: reset the peak tracker and look for an entry.
    peak_close = None
    if state.seq - last_exit_seq < COOLDOWN_BARS:
        return []
    if state.seq >= NO_ENTRY_AFTER:
        return []
    ret10 = ten_bar_return()
    if ret10 is not None and ret10 > ENTRY_BPS:
        notional = state.cash
        if notional >= int(state.hello["fees"]["min_notional_quote_units"]):
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": notional,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch)

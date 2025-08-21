from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

import ccxt
import pandas as pd


def fetch_trades_to_parquet(exchange_id: str, symbol: str, limit: int = 500, out_path: str = 'data/trades.parquet') -> str:
    """Fetch recent trades via CCXT and write to a Parquet file.

    Creates the destination directory if needed.
    """
    ex = getattr(ccxt, exchange_id)()
    trades = ex.fetch_trades(symbol, limit=limit)
    df = pd.DataFrame(trades)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    return str(out)


def csv_to_vectorbt_signals(csv_path: str) -> pd.DataFrame:
    """Convert a run CSV (inventory_mm_run.csv) to a basic vectorbt signals frame.

    Returns a DataFrame with 'close', 'entries', 'exits' columns for quick vectorbt demo.
    """
    df = pd.read_csv(csv_path)
    # Use mid_price as close proxy
    out = pd.DataFrame()
    out['close'] = df['mid_price'].astype(float)
    # Define naive entries/exits from inventory changes
    inv = df['inventory'].astype(float).fillna(0)
    delta = inv.diff().fillna(0)
    out['entries'] = (delta > 0).astype(bool)
    out['exits'] = (delta < 0).astype(bool)
    return out
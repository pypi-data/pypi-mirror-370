from io import BytesIO
from typing import Dict

import numpy as np
import pandas as pd
from wbcore.contrib.io.models import ImportSource

from wbportfolio.models import Trade


def parse_row(obj: Dict, import_source: ImportSource) -> Dict:
    isin = obj["underlying_instrument__isin"]
    shares = obj["shares"]
    if import_source.source.import_parameters.get("negate_shares", False):
        shares = -1 * shares
    return {
        "underlying_instrument": {"isin": isin, "instrument_type": "product"},
        "portfolio": {"isin": isin, "instrument_type": "product"},
        "transaction_date": obj["transaction_date"].strftime("%Y-%m-%d"),
        "shares": shares,
        "bank": obj["custodian"],
        "transaction_subtype": Trade.Type.REDEMPTION if shares < 0 else Trade.Type.SUBSCRIPTION,
        "price": round(obj["price"], 6),
    }


def parse(import_source):
    df = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl")
    if "Trade Date" not in df.columns:
        xx, yy = np.where(df == "Trade Date")
        df = df.iloc[xx[0] :, yy[0] :]
        df = df.rename(columns=df.iloc[0]).drop(df.index[0]).dropna(how="all")
    df = df.rename(columns=lambda x: x.lower())
    df = df.rename(
        columns={
            "trade date": "transaction_date",
            "isin": "underlying_instrument__isin",
            "client side": "client_side",
            "net quantity": "shares",
            "price": "price",
            "custodian": "custodian",
            "name": "custodian",
            "buy/sell": "client_side",
            "nominal": "shares",
        }
    )
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["underlying_instrument__isin"] = df["underlying_instrument__isin"].str.strip()
    df = df.replace([np.inf, -np.inf, np.nan], None)
    df.loc[df["custodian"].isnull(), "custodian"] = "N/A"
    data = list()
    for d in df.to_dict("records"):
        data.append(parse_row(d, import_source))

    return {"data": data}

"""Order-level contribution-margin waterfall (reference implementation, synthetic).

Models the structure documented for the production semantic model: every cost
or income that touches an order is a separate, signed component, so margin can
be explained, not just reported. Rates and values below are illustrative only.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Tuple

# ---- time-variant dimension: seller indicator per channel and validity window ----
# (channel, valid_from, valid_to, indicator)
INDICATORS: List[Tuple[str, date, date, str]] = [
    ("CH_A", date(2026, 1, 1), date(2026, 1, 31), "GREEN"),
    ("CH_A", date(2026, 2, 1), date(2026, 2, 28), "LEVEL_3"),
    ("CH_B", date(2026, 1, 1), date(2026, 2, 28), "GREEN"),
]
# freight subsidy applied on the channel freight, depending on the indicator
FREIGHT_SUBSIDY = {"GREEN": 0.30, "LEVEL_3": 0.0}

# channel dimension: calculation group + fulfillment model
CHANNELS = {
    "CH_A": {"calc_group": "A", "model": "SELF", "commission": 0.14, "fixed_fee": 5.0},
    "CH_B": {"calc_group": "B", "model": "FULFILLED", "commission": 0.16, "fixed_fee": 0.0},
}


def indicator_on(channel: str, billing_date: date) -> str:
    """Pick the indicator valid on the billing date (no overlap allowed per channel)."""
    hits = [i for c, a, b, i in INDICATORS if c == channel and a <= billing_date <= b]
    if len(hits) > 1:
        raise ValueError("overlapping validity windows")
    return hits[0] if hits else "NONE"


@dataclass
class OrderLine:
    channel: str
    billing_date: date
    gross_sale: float           # paid by the customer, invoiced
    product_value: float        # final product price
    customer_freight: float
    product_cost: float         # purchase + duties + inbound freight
    channel_freight: float = 0.0
    own_freight: float = 0.0
    seller_discount: float = 0.0
    channel_discount_refund: float = 0.0
    rebates: float = 0.0
    supplier_funds: float = 0.0
    ads: float = 0.0
    fulfillment_cost: float = 0.0
    reverse_cost: float = 0.0
    support_cost: float = 0.0
    loss: float = 0.0
    tax_rate: float = 0.11
    extras: Dict[str, float] = field(default_factory=dict)


def waterfall(o: OrderLine) -> Dict[str, float]:
    ch = CHANNELS[o.channel]
    base = o.product_value                       # "base value" used to compute rates
    subsidy = FREIGHT_SUBSIDY.get(indicator_on(o.channel, o.billing_date), 0.0)
    c: Dict[str, float] = {
        "gross_sale": o.gross_sale,
        "commission": -base * ch["commission"],
        "channel_freight": -o.channel_freight * (1 - subsidy),
        "own_freight": -o.own_freight,
        "fixed_fee": -ch["fixed_fee"],
        "seller_discount": -o.seller_discount,
        "channel_discount_refund": o.channel_discount_refund,
        "rebates": o.rebates,
        "product_cost": -o.product_cost,
        "taxes": -o.gross_sale * o.tax_rate,
        "supplier_funds": o.supplier_funds,
        "ads": -o.ads,
        "fulfillment_cost": -o.fulfillment_cost,
        "reverse_logistics": -o.reverse_cost,
        "support": -o.support_cost,
        "loss": -o.loss,
    }
    # gross sale already includes what the customer paid (product + customer freight)
    c["contribution_margin"] = o.gross_sale + sum(v for k, v in c.items() if k != "gross_sale")
    return c


def margin_pct(o: OrderLine) -> float:
    w = waterfall(o)
    return w["contribution_margin"] / o.gross_sale if o.gross_sale else 0.0

import pathlib, sys
from datetime import date
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "reference_implementation"))
from margin_waterfall import OrderLine, indicator_on, waterfall, margin_pct


def line(**kw):
    base = dict(channel="CH_A", billing_date=date(2026, 1, 15), gross_sale=100.0, product_value=100.0,
                customer_freight=0.0, product_cost=50.0, channel_freight=10.0)
    base.update(kw)
    return OrderLine(**base)


def test_indicator_follows_validity_window():
    assert indicator_on("CH_A", date(2026, 1, 15)) == "GREEN"
    assert indicator_on("CH_A", date(2026, 2, 15)) == "LEVEL_3"
    assert indicator_on("CH_A", date(2025, 12, 31)) == "NONE"


def test_freight_subsidy_depends_on_billing_month():
    jan = waterfall(line())["channel_freight"]
    feb = waterfall(line(billing_date=date(2026, 2, 15)))["channel_freight"]
    assert round(jan, 2) == -7.0 and round(feb, 2) == -10.0


def test_margin_value_matches_hand_calculation():
    # 100 - 14 commission - 7 freight (30% subsidy) - 5 fixed fee - 50 cost - 11 taxes
    assert round(waterfall(line())["contribution_margin"], 2) == 13.0


def test_every_component_is_explained():
    w = waterfall(line(ads=3.0, loss=2.0))
    parts = sum(v for k, v in w.items() if k != "contribution_margin")
    assert round(parts, 6) == round(w["contribution_margin"], 6)


def test_margin_pct_drops_with_ads():
    assert margin_pct(line(ads=10.0)) < margin_pct(line())

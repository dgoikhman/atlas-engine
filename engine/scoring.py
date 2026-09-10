"""Atlas Engine — scoring.
One framework, one named index per atlas. A new atlas = a new config block.
Every factor maps raw metrics to 0-100; the index is the weighted sum.
"""

def clamp01(x):
    return max(0.0, min(1.0, x))

# ---------------- Rentals: the Star Score ----------------
# Factors read a metro dict with keys:
# home_value, rent, landlord (0-100), tax_rate (%), growth (0-100), climate (0-100)

RENTALS = {
    "index_name": "Star Score",
    "factors": {
        "gross_yield": {
            "label": "Gross yield",
            "weight": 0.35,
            "fn": lambda m: clamp01(((m["rent"] * 12 / m["home_value"]) - 0.045) / 0.035) * 100,
            "display": lambda m: f"{m['rent']*12/m['home_value']*100:.1f}%",
        },
        "entry": {
            "label": "Entry price (vs $100K reference budget)",
            "weight": 0.15,
            "fn": lambda m: clamp01((340000 - m["home_value"]) / 140000) * 100,
        },
        "landlord": {
            "label": "Landlord-friendliness",
            "weight": 0.15,
            "fn": lambda m: float(m["landlord"]),
        },
        "growth": {
            "label": "Equity growth",
            "weight": 0.15,
            "fn": lambda m: float(m["growth"]),
        },
        "tax": {
            "label": "Property-tax drag (inverted)",
            "weight": 0.10,
            "fn": lambda m: clamp01((2.2 - m["tax_rate"]) / 1.8) * 100,
        },
        "climate": {
            "label": "Climate & insurance risk (inverted)",
            "weight": 0.10,
            "fn": lambda m: float(m["climate"]),
        },
    },
}

# Future configs, same shape:
# FRANCHISES -> "Zee Score": item7 cost vs category, item19 disclosure quality,
#               unit growth (item20 3yr), closure rate, litigation flags.
# STR       -> "Stay Score": STR revenue yield vs purchase price, regulation
#               risk (ordinance tier), seasonality, host concentration.
# MAINSTREET-> "Succession Score": owner-age proxies, registry age, digital
#               weakness, density gap vs demand.

# ---------------- Main Street: the Succession Score (v0.1, registry-only) --
import math

MAINSTREET = {
    "index_name": "Succession Score",
    "factors": {
        "share20": {
            "label": "Share of businesses 20+ years old",
            "weight": 0.45,
            "fn": lambda m: clamp01((m["share20"] - 5) / 25) * 100,
        },
        "share30": {
            "label": "Share 30+ years old",
            "weight": 0.25,
            "fn": lambda m: clamp01((m["share30"] - 2) / 13) * 100,
        },
        "depth": {
            "label": "Depth of aged businesses (count)",
            "weight": 0.30,
            "fn": lambda m: clamp01(math.log10(max(m["over20"], 1)) / 4) * 100,
        },
    },
}

CONFIGS = {"rentals": RENTALS, "mainstreet": MAINSTREET}


def compute(atlas: str, m: dict):
    cfg = CONFIGS[atlas]
    factors = {}
    total = 0.0
    for key, f in cfg["factors"].items():
        s = f["fn"](m)
        factors[key] = {"label": f["label"], "score": round(s), "weight": f["weight"]}
        total += f["weight"] * s
    return round(total, 1), factors


def stars(score: float) -> str:
    """0-100 -> unicode star string in half-star steps."""
    half = round(score / 10)
    full, rem = divmod(half, 2)
    return "★" * full + ("½" if rem else "") + "☆" * (5 - full - rem)

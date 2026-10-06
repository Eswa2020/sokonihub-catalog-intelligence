"""Gates analytics outputs on the reference fixture.

- Category rates are internally consistent and sum to overall.
- Bags has n >= 2 and a lower flag rate than shoes.
- Search for "kiondo" ranks KND-01 above NK-99.
"""
import json
from pathlib import Path

from search import search

ROOT = Path(__file__).resolve().parent


def main() -> int:
    try:
        rates = json.loads((ROOT / "rates.json").read_text(encoding="utf-8"))
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        print("FAIL: missing", e.filename, "- run analytics.py first")
        return 1

    cats = {k: v for k, v in rates.items() if k != "overall"}
    for name, r in rates.items():
        expected = round(r["n_flagged"] / r["n"], 4) if r["n"] else 0.0
        if r["flag_rate"] != expected:
            print(f"FAIL {name}: flag_rate {r['flag_rate']} != {expected}")
            return 1
    if sum(r["n"] for r in cats.values()) != rates["overall"]["n"]:
        print("FAIL: category n does not sum to overall")
        return 1
    if sum(r["n_flagged"] for r in cats.values()) != rates["overall"]["n_flagged"]:
        print("FAIL: category n_flagged does not sum to overall")
        return 1
    if rates["bags"]["n"] < 2:
        print("FAIL: bags needs n >= 2")
        return 1
    if not rates["bags"]["flag_rate"] < rates["shoes"]["flag_rate"]:
        print("FAIL: expected bags flag_rate below shoes on the reference fixture")
        return 1
    print(f"OK   rates consistent; bags {rates['bags']['flag_rate']} < shoes {rates['shoes']['flag_rate']}")

    ranking = [sku for _, sku in search("kiondo", catalog, k=len(catalog))]
    if ranking.index("KND-01") > ranking.index("NK-99"):
        print("FAIL: KND-01 must rank above NK-99 for 'kiondo'")
        return 1
    print(f"OK   search 'kiondo' top result {ranking[0]}")
    print("analytics OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
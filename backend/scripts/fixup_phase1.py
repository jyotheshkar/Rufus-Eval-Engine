# One-off fixup script: adds 100 synthetic products and corrects question intent distribution
import json
import random
from pathlib import Path

random.seed(42)

PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"
QUESTIONS_PATH = Path(__file__).parent.parent / "data" / "questions.json"

# ---------------------------------------------------------------------------
# 1. Add 100 synthetic products (10 per category, no API call)
# ---------------------------------------------------------------------------

CATEGORY_TEMPLATES = {
    "headphones": {
        "brands": ["Sony", "Bose", "Sennheiser", "JBL", "Audio-Technica", "Beyerdynamic", "AKG", "Jabra", "Plantronics", "Skullcandy"],
        "names": ["Wireless Pro", "Studio Elite", "Bass Boost X", "Comfort Plus", "Active SE", "Clarity HD", "Sport Edition", "Travel Compact", "Studio Reference", "Urban Series"],
        "price_range": (29.99, 399.99),
        "tags": ["wireless", "noise-cancelling", "premium", "budget", "sport"],
        "specs": {"battery_life": ["20 hours", "30 hours", "40 hours", "15 hours"], "connectivity": ["Bluetooth 5.0", "Bluetooth 5.2", "Bluetooth 5.3", "Wired 3.5mm"]},
    },
    "laptops": {
        "brands": ["Dell", "HP", "Lenovo", "Asus", "Acer", "Microsoft", "Samsung", "LG", "Razer", "MSI"],
        "names": ["ProBook 15", "XPS Ultra", "ThinkPad X1", "VivoBook 14", "Aspire 5", "Surface Laptop", "Galaxy Book", "Gram 16", "Blade 15", "Prestige 14"],
        "price_range": (299.99, 1999.99),
        "tags": ["ultrabook", "gaming", "business", "student", "lightweight"],
        "specs": {"battery_life": ["8 hours", "12 hours", "15 hours", "10 hours"], "connectivity": ["Wi-Fi 6", "Wi-Fi 6E", "Wi-Fi 5"]},
    },
    "smartphones": {
        "brands": ["Samsung", "Google", "OnePlus", "Xiaomi", "Motorola", "Nokia", "Oppo", "Realme", "Nothing", "Fairphone"],
        "names": ["Galaxy A55", "Pixel 8a", "12T Pro", "13 Pro", "Edge 40", "G60", "Find X7", "GT Neo", "Phone 2a", "4"],
        "price_range": (149.99, 1099.99),
        "tags": ["5G", "camera", "battery", "android", "midrange"],
        "specs": {"battery_life": ["24 hours", "36 hours", "48 hours"], "connectivity": ["5G", "4G LTE", "5G mmWave"]},
    },
    "tablets": {
        "brands": ["Samsung", "Lenovo", "Amazon", "Huawei", "TCL", "Alcatel", "Xiaomi", "Realme"],
        "names": ["Tab S9 FE", "Tab P12", "Fire HD 10", "MatePad 11", "Tab 10s", "1T 10", "Pad 6", "Pad"],
        "price_range": (79.99, 699.99),
        "tags": ["android", "kids", "productivity", "drawing", "entertainment"],
        "specs": {"battery_life": ["10 hours", "12 hours", "14 hours"], "connectivity": ["Wi-Fi", "Wi-Fi + 4G", "Wi-Fi 6"]},
    },
    "smartwatches": {
        "brands": ["Garmin", "Fitbit", "Amazfit", "Fossil", "Withings", "Polar", "Suunto", "Mobvoi"],
        "names": ["Venu 3", "Charge 6", "GTR 4", "Gen 6", "ScanWatch 2", "Ignite 3", "Race", "TicWatch Pro"],
        "price_range": (49.99, 499.99),
        "tags": ["fitness", "GPS", "heart-rate", "sleep-tracking", "sports"],
        "specs": {"battery_life": ["5 days", "7 days", "14 days", "21 days"], "connectivity": ["Bluetooth 5.0", "Bluetooth 5.2", "Wi-Fi + Bluetooth"]},
    },
    "cameras": {
        "brands": ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic", "Olympus", "Leica", "Pentax"],
        "names": ["EOS R50", "Z30", "ZV-E10", "X-S20", "G100", "OM-5", "Q3", "K-70"],
        "price_range": (299.99, 2499.99),
        "tags": ["mirrorless", "DSLR", "vlogging", "4K", "beginner"],
        "specs": {"battery_life": ["300 shots", "450 shots", "600 shots"], "connectivity": ["Wi-Fi + Bluetooth", "Wi-Fi", "USB-C"]},
    },
    "speakers": {
        "brands": ["JBL", "Bose", "Ultimate Ears", "Sony", "Marshall", "Harman Kardon", "Bang & Olufsen", "Tribit"],
        "names": ["Charge 6", "SoundLink Flex", "Boom 3", "XB43", "Emberton III", "Onyx Studio 8", "Beosound A1", "StormBox Pro"],
        "price_range": (29.99, 449.99),
        "tags": ["portable", "waterproof", "bluetooth", "outdoor", "360-sound"],
        "specs": {"battery_life": ["12 hours", "17 hours", "24 hours", "30 hours"], "connectivity": ["Bluetooth 5.3", "Bluetooth 5.1", "Wi-Fi + Bluetooth"]},
    },
    "gaming": {
        "brands": ["Razer", "Logitech", "SteelSeries", "Corsair", "HyperX", "ASUS ROG", "MSI", "NZXT"],
        "names": ["DeathAdder V3", "G Pro X", "Rival 3", "Dark Core", "Pulsefire", "Gladius III", "Clutch GM41", "Lift"],
        "price_range": (19.99, 249.99),
        "tags": ["gaming", "RGB", "wireless", "mechanical", "FPS"],
        "specs": {"battery_life": ["70 hours", "100 hours", "N/A"], "connectivity": ["USB", "2.4GHz wireless", "Bluetooth + 2.4GHz"]},
    },
    "monitors": {
        "brands": ["LG", "Samsung", "BenQ", "Asus", "Dell", "AOC", "Acer", "Philips"],
        "names": ["27UK850", "Odyssey G5", "PD2705U", "ProArt PA278", "U2722D", "27G2", "Nitro XV272U", "279P1"],
        "price_range": (129.99, 999.99),
        "tags": ["4K", "gaming", "IPS", "HDR", "ultrawide"],
        "specs": {"battery_life": [None], "connectivity": ["HDMI + DisplayPort", "USB-C + HDMI", "DisplayPort 1.4"]},
    },
    "accessories": {
        "brands": ["Anker", "Belkin", "Logitech", "Satechi", "HyperDrive", "Ugreen", "AUKEY", "Baseus"],
        "names": ["PowerCore 26800", "BoostCharge Pro", "MX Keys Mini", "Pro Hub", "USB-C Hub", "USB-C Docking", "65W Charger", "Speed Pro"],
        "price_range": (9.99, 149.99),
        "tags": ["USB-C", "wireless", "charging", "portable", "hub"],
        "specs": {"battery_life": [None], "connectivity": ["USB-C", "USB-A + USB-C", "Bluetooth 5.0"]},
    },
}


def make_product(category: str, template: dict, prod_id: int, idx: int) -> dict:
    """Build one synthetic product for a given category."""
    brand = template["brands"][idx % len(template["brands"])]
    name_suffix = template["names"][idx % len(template["names"])]
    price = round(
        template["price_range"][0]
        + (template["price_range"][1] - template["price_range"][0]) * random.random(),
        2,
    )
    battery_opts = template["specs"]["battery_life"]
    connectivity_opts = template["specs"]["connectivity"]
    battery = random.choice(battery_opts)
    connectivity = random.choice(connectivity_opts)
    colors = random.sample(["Black", "White", "Silver", "Blue", "Red", "Green", "Grey", "Rose Gold"], k=random.randint(1, 3))
    tags = random.sample(template["tags"], k=min(3, len(template["tags"])))

    return {
        "id": f"prod_{prod_id:04d}",
        "name": f"{brand} {name_suffix}",
        "category": category,
        "price": price,
        "currency": "GBP",
        "rating": round(random.uniform(3.5, 5.0), 1),
        "review_count": random.randint(50, 15000),
        "brand": brand,
        "description": (
            f"The {brand} {name_suffix} is a high-quality {category[:-1] if category.endswith('s') else category} "
            f"designed for everyday use. It offers excellent performance and reliability at its price point. "
            f"A popular choice among customers looking for {tags[0]} features."
        ),
        "specs": {
            "battery_life": battery,
            "connectivity": connectivity,
            "weight": f"{random.randint(80, 800)}g",
            "waterproof": random.choice([True, False]),
            "color": colors,
        },
        "tags": tags,
        "in_stock": random.choice([True, True, True, False]),
        "embedding": [],
    }


def add_products() -> None:
    with open(PRODUCTS_PATH) as f:
        products = json.load(f)

    current_count = len(products)
    target_count = 1000
    needed = target_count - current_count
    print(f"Products: {current_count} -> adding {needed} to reach {target_count}")

    next_id = current_count + 1
    cats = list(CATEGORY_TEMPLATES.keys())  # 10 categories
    per_cat = needed // len(cats)           # 10 each
    remainder = needed % len(cats)

    for i, category in enumerate(cats):
        count = per_cat + (1 if i < remainder else 0)
        template = CATEGORY_TEMPLATES[category]
        for j in range(count):
            products.append(make_product(category, template, next_id, j))
            next_id += 1

    with open(PRODUCTS_PATH, "w") as f:
        json.dump(products, f, indent=2)

    from collections import Counter
    counts = Counter(p["category"] for p in products)
    print(f"Total products now: {len(products)}")
    for cat, cnt in sorted(counts.items()):
        print(f"  {cat}: {cnt}")


# ---------------------------------------------------------------------------
# 2. Fix question intent distribution
# ---------------------------------------------------------------------------

TARGET = {
    "recommendation": 60,
    "comparison": 40,
    "specific_question": 50,
    "budget_query": 30,
    "feature_query": 20,
}


def fix_questions() -> None:
    with open(QUESTIONS_PATH) as f:
        questions = json.load(f)

    from collections import Counter
    current = Counter(q["intent"] for q in questions)
    print(f"\nQuestion intents before: {dict(current)}")

    # Build a pool of indices per intent to draw from when we need to reassign
    pools: dict[str, list[int]] = {intent: [] for intent in TARGET}
    for i, q in enumerate(questions):
        if q["intent"] in pools:
            pools[q["intent"]].append(i)

    # Calculate how many to take FROM each intent and how many to add TO each intent
    deficits = {intent: TARGET[intent] - current[intent] for intent in TARGET}
    # Positive deficit = need more; negative = need fewer

    sources: list[tuple[int, str]] = []  # (question_idx, new_intent)

    # Take from over-represented intents, assign to under-represented
    to_give: list[int] = []
    for intent, delta in deficits.items():
        if delta < 0:  # over-represented — take away abs(delta) questions
            indices = pools[intent][:]
            random.shuffle(indices)
            for idx in indices[: abs(delta)]:
                to_give.append(idx)

    # Distribute to under-represented intents
    ptr = 0
    for intent, delta in deficits.items():
        if delta > 0:
            for _ in range(delta):
                if ptr < len(to_give):
                    sources.append((to_give[ptr], intent))
                    ptr += 1

    for idx, new_intent in sources:
        questions[idx]["intent"] = new_intent

    after = Counter(q["intent"] for q in questions)
    print(f"Question intents after:  {dict(after)}")

    with open(QUESTIONS_PATH, "w") as f:
        json.dump(questions, f, indent=2)

    print("questions.json saved.")


if __name__ == "__main__":
    add_products()
    fix_questions()
    print("\nFixup complete.")

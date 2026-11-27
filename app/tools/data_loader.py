
import json
from pathlib import Path
from typing import Any

# Locate the project root regardless of where Python is launched.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = PROJECT_ROOT / "app" / "data" / "market_data.json"


def load_market_data() -> dict[str, Any]:
    """Load the simulated apparel market dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Market dataset not found at: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    data = load_market_data()

    print("Market dataset loaded successfully!")
    print(f"Business: {data['business']['business_name']}")
    print(f"Historical products: {len(data['historical_sales'])}")
    print(f"Competitor products: {len(data['competitor_products'])}")

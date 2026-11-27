
import json
from pathlib import Path
from typing import Any
from math import ceil, isfinite


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_FILE = PROJECT_ROOT / "app" / "data" / "inventory.json"

COMMITTED_STATUSES = {
    "approved",
    "confirmed",
    "in_transit",
}


def load_inventory_data() -> dict[str, Any]:
    """Load simulated inventory data."""

    if not INVENTORY_FILE.exists():
        raise FileNotFoundError(
            f"Inventory dataset not found: {INVENTORY_FILE}"
        )

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_units(value: Any, field: str) -> int:
    """Validate non-negative integer inventory quantities."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer.")

    if value < 0:
        raise ValueError(f"{field} cannot be negative.")

    return value


def calculate_inventory_position(
    inventory_item: dict[str, Any],
    forecast_horizon_days: int,
    safety_stock_multiplier: float = 1.0,
) -> dict[str, Any]:
    """
    Calculate inventory position for one product.

    Incoming orders only count if:
    1. They have a committed status.
    2. They are expected to arrive within the forecast horizon.
    """

    if (
        isinstance(safety_stock_multiplier, bool)
        or not isinstance(safety_stock_multiplier, (int, float))
        or not isfinite(safety_stock_multiplier)
        or safety_stock_multiplier < 0
    ):
        raise ValueError(
            "Safety stock multiplier must be finite and non-negative."
        )

    product = inventory_item["product"]

    on_hand = validate_units(
        inventory_item["on_hand_units"],
        "on_hand_units",
    )

    reserved = validate_units(
        inventory_item["reserved_units"],
        "reserved_units",
    )

    original_safety_stock = validate_units(
        inventory_item["safety_stock_units"],
        "safety_stock_units",
    )

    safety_stock = ceil(
        original_safety_stock * safety_stock_multiplier
    )

    available_stock = max(0, on_hand - reserved)
    stock_shortfall = max(0, reserved - on_hand)

    incoming_within_horizon = 0
    incoming_after_horizon = 0
    committed_order_ids = []

    for order in inventory_item.get("incoming_orders", []):

        quantity = validate_units(
            order["quantity"],
            "incoming order quantity",
        )

        arrival_days = validate_units(
            order["expected_arrival_days"],
            "expected_arrival_days",
        )

        status = order["status"].lower()

        if status not in COMMITTED_STATUSES:
            continue

        if arrival_days <= forecast_horizon_days:
            incoming_within_horizon += quantity
            committed_order_ids.append(order["order_id"])
        else:
            incoming_after_horizon += quantity

    inventory_position = (
        on_hand - reserved + incoming_within_horizon
    )

    return {
        "product": product,
        "on_hand_units": on_hand,
        "reserved_units": reserved,
        "available_stock": available_stock,
        "stock_shortfall": stock_shortfall,
        "incoming_units": incoming_within_horizon,
        "incoming_after_horizon": incoming_after_horizon,
        "committed_order_ids": committed_order_ids,
        "safety_stock_units": safety_stock,
        "inventory_position": inventory_position,
    }


def calculate_replenishment_requirements(
    inventory_data: dict[str, Any],
    forecast_result: dict[str, Any],
    safety_stock_multiplier: float = 1.0,
) -> dict[str, Any]:
    """
    Combine inventory positions with forecast demand.

    This calculates replenishment requirements before applying
    supplier MOQs, order multiples or budget constraints.
    """

    horizon_days = forecast_result["forecast_horizon_days"]

    if not isinstance(horizon_days, int) or isinstance(horizon_days, bool):
        raise ValueError("Forecast horizon must be an integer.")

    if horizon_days <= 0:
        raise ValueError("Forecast horizon must be positive.")

    inventory_items = inventory_data.get("inventory", [])
    forecasts = forecast_result.get("forecasts", [])

    if not inventory_items:
        raise ValueError("Inventory dataset is empty.")

    if not forecasts:
        raise ValueError("Forecast dataset is empty.")

    inventory_by_product = {}
    forecasts_by_product = {}

    for item in inventory_items:
        product = item["product"]

        if product in inventory_by_product:
            raise ValueError(f"Duplicate inventory product: {product}")

        inventory_by_product[product] = item

    for forecast in forecasts:
        product = forecast["product"]

        if product in forecasts_by_product:
            raise ValueError(f"Duplicate forecast product: {product}")

        if forecast["forecast_period_days"] != horizon_days:
            raise ValueError(
                f"Forecast horizon mismatch for {product}."
            )

        forecast_units = validate_units(
            forecast["forecast_units"],
            "forecast_units",
        )

        forecasts_by_product[product] = forecast_units

    if set(inventory_by_product) != set(forecasts_by_product):
        raise ValueError(
            "Inventory and forecast products must match exactly."
        )

    replenishment = []

    for product, inventory_item in inventory_by_product.items():

        inventory = calculate_inventory_position(
            inventory_item,
            horizon_days,
            safety_stock_multiplier,
        )

        forecast_units = forecasts_by_product[product]

        target_stock = (
            forecast_units + inventory["safety_stock_units"]
        )

        replenishment_need = max(
            0,
            target_stock - inventory["inventory_position"],
        )

        replenishment.append({
            **inventory,
            "forecast_demand": forecast_units,
            "forecast_horizon_days": horizon_days,
            "target_stock": target_stock,
            "replenishment_quantity": replenishment_need,
            "status": (
                "Replenishment required"
                if replenishment_need > 0
                else "Sufficient inventory"
            ),
        })

    return {
        "dataset_type": inventory_data.get(
            "metadata", {}
        ).get("dataset_type", "unknown"),
        "forecast_horizon_days": horizon_days,
        "product_count": len(replenishment),
        "total_replenishment_units": sum(
            item["replenishment_quantity"]
            for item in replenishment
        ),
        "replenishment": replenishment,
    }


def print_inventory_report(
    result: dict[str, Any],
) -> None:
    """Print a readable inventory and replenishment report."""

    print("\nSTOCKLINE INVENTORY INTELLIGENCE")
    print("=" * 70)

    print(f"Dataset: {result['dataset_type']}")
    print(f"Forecast horizon: {result['forecast_horizon_days']} days")
    print(f"Products analysed: {result['product_count']}")
    print(
        f"Total replenishment requirement: "
        f"{result['total_replenishment_units']} units"
    )

    for item in result["replenishment"]:

        print(f"\n{item['product']}")
        print("-" * 50)

        print(f"Physical stock: {item['on_hand_units']}")
        print(f"Reserved stock: {item['reserved_units']}")
        print(f"Available stock: {item['available_stock']}")
        print(f"Incoming stock: {item['incoming_units']}")
        print(f"Safety stock: {item['safety_stock_units']}")
        print(f"Forecast demand: {item['forecast_demand']}")
        print(f"Target stock: {item['target_stock']}")

        print(
            f"Inventory position: {item['inventory_position']}"
        )

        print(
            f"Replenishment required: "
            f"{item['replenishment_quantity']}"
        )

        print(f"Status: {item['status']}")


if __name__ == "__main__":
    from app.tools.data_loader import load_market_data
    from app.tools.demand_forecaster import forecast_demand

    market_data = load_market_data()
    inventory_data = load_inventory_data()

    forecasts = forecast_demand(
        market_data=market_data,
        horizon_days=30,
        historical_period_days=90,
    )

    result = calculate_replenishment_requirements(
        inventory_data=inventory_data,
        forecast_result=forecasts,
    )

    print_inventory_report(result)

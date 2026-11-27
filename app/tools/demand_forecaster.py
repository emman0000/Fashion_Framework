
from math import ceil
from typing import Any


def forecast_demand(
    market_data: dict[str, Any],
    horizon_days: int = 30,
    historical_period_days: int = 90,
    product_adjustments: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    """
    Generate transparent simulated demand forecasts.

    This is a historical baseline model, NOT a trained ML model.

    Historical sales are scaled to the requested forecast horizon.
    Optional seasonal and market adjustments can be applied per product.
    """

    if horizon_days <= 0:
        raise ValueError("Forecast horizon must be positive.")

    if historical_period_days <= 0:
        raise ValueError("Historical period must be positive.")

    if product_adjustments is None:
        product_adjustments = {}

    historical_sales = market_data.get("historical_sales")

    if not historical_sales:
        raise ValueError("Historical sales data is missing.")

    forecasts = []
    seen_products = set()

    for sale in historical_sales:
        product = sale["product"]

        if product in seen_products:
            raise ValueError(f"Duplicate historical product: {product}")

        seen_products.add(product)

        historical_units = int(sale["units_sold"])

        if historical_units < 0:
            raise ValueError(
                f"Historical demand cannot be negative: {product}"
            )

        adjustments = product_adjustments.get(product, {})

        seasonal_index = float(
            adjustments.get("seasonality_index", 1.0)
        )

        market_index = float(
            adjustments.get("market_demand_index", 1.0)
        )

        if seasonal_index < 0 or market_index < 0:
            raise ValueError(
                f"Forecast adjustments cannot be negative: {product}"
            )

        baseline_demand = (
            historical_units
            * horizon_days
            / historical_period_days
        )

        adjusted_demand = (
            baseline_demand
            * seasonal_index
            * market_index
        )

        forecast_units = ceil(adjusted_demand)

        forecasts.append({
            "product": product,
            "category": sale["category"],
            "historical_units_sold": historical_units,
            "forecast_units": forecast_units,
            "forecast_period_days": horizon_days,
            "baseline_demand": round(baseline_demand, 2),
            "seasonality_index": seasonal_index,
            "market_demand_index": market_index,
            "method": "simulated_historical_baseline",
            "confidence": "low",
            "assumptions": [
                f"Historical sales represent {historical_period_days} days",
                "Historical demand is used as the baseline",
                "Seasonality adjustment is explicitly configurable",
                "Market demand adjustment is explicitly configurable",
                "No trained machine learning model is used",
            ],
        })

    return {
        "forecast_type": "simulated",
        "forecast_horizon_days": horizon_days,
        "historical_period_days": historical_period_days,
        "forecast_count": len(forecasts),
        "forecasts": forecasts,
    }


def print_forecasts(result: dict[str, Any]) -> None:
    """Print demand forecasts in a readable format."""

    print("\nSTOCKLINE DEMAND FORECAST")
    print("=" * 65)

    print(f"Forecast type: {result['forecast_type']}")
    print(f"Forecast horizon: {result['forecast_horizon_days']} days")
    print(f"Products forecast: {result['forecast_count']}")

    print("\nPRODUCT FORECASTS")
    print("-" * 65)

    for item in result["forecasts"]:
        print(f"\n{item['product']}")
        print(f"Historical sales: {item['historical_units_sold']}")
        print(f"Forecast demand: {item['forecast_units']} units")
        print(f"Forecast confidence: {item['confidence']}")
        print(f"Method: {item['method']}")


if __name__ == "__main__":
    from app.tools.data_loader import load_market_data

    data = load_market_data()

    forecasts = forecast_demand(
        market_data=data,
        horizon_days=30,
        historical_period_days=90,
    )

    print_forecasts(forecasts)

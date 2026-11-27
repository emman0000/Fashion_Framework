"""ADK-compatible tools connecting Stockline agents to business logic."""

from typing import Any

from app.tools.data_loader import load_market_data
from app.tools.demand_forecaster import forecast_demand
from app.tools.inventory_manager import (
    load_inventory_data,
    calculate_replenishment_requirements,
)
from app.tools.product_evaluator import evaluate_products, rank_products
from app.tools.risk_controller import apply_risk_strategy
from app.tools.purchasing_optimizer import optimise_purchase_allocation


def get_market_overview() -> dict[str, Any]:
    """Return business context, customer insights and supplier catalogue."""
    data = load_market_data()

    return {
        "metadata": data["metadata"],
        "business": data["business"],
        "customer_insights": data["customer_insights"],
        "competitor_products": data["competitor_products"],
        "supplier_catalog": data["supplier_catalog"],
    }


def get_supplier_information() -> list[dict[str, Any]]:
    """Return supplier costs, minimum order quantities and lead times."""
    return load_market_data()["supplier_catalog"]


def evaluate_and_rank_products() -> list[dict[str, Any]]:
    """Evaluate and rank products using the existing scoring engine."""
    data = load_market_data()
    evaluations = evaluate_products(data)
    return rank_products(evaluations)


def generate_demand_forecast(horizon_days: int = 30) -> dict[str, Any]:
    """Generate the historical-baseline demand forecast."""
    if not 1 <= horizon_days <= 365:
        return {"error": "Forecast horizon must be between 1 and 365 days."}

    return forecast_demand(
        market_data=load_market_data(),
        horizon_days=horizon_days,
    )


def analyse_inventory(
    horizon_days: int = 30,
    safety_stock_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Calculate inventory positions and replenishment requirements."""
    if not 1 <= horizon_days <= 365:
        return {"error": "Forecast horizon must be between 1 and 365 days."}

    if not 0 <= safety_stock_multiplier <= 3:
        return {"error": "Safety stock multiplier must be between 0 and 3."}

    market_data = load_market_data()
    inventory_data = load_inventory_data()

    forecast = forecast_demand(
        market_data=market_data,
        horizon_days=horizon_days,
    )

    return calculate_replenishment_requirements(
        inventory_data=inventory_data,
        forecast_result=forecast,
        safety_stock_multiplier=safety_stock_multiplier,
    )


def assess_purchasing_risk(
    strategy_name: str = "balanced",
) -> dict[str, Any]:
    """Apply the selected risk policy to the ranked product portfolio."""
    data = load_market_data()
    ranked_products = evaluate_and_rank_products()

    return apply_risk_strategy(
        ranked_products=ranked_products,
        budget=data["business"]["purchasing_budget"],
        strategy_name=strategy_name,
    )


def optimise_purchasing(
    strategy_name: str = "balanced",
) -> dict[str, Any]:
    """Create an optimised purchase recommendation; never place an order."""
    data = load_market_data()
    ranked_products = evaluate_and_rank_products()
    risk_assessment = assess_purchasing_risk(strategy_name)

    replenishment = analyse_inventory(
        horizon_days=30,
        safety_stock_multiplier=1.0,
    )

    return optimise_purchase_allocation(
        ranked_products=ranked_products,
        replenishment_result=replenishment,
        risk_assessment=risk_assessment,
    )
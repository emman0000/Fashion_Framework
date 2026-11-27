
from math import ceil, floor
from typing import Any


def validate_non_negative_number(
    value: Any,
    field: str,
) -> float:
    """Validate a non-negative finite numeric value."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric.")

    number = float(value)

    if number < 0 or not __import__("math").isfinite(number):
        raise ValueError(f"{field} must be finite and non-negative.")

    return number
def round_to_supplier_constraints(
    quantity: int,
    minimum_order: int,
    order_multiple: int = 1,
) -> int:
    """
    Round a purchase quantity up to satisfy supplier MOQ
    and order-multiple requirements.
    """

    if quantity <= 0:
        return 0

    if minimum_order <= 0:
        raise ValueError("Minimum order must be positive.")

    if order_multiple <= 0:
        raise ValueError("Order multiple must be positive.")

    quantity_adjusted = ceil(quantity / order_multiple) * order_multiple

    minimum_adjusted = (
        ceil(minimum_order / order_multiple) * order_multiple
    )

    return max(quantity_adjusted, minimum_adjusted)


def create_purchase_plan(
    ranked_products: list[dict[str, Any]],
    replenishment_result: dict[str, Any],
    budget: float,
    risk_assessment: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a risk-adjusted proposed purchase plan.

    Enforces:
    - Product eligibility from the risk controller.
    - Strategy-specific spending ceilings.
    - Inventory replenishment requirements.
    - Supplier MOQs and order multiples.
    """

    budget = validate_non_negative_number(
        budget,
        "Purchasing budget",
    )

    if not ranked_products:
        raise ValueError("No ranked products supplied.")

    if risk_assessment["available_budget"] != round(budget, 2):
        raise ValueError("Risk assessment budget does not match.")

    replenishment_items = replenishment_result.get(
        "replenishment", []
    )

    replenishment_by_product = {
        item["product"]: item
        for item in replenishment_items
    }

    if len(replenishment_by_product) != len(replenishment_items):
        raise ValueError("Duplicate replenishment products.")

    ranked_by_product = {
        item["product"]: item
        for item in ranked_products
    }

    if len(ranked_by_product) != len(ranked_products):
        raise ValueError("Duplicate ranked products.")

    if set(ranked_by_product) != set(replenishment_by_product):
        raise ValueError(
            "Ranked and replenishment products must match."
        )

    eligible_products = set(
        risk_assessment["eligible_products"]
    )

    excluded_products = {
        item["product"]: item
        for item in risk_assessment["excluded_products"]
    }

    maximum_budget = min(
        budget,
        risk_assessment["maximum_purchasing_budget"],
    )

    remaining_budget = maximum_budget
    purchase_orders = []

    total_units = 0
    total_cost = 0.0

    for product in ranked_products:

        product_name = product["product"]
        inventory = replenishment_by_product[product_name]

        unit_cost = validate_non_negative_number(
            product["supplier_unit_cost"],
            f"{product_name} supplier cost",
        )

        minimum_order = product["minimum_order_quantity"]
        order_multiple = product.get("order_multiple", 1)

        if not isinstance(minimum_order, int) or isinstance(minimum_order, bool) or minimum_order <= 0:
            raise ValueError(f"Invalid MOQ for {product_name}.")

        if not isinstance(order_multiple, int) or isinstance(order_multiple, bool) or order_multiple <= 0:
            raise ValueError(
                f"Invalid order multiple for {product_name}."
            )

        lead_time = product["supplier_lead_time_days"]

        if not isinstance(lead_time, int) or isinstance(lead_time, bool) or lead_time < 0:
            raise ValueError(
                f"Invalid lead time for {product_name}."
            )

        required_quantity = inventory["replenishment_quantity"]

        if (
            not isinstance(required_quantity, int)
            or isinstance(required_quantity, bool)
            or required_quantity < 0
        ):
            raise ValueError(
                f"Invalid replenishment quantity for {product_name}."
            )

        # Products excluded by the selected risk strategy
        # cannot receive a purchase recommendation.
        if product_name not in eligible_products:

            exclusion = excluded_products.get(product_name, {})

            purchase_orders.append({
                "product": product_name,
                "rank": product["rank"],
                "required_quantity": required_quantity,
                "recommended_quantity": 0,
                "unit_cost": round(unit_cost, 2),
                "total_cost": 0.0,
                "minimum_order_quantity": minimum_order,
                "order_multiple": order_multiple,
                "lead_time_days": lead_time,
                "status": "Excluded by risk strategy",
                "reason": exclusion.get(
                    "reason",
                    "Product is not eligible.",
                ),
            })

            continue

        if unit_cost <= 0:
            raise ValueError(
                f"Supplier cost must be positive for {product_name}."
            )

        if required_quantity == 0:

            purchase_orders.append({
                "product": product_name,
                "rank": product["rank"],
                "required_quantity": 0,
                "recommended_quantity": 0,
                "unit_cost": round(unit_cost, 2),
                "total_cost": 0.0,
                "minimum_order_quantity": minimum_order,
                "order_multiple": order_multiple,
                "lead_time_days": lead_time,
                "status": "No order required",
            })

            continue

        desired_quantity = round_to_supplier_constraints(
            required_quantity,
            minimum_order,
            order_multiple,
        )

        affordable_batches = floor(
            remaining_budget / (unit_cost * order_multiple)
        )

        affordable_quantity = (
            affordable_batches * order_multiple
        )

        if affordable_quantity < minimum_order:

            recommended_quantity = 0
            order_cost = 0.0
            status = "Not ordered: insufficient budget for MOQ"

        else:

            recommended_quantity = min(
                desired_quantity,
                affordable_quantity,
            )

            order_cost = recommended_quantity * unit_cost

            if recommended_quantity < desired_quantity:
                status = "Reduced: limited by strategy budget"

            elif recommended_quantity > required_quantity:
                status = "Adjusted: supplier ordering constraints"

            else:
                status = "Within demand and strategy limits"

        purchase_orders.append({
            "product": product_name,
            "rank": product["rank"],
            "required_quantity": required_quantity,
            "recommended_quantity": recommended_quantity,
            "unit_cost": round(unit_cost, 2),
            "total_cost": round(order_cost, 2),
            "minimum_order_quantity": minimum_order,
            "order_multiple": order_multiple,
            "lead_time_days": lead_time,
            "status": status,
        })

        remaining_budget -= order_cost
        total_cost += order_cost
        total_units += recommended_quantity

    return {
        "plan_status": "proposed",
        "strategy": risk_assessment["strategy"],
        "dataset_type": replenishment_result.get(
            "dataset_type", "unknown"
        ),
        "forecast_horizon_days": replenishment_result[
            "forecast_horizon_days"
        ],
        "budget": round(budget, 2),
        "maximum_purchasing_budget": round(maximum_budget, 2),
        "total_purchase_cost": round(total_cost, 2),
        "remaining_budget": round(budget - total_cost, 2),
        "unused_strategy_budget": round(
            maximum_budget - total_cost, 2
        ),
        "budget_utilisation_percent": (
            round((total_cost / budget) * 100, 2)
            if budget > 0 else 0
        ),
        "strategy_budget_utilisation_percent": (
            round((total_cost / maximum_budget) * 100, 2)
            if maximum_budget > 0 else 0
        ),
        "total_units": total_units,
        "purchase_orders": purchase_orders,
    }



def print_purchase_plan(plan: dict[str, Any]) -> None:
    """Print a readable proposed purchasing plan."""

    print("\nSTOCKLINE PROPOSED PURCHASE PLAN")
    print("=" * 70)

    print(f"Plan status: {plan['plan_status']}")
    print(f"Risk strategy: {plan['strategy']}")
    print(f"Dataset: {plan['dataset_type']}")
    print(f"Forecast horizon: {plan['forecast_horizon_days']} days")

    print(f"\nAvailable business budget: ${plan['budget']:,.2f}")
    print(
    f"Strategy spending ceiling: "
    f"${plan['maximum_purchasing_budget']:,.2f}"
)
    print(f"Total purchase cost: ${plan['total_purchase_cost']:,.2f}")
    print(f"Remaining business budget: ${plan['remaining_budget']:,.2f}")
    print(
    f"Unused strategy budget: "
    f"${plan['unused_strategy_budget']:,.2f}"
)

    print(
        f"Budget utilisation: "
        f"{plan['budget_utilisation_percent']}%"
    )
    print(
        f"Strategy budget utilisation: "
        f"{plan['strategy_budget_utilisation_percent']}%"
    )

    print(f"Total units proposed: {plan['total_units']}")

    print("\nPRODUCT ORDERS")
    print("-" * 70)

    for order in plan["purchase_orders"]:

        print(f"\n#{order['rank']} — {order['product']}")

        print(
            f"Required quantity: "
            f"{order['required_quantity']} units"
        )

        print(
            f"Recommended quantity: "
            f"{order['recommended_quantity']} units"
        )

        print(f"Unit cost: ${order['unit_cost']:.2f}")
        print(f"Order cost: ${order['total_cost']:,.2f}")

        print(
            f"Supplier MOQ: "
            f"{order['minimum_order_quantity']}"
        )

        print(
            f"Order multiple: "
            f"{order['order_multiple']}"
        )

        print(
            f"Lead time: "
            f"{order['lead_time_days']} days"
        )

        print(f"Status: {order['status']}")

    print("\nNOTE: These are proposed orders, not approved orders.")



if __name__ == "__main__":
    from app.tools.data_loader import load_market_data
    from app.tools.demand_forecaster import forecast_demand
    from app.tools.inventory_manager import (
        load_inventory_data,
        calculate_replenishment_requirements,
    )
    from app.tools.product_evaluator import (
        evaluate_products,
        rank_products,
    )
    from app.tools.risk_controller import apply_risk_strategy

    # Select the purchasing strategy here.
    selected_strategy = "growth"

    market_data = load_market_data()

    # 1. Evaluate and rank products.
    evaluations = evaluate_products(market_data)
    rankings = rank_products(evaluations)

    # 2. Apply purchasing risk controls.
    budget = market_data["business"]["purchasing_budget"]

    risk_assessment = apply_risk_strategy(
        ranked_products=rankings,
        budget=budget,
        strategy_name=selected_strategy,
    )

    # 3. Generate simulated demand forecasts.
    forecasts = forecast_demand(
        market_data=market_data,
        horizon_days=30,
        historical_period_days=90,
    )

    # 4. Load inventory and apply strategy-specific safety stock.
    inventory_data = load_inventory_data()

    replenishment = calculate_replenishment_requirements(
        inventory_data=inventory_data,
        forecast_result=forecasts,
        safety_stock_multiplier=risk_assessment[
            "safety_stock_multiplier"
        ],
    )

    # 5. Generate the risk-adjusted purchase plan.
    plan = create_purchase_plan(
        ranked_products=rankings,
        replenishment_result=replenishment,
        budget=budget,
        risk_assessment=risk_assessment,
    )

    print_purchase_plan(plan)

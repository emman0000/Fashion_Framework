
from math import isfinite
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


OBJECTIVE_WEIGHTS = {
    "conservative": {
        "profit": 0.80,
        "revenue": 0.05,
        "demand": 0.10,
        "urgency": 0.05,
    },
    "balanced": {
        "profit": 0.70,
        "revenue": 0.15,
        "demand": 0.10,
        "urgency": 0.05,
    },
    "growth": {
        "profit": 0.60,
        "revenue": 0.20,
        "demand": 0.15,
        "urgency": 0.05,
    },
}


def validate_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
    ):
        raise ValueError(f"{field} must be a finite number.")

    return float(value)


def build_optimisation_inputs(
    ranked_products: list[dict[str, Any]],
    replenishment_result: dict[str, Any],
    risk_assessment: dict[str, Any],
    budget_override: float | None = None,
) -> tuple[list[dict[str, Any]], float, dict[str, float]]:
    """Prepare eligible products and their commercial inputs."""

    strategy = risk_assessment["strategy"]

    if strategy not in OBJECTIVE_WEIGHTS:
        raise ValueError(f"Unknown strategy: {strategy}")

    available_budget = validate_number(
        risk_assessment["available_budget"],
        "Available budget",
    )

    strategy_ceiling = validate_number(
        risk_assessment["maximum_purchasing_budget"],
        "Strategy budget ceiling",
    )

    if available_budget < 0 or strategy_ceiling < 0:
        raise ValueError("Budgets cannot be negative.")

    budget = min(available_budget, strategy_ceiling)

    if budget_override is not None:
        budget_override = validate_number(
            budget_override,
            "Budget override",
        )
        if budget_override < 0:
            raise ValueError("Budget override cannot be negative.")
        budget = min(budget, budget_override)

    eligible = set(risk_assessment["eligible_products"])

    replenishment = {
        item["product"]: item
        for item in replenishment_result["replenishment"]
    }

    if len(replenishment) != len(
        replenishment_result["replenishment"]
    ):
        raise ValueError("Duplicate replenishment products.")

    if len({item["product"] for item in ranked_products}) != len(
        ranked_products
    ):
        raise ValueError("Duplicate ranked products.")

    products = []

    for product in ranked_products:
        name = product["product"]

        if name not in eligible:
            continue

        if name not in replenishment:
            raise ValueError(
                f"Missing replenishment data for {name}."
            )

        cost = validate_number(
            product["supplier_unit_cost"],
            f"{name} supplier cost",
        )

        selling_price = validate_number(
            product["historical_selling_price"],
            f"{name} selling price",
        )

        if cost <= 0 or selling_price <= 0:
            raise ValueError(
                f"Invalid price or cost for {name}."
            )

        if selling_price <= cost:
            raise ValueError(
                f"{name} has no positive gross profit per unit."
            )

        moq = product["minimum_order_quantity"]
        multiple = product.get("order_multiple", 1)

        for value, field in (
            (moq, "MOQ"),
            (multiple, "order multiple"),
        ):
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value <= 0
            ):
                raise ValueError(
                    f"Invalid {field} for {name}."
                )

        required = replenishment[name]["replenishment_quantity"]

        if (
            not isinstance(required, int)
            or isinstance(required, bool)
            or required < 0
        ):
            raise ValueError(
                f"Invalid replenishment quantity for {name}."
            )

        score = validate_number(
            product["overall_score"],
            f"{name} product score",
        )

        if not 0 <= score <= 100:
            raise ValueError(f"Invalid score for {name}.")

        historical_units = validate_number(
            product["historical_units_sold"],
            f"{name} historical demand",
        )

        if historical_units < 0:
            raise ValueError(f"Invalid demand for {name}.")

        lead_time = product["supplier_lead_time_days"]

        if (
            not isinstance(lead_time, int)
            or isinstance(lead_time, bool)
            or lead_time < 0
        ):
            raise ValueError(f"Invalid lead time for {name}.")

        # Quantities are expressed in supplier order multiples.
        maximum_batches = required // multiple

        # Never exceed the replenishment requirement.
        if maximum_batches * multiple < moq:
            maximum_batches = 0

        urgency = (
            replenishment[name]["forecast_demand"]
            / max(
                replenishment[name]["inventory_position"],
                1,
            )
        )

        products.append({
            "product": name,
            "unit_cost": cost,
            "selling_price": selling_price,
            "unit_profit": selling_price - cost,
            "moq": moq,
            "multiple": multiple,
            "required_quantity": required,
            "maximum_batches": maximum_batches,
            "score": score,
            "historical_demand": historical_units,
            "lead_time": lead_time,
            "urgency": urgency,
            "rank": product["rank"],
        })

    return products, budget, OBJECTIVE_WEIGHTS[strategy]


def optimise_purchase_allocation(
    ranked_products: list[dict[str, Any]],
    replenishment_result: dict[str, Any],
    risk_assessment: dict[str, Any],
    budget_override: float | None = None,
) -> dict[str, Any]:
    """Maximise weighted commercial value under purchasing constraints."""

    products, budget, weights = build_optimisation_inputs(
        ranked_products,
        replenishment_result,
        risk_assessment,
        budget_override,
    )

    if not products:
        return {
            "status": "optimal",
            "strategy": risk_assessment["strategy"],
            "budget": budget,
            "total_cost": 0.0,
            "total_revenue": 0.0,
            "expected_gross_profit": 0.0,
            "total_units": 0,
            "orders": [],
            "objective_weights": weights,
        }

    count = len(products)

    # Two integer variables per product:
    # x[i] = number of supplier order multiples.
    # y[i] = 1 if the product is ordered, otherwise 0.
    variable_count = count * 2

    objective = np.zeros(variable_count)
    integrality = np.ones(variable_count)
    lower_bounds = np.zeros(variable_count)
    upper_bounds = np.zeros(variable_count)

    # Normalise commercial values so the objectives are comparable.
    max_profit_per_batch = max(
        p["unit_profit"] * p["multiple"]
        for p in products
    )

    max_revenue_per_batch = max(
        p["selling_price"] * p["multiple"]
        for p in products
    )

    max_urgency = max(
        p["urgency"] for p in products
    )

    for i, product in enumerate(products):

        quantity_index = i
        active_index = count + i

        maximum_batches = product["maximum_batches"]

        upper_bounds[quantity_index] = maximum_batches
        upper_bounds[active_index] = 1

        profit_value = (
            product["unit_profit"] * product["multiple"]
            / max(max_profit_per_batch, 1)
        )

        revenue_value = (
            product["selling_price"] * product["multiple"]
            / max(max_revenue_per_batch, 1)
        )

        # Reward the proportion of replenishment need covered.
        demand_coverage_value = (
            product["multiple"]
            / max(product["required_quantity"], 1)
        )

        # Reward replenishment coverage more strongly for urgent products.
        urgency_value = (
            demand_coverage_value
            * product["urgency"]
            / max(max_urgency, 1)
        )

        commercial_value = (
            weights["profit"] * profit_value
            + weights["revenue"] * revenue_value
            + weights["demand"] * demand_coverage_value
            + weights["urgency"] * urgency_value
        )

        objective[quantity_index] = -commercial_value

    # Constraints:
    # 1. Budget.
    # 2. MOQ activation.
    # 3. Quantity cannot exceed replenishment requirement.
    constraints = lil_matrix(
        (1 + count * 2, variable_count)
    )
    lower = np.full(1 + count * 2, -np.inf)
    upper = np.zeros(1 + count * 2)

    for i, product in enumerate(products):

        quantity_index = i
        active_index = count + i

        constraints[0, quantity_index] = (
            product["unit_cost"] * product["multiple"]
        )

        constraints[1 + i, quantity_index] = -1
        constraints[1 + i, active_index] = (
            product["moq"] / product["multiple"]
        )
        upper[1 + i] = 0

        constraints[1 + count + i, quantity_index] = 1
        constraints[1 + count + i, active_index] = (
            -product["maximum_batches"]
        )
        upper[1 + count + i] = 0

    upper[0] = budget

    result = milp(
        c=objective,
        integrality=integrality,
        bounds=Bounds(lower_bounds, upper_bounds),
        constraints=LinearConstraint(
            constraints.tocsr(),
            lower,
            upper,
        ),
        options={"time_limit": 30},
    )

    if result.x is None:
        raise RuntimeError(
            f"Purchasing optimisation failed: {result.message}"
        )

    orders = []
    total_cost = 0.0
    total_revenue = 0.0
    total_profit = 0.0
    total_units = 0

    for i, product in enumerate(products):

        batches = int(round(result.x[i]))
        quantity = batches * product["multiple"]

        if quantity < product["moq"]:
            quantity = 0

        cost = quantity * product["unit_cost"]
        revenue = quantity * product["selling_price"]
        profit = quantity * product["unit_profit"]

        orders.append({
            "product": product["product"],
            "rank": product["rank"],
            "required_quantity": product["required_quantity"],
            "recommended_quantity": quantity,
            "unit_cost": product["unit_cost"],
            "unit_profit": product["unit_profit"],
            "total_cost": round(cost, 2),
            "expected_revenue": round(revenue, 2),
            "expected_gross_profit": round(profit, 2),
            "lead_time_days": product["lead_time"],
            "status": (
                "Recommended" if quantity > 0
                else "Not selected by optimiser"
            ),
        })

        total_cost += cost
        total_revenue += revenue
        total_profit += profit
        total_units += quantity

    if total_cost > budget + 0.01:
        raise RuntimeError("Optimiser exceeded the budget.")

    return {
        "status": result.message,
        "strategy": risk_assessment["strategy"],
        "budget": round(budget, 2),
        "total_cost": round(total_cost, 2),
        "remaining_budget": round(budget - total_cost, 2),
        "total_revenue": round(total_revenue, 2),
        "expected_gross_profit": round(total_profit, 2),
        "total_units": total_units,
        "orders": orders,
        "objective_weights": weights,
    }


def print_optimisation_report(
    result: dict[str, Any],
) -> None:
    print("\nSTOCKLINE PURCHASING OPTIMISER")
    print("=" * 70)

    print(f"Strategy: {result['strategy']}")
    print(f"Solver status: {result['status']}")
    print(f"Budget: ${result['budget']:,.2f}")
    print(f"Purchase cost: ${result['total_cost']:,.2f}")
    print(f"Remaining budget: ${result['remaining_budget']:,.2f}")
    print(f"Expected revenue: ${result['total_revenue']:,.2f}")
    print(
        "Expected gross profit: "
        f"${result['expected_gross_profit']:,.2f}"
    )
    print(f"Total units: {result['total_units']}")

    print("\nOBJECTIVE WEIGHTS")
    for name, weight in result["objective_weights"].items():
        print(f"{name}: {weight:.0%}")

    print("\nPRODUCT ALLOCATION")
    print("-" * 70)

    for order in result["orders"]:
        print(f"\n{order['product']}")
        print(
            f"Recommended: {order['recommended_quantity']} / "
            f"{order['required_quantity']} units"
        )
        print(f"Purchase cost: ${order['total_cost']:,.2f}")
        print(
            f"Expected gross profit: "
            f"${order['expected_gross_profit']:,.2f}"
        )
        print(f"Status: {order['status']}")

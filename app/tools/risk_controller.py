
from typing import Any


PURCHASING_STRATEGIES = {
    "conservative": {
        "budget_deployment_limit": 0.50,
        "safety_stock_multiplier": 0.80,
        "minimum_scoring_coverage": 80.0,
        "minimum_product_score": 65.0,
        "risk_tolerance": "low",
        "description": (
            "Prioritises proven products, cash preservation "
            "and lower inventory exposure."
        ),
    },
    "balanced": {
        "budget_deployment_limit": 0.75,
        "safety_stock_multiplier": 1.00,
        "minimum_scoring_coverage": 60.0,
        "minimum_product_score": 50.0,
        "risk_tolerance": "medium",
        "description": (
            "Balances profitability, product performance "
            "and growth opportunities."
        ),
    },
    "growth": {
        "budget_deployment_limit": 0.90,
        "safety_stock_multiplier": 1.20,
        "minimum_scoring_coverage": 40.0,
        "minimum_product_score": 35.0,
        "risk_tolerance": "high",
        "description": (
            "Allows greater inventory exposure to pursue "
            "commercial growth."
        ),
    },
}


def get_strategy(strategy_name: str) -> dict[str, Any]:
    """Retrieve and validate a purchasing strategy."""

    strategy_name = strategy_name.lower().strip()

    if strategy_name not in PURCHASING_STRATEGIES:
        raise ValueError(
            f"Unknown purchasing strategy: {strategy_name}. "
            f"Choose from {list(PURCHASING_STRATEGIES)}."
        )

    return {
        "name": strategy_name,
        **PURCHASING_STRATEGIES[strategy_name],
    }


def validate_budget(budget: float) -> float:
    """Validate the available purchasing budget."""

    if isinstance(budget, bool) or not isinstance(budget, (int, float)):
        raise ValueError("Budget must be numeric.")

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    return float(budget)


def evaluate_product_risk(
    product: dict[str, Any],
    strategy: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate product eligibility using commercial evidence.

    Products are assessed using their existing product score
    and scoring coverage. Missing evidence is not invented.
    """

    product_name = product["product"]

    score = product.get("overall_score")
    coverage = product.get("scoring_coverage_percent")

    if score is None or coverage is None:
        return {
            "product": product_name,
            "eligible": False,
            "risk_status": "insufficient_evidence",
            "reason": "Product scoring evidence is incomplete.",
        }

    if not 0 <= score <= 100:
        raise ValueError(f"Invalid product score: {product_name}")

    if not 0 <= coverage <= 100:
        raise ValueError(f"Invalid scoring coverage: {product_name}")

    if score < strategy["minimum_product_score"]:
        return {
            "product": product_name,
            "eligible": False,
            "risk_status": "below_score_threshold",
            "reason": (
                f"Score {score} is below the strategy threshold "
                f"of {strategy['minimum_product_score']}."
            ),
        }

    if coverage < strategy["minimum_scoring_coverage"]:
        return {
            "product": product_name,
            "eligible": False,
            "risk_status": "insufficient_scoring_coverage",
            "reason": (
                f"Scoring coverage {coverage}% is below "
                f"the required {strategy['minimum_scoring_coverage']}%."
            ),
        }

    return {
        "product": product_name,
        "eligible": True,
        "risk_status": "eligible",
        "reason": "Product meets the selected strategy thresholds.",
    }


def apply_risk_strategy(
    ranked_products: list[dict[str, Any]],
    budget: float,
    strategy_name: str = "balanced",
) -> dict[str, Any]:
    """
    Apply purchasing risk controls to ranked products.

    This module does not allocate individual purchase quantities.
    It establishes purchasing eligibility and a strategy-specific
    spending ceiling for the budget optimiser.
    """

    budget = validate_budget(budget)

    strategy = get_strategy(strategy_name)

    product_assessments = []

    for product in ranked_products:

        assessment = evaluate_product_risk(
            product,
            strategy,
        )

        product_assessments.append(assessment)

    eligible_products = [
        item["product"]
        for item in product_assessments
        if item["eligible"]
    ]

    excluded_products = [
        item
        for item in product_assessments
        if not item["eligible"]
    ]

    maximum_deployment = round(
        budget * strategy["budget_deployment_limit"],
        2,
    )

    return {
        "strategy": strategy["name"],
        "risk_tolerance": strategy["risk_tolerance"],
        "strategy_description": strategy["description"],
        "available_budget": round(budget, 2),
        "budget_deployment_limit": (
            strategy["budget_deployment_limit"]
        ),
        "maximum_purchasing_budget": maximum_deployment,
        "safety_stock_multiplier": (
            strategy["safety_stock_multiplier"]
        ),
        "eligible_products": eligible_products,
        "excluded_products": excluded_products,
        "product_assessments": product_assessments,
        "eligible_product_count": len(eligible_products),
        "excluded_product_count": len(excluded_products),
    }


def print_risk_assessment(
    result: dict[str, Any],
) -> None:
    """Display the purchasing risk assessment."""

    print("\nSTOCKLINE PURCHASING RISK ASSESSMENT")
    print("=" * 65)

    print(f"Strategy: {result['strategy'].upper()}")
    print(f"Risk tolerance: {result['risk_tolerance']}")
    print(f"Description: {result['strategy_description']}")

    print(f"\nAvailable budget: ${result['available_budget']:,.2f}")

    print(
        f"Maximum purchasing budget: "
        f"${result['maximum_purchasing_budget']:,.2f}"
    )

    print(
        f"Budget deployment limit: "
        f"{result['budget_deployment_limit'] * 100:.0f}%"
    )

    print(
        f"Safety stock multiplier: "
        f"{result['safety_stock_multiplier']:.2f}"
    )

    print("\nPRODUCT ASSESSMENTS")
    print("-" * 65)

    for product in result["product_assessments"]:

        status = "ELIGIBLE" if product["eligible"] else "EXCLUDED"

        print(f"\n{product['product']}: {status}")
        print(f"Reason: {product['reason']}")

    print("\nSUMMARY")
    print(f"Eligible products: {result['eligible_product_count']}")
    print(f"Excluded products: {result['excluded_product_count']}")


if __name__ == "__main__":
    from app.tools.data_loader import load_market_data
    from app.tools.product_evaluator import (
        evaluate_products,
        rank_products,
    )

    market_data = load_market_data()

    evaluations = evaluate_products(market_data)
    rankings = rank_products(evaluations)

    budget = market_data["business"]["purchasing_budget"]

    for strategy_name in PURCHASING_STRATEGIES:

        result = apply_risk_strategy(
            ranked_products=rankings,
            budget=budget,
            strategy_name=strategy_name,
        )

        print_risk_assessment(result)

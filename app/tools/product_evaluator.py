
from typing import Any


def calculate_gross_margin(
    selling_price: float,
    unit_cost: float,
) -> float:
    """Calculate gross margin as a percentage."""
    if selling_price <= 0:
        raise ValueError("Selling price must be greater than zero.")

    if unit_cost < 0:
        raise ValueError("Unit cost cannot be negative.")

    return ((selling_price - unit_cost) / selling_price) * 100

def find_competitor_match(
    sale: dict[str, Any],
    competitors: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Find the most relevant competitor product."""

    product_name = sale["product"].lower()
    category = sale["category"].lower()

    category_matches = [
        item for item in competitors
        if item["category"].lower() == category
    ]

    keywords = {
        "cotton t-shirt": ["cotton t-shirt"],
        "linen shirt": ["linen", "shirt"],
        "wide-leg trousers": ["wide-leg", "trousers"],
        "summer dress": ["summer dress", "dress"],
        "co-ord set": ["co-ord", "set"],
    }

    product_keywords = keywords.get(product_name)

    if not product_keywords:
        return None

    for competitor in category_matches:
        competitor_name = competitor["product"].lower()

        if all(
            keyword in competitor_name
            for keyword in product_keywords
        ):
            return competitor

    return None


def evaluate_products(data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Evaluate products using historical sales, supplier costs,
    competitor pricing and observed competitor demand.

    All results are based on the supplied dataset.
    """

    historical_sales = data["historical_sales"]
    competitors = data["competitor_products"]
    suppliers = data["supplier_catalog"]
    business = data["business"]

    results = []

    for sale in historical_sales:
        product_name = sale["product"]

        # Match the supplier record by product name.
        supplier = next(
            (
                item for item in suppliers
                if item["product"].strip().lower()
                == product_name.strip().lower()
            ),
            None,
        )

        # Match competitor records by product name.
        competitor = find_competitor_match(sale, competitors)

        if supplier is None:
            continue

        selling_price = float(sale["average_selling_price"])
        historical_cost = float(sale["average_unit_cost"])
        supplier_cost = float(supplier["unit_cost"])

        historical_margin = calculate_gross_margin(
            selling_price,
            historical_cost,
        )

        projected_margin = calculate_gross_margin(
            selling_price,
            supplier_cost,
        )

        target_margin = float(
            business["target_gross_margin_percent"]
        )

        competitor_price = (
            float(competitor["competitor_price"])
            if competitor else None
        )

        price_difference = (
            selling_price - competitor_price
            if competitor_price is not None else None
        )

        results.append({
            "product": product_name,
            "category": sale["category"],
            "historical_units_sold": int(sale["units_sold"]),
            "historical_selling_price": selling_price,
            "historical_unit_cost": historical_cost,
            "supplier_unit_cost": supplier_cost,
            "historical_gross_margin_percent": round(
                historical_margin, 2
            ),
            "projected_gross_margin_percent": round(
                projected_margin, 2
            ),
            "target_gross_margin_percent": target_margin,
            "meets_target_margin": projected_margin >= target_margin,
            "minimum_order_quantity": int(
                supplier["minimum_order_quantity"]
            ),
            "supplier_lead_time_days": int(
                supplier["lead_time_days"]
            ),
            "competitor_price": competitor_price,
            "price_difference_vs_competitor": (
                round(price_difference, 2)
                if price_difference is not None else None
            ),
            "competitor_observed_demand": (
                competitor["observed_demand"]
                if competitor else None
            ),
        })

    return results


def rank_products(
    evaluations: list[dict[str, Any]],
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Calculate transparent weighted product scores."""

    if weights is None:
        weights = {
            "historical_demand": 40,
            "gross_margin": 35,
            "competitor_demand": 25,
        }

    if any(weight < 0 for weight in weights.values()):
        raise ValueError("Scoring weights cannot be negative.")

    if sum(weights.values()) <= 0:
        raise ValueError("At least one scoring weight must be positive.")

    if not evaluations:
        return []

    maximum_sales = max(
        item["historical_units_sold"]
        for item in evaluations
    )

    demand_scores = {
        "high": 100,
        "medium": 60,
        "low": 30,
    }

    ranked_products = []

    for product in evaluations:

        # Score historical sales relative to the top seller.
        sales_score = (
            product["historical_units_sold"] / maximum_sales
        ) * 100 if maximum_sales > 0 else 0

        # Score margin relative to the business target.
        target_margin = product["target_gross_margin_percent"]

        actual_margin = product["projected_gross_margin_percent"]

        if target_margin > 0:
            margin_score = 80 + ((actual_margin - target_margin) * 2)
            margin_score = max(0, min(margin_score, 100))
        else:
            margin_score = 0

        margin_score = min(margin_score, 100)

        # Convert qualitative competitor demand into a score.
        competitor_demand = product["competitor_observed_demand"]

        competitor_score = (
            demand_scores.get(competitor_demand.lower())
            if competitor_demand else None
        )

        component_scores = {
            "historical_demand": sales_score,
            "gross_margin": margin_score,
            "competitor_demand": competitor_score,
        }

        # Only use available evidence in the weighted calculation.
        available_weight = sum(
            weights[key]
            for key, score in component_scores.items()
            if score is not None
        )

        if available_weight == 0:
            overall_score = None
        else:
            overall_score = sum(
                score * weights[key]
                for key, score in component_scores.items()
                if score is not None
            ) / available_weight

        ranked_products.append({
            **product,
            "component_scores": {
                key: round(score, 2) if score is not None else None
                for key, score in component_scores.items()
            },
            "overall_score": (
                round(overall_score, 2)
                if overall_score is not None else None
            ),
            "scoring_coverage_percent": round(
                available_weight / sum(weights.values()) * 100,
                2,
            ),
        })

    ranked_products.sort(
        key=lambda item: (
            item["overall_score"] is not None,
            item["overall_score"] or 0,
        ),
        reverse=True,
    )

    for rank, product in enumerate(ranked_products, start=1):
        product["rank"] = rank

    return ranked_products


if __name__ == "__main__":
    from app.tools.data_loader import load_market_data

    market_data = load_market_data()

    evaluations = evaluate_products(market_data)
    rankings = rank_products(evaluations)

    print("\nPRODUCT RANKINGS")
    print("=" * 65)

    for product in rankings:
        print(f"\nRank: #{product['rank']} — {product['product']}")
        print(f"Overall score: {product['overall_score']}/100")
        print(
            f"Scoring coverage: "
            f"{product['scoring_coverage_percent']}%"
        )

        print("\nComponent scores:")

        for factor, score in product["component_scores"].items():
            print(f"  {factor}: {score}")

        print(
            f"\nProjected gross margin: "
            f"{product['projected_gross_margin_percent']}%"
        )
        print(
            f"Historical units sold: "
            f"{product['historical_units_sold']}"
        )
        print(
            f"Competitor demand: "
            f"{product['competitor_observed_demand']}"
        )

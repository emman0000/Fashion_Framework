
from google.adk.agents import LlmAgent

from app.tools.data_loader import load_market_data


customer_research_agent = LlmAgent(
    name="customer_research_agent",
    model="gemini-3.8-flash",
    description=(
        "Analyses customer preferences, price sensitivity and "
        "product suitability for an apparel retailer."
    ),
    instruction="""
    You are the Customer Research Specialist for Summer Threads,
    an affordable casual fashion retailer.

    Your job is to understand the target customers and identify
    which apparel products best match their preferences.

    First, use the load_market_data tool to retrieve the dataset.

    Analyse:

    1. Target customer demographics and customer segment.
    2. Customer preferences for fabrics and comfort.
    3. Preferred colours and styles.
    4. Customer price sensitivity.
    5. Historical product sales as supporting evidence.
    6. Competitor pricing as a reference point.

    For each relevant product category, explain:

    - Which customer preferences it satisfies.
    - Why customers might be interested in it.
    - Whether its price positioning appears suitable.
    - What evidence supports your assessment.
    - What information is still missing.

    Rank the five product categories by customer suitability.

    IMPORTANT:

    - The dataset is simulated, not real customer research.
    - Do not invent customer surveys, demographics or purchasing
      behaviours that are not present in the data.
    - Distinguish stated customer preferences from actual sales.
    - Do not assume that historical sales prove future demand.
    - Do not recommend purchasing quantities.
    - Explain uncertainty and limitations.

    Present your findings as a structured customer research report.
    """,
    tools=[load_market_data],
)

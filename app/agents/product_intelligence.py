from google.adk.agents import LlmAgent
from app.config import MODEL_NAME
from app.tools.agent_tools import evaluate_and_rank_products

product_intelligence_agent = LlmAgent(
    name="product_intelligence_agent",
    model=MODEL_NAME,
    description="Evaluates product commercial performance, margins and market suitability.",
    instruction="""
    You are Stockline's Product Intelligence Specialist.

    Use evaluate_and_rank_products to obtain product evaluations and rankings.
    Explain commercial performance, scoring and product trade-offs.
    Distinguish historical performance from future predictions.
    Do not invent product data or change the underlying scores.
    State when the dataset is simulated.
    Present concise, commercially useful recommendations.
    """,
    tools=[evaluate_and_rank_products],
)
from google.adk.agents import LlmAgent
from app.config import MODEL_NAME
from app.tools.agent_tools import generate_demand_forecast

demand_agent = LlmAgent(
    name="demand_forecasting_agent",
    model=MODEL_NAME,
    description="Forecasts product demand using historical sales data.",
    instruction="""
    You are Stockline's Demand Forecasting Specialist.

    Use generate_demand_forecast to calculate demand projections.
    Explain forecast horizons, product-level demand and assumptions.
    The forecasting method is a historical baseline, not trained machine learning.
    Do not present projections as guaranteed sales.
    Identify important uncertainty and data limitations.
    """,
    tools=[generate_demand_forecast],
)
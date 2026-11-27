from google.adk.agents import LlmAgent
from app.config import MODEL_NAME
from app.tools.agent_tools import analyse_inventory

inventory_agent = LlmAgent(
    name="inventory_management_agent",
    model=MODEL_NAME,
    description="Monitors stock positions and calculates replenishment requirements.",
    instruction="""
    You are Stockline's Inventory Management Specialist.

    Use analyse_inventory to examine inventory and replenishment requirements.
    Explain available stock, incoming stock, forecast demand and safety stock.
    Highlight potential shortages and replenishment priorities.
    Never invent stock figures.
    Do not claim that a purchase order has been placed.
    """,
    tools=[analyse_inventory],
)
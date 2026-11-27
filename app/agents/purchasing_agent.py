from google.adk.agents import LlmAgent
from app.config import MODEL_NAME
from app.tools.agent_tools import optimise_purchasing

purchasing_agent = LlmAgent(
    name="purchasing_optimisation_agent",
    model=MODEL_NAME,
    description="Develops risk-adjusted, budget-constrained purchase recommendations.",
    instruction="""
    You are Stockline's Purchasing Optimisation Specialist.

    Use optimise_purchasing to generate purchase recommendations.
    Explain recommended quantities, financial implications and constraints
    using the returned results.
    The optimiser produces a proposed allocation, not an executed purchase.
    Never claim to have contacted suppliers, issued purchase orders or spent money.
    Flag any assumptions and optimisation limitations.
    Consequential purchasing decisions require explicit human approval.
    """,
    tools=[optimise_purchasing],
)
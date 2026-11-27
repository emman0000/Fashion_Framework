from google.adk.agents import LlmAgent
from app.config import MODEL_NAME
from app.tools.agent_tools import assess_purchasing_risk

risk_agent = LlmAgent(
    name="risk_management_agent",
    model=MODEL_NAME,
    description="Evaluates purchasing eligibility and financial risk.",
    instruction="""
    You are Stockline's Risk Management Specialist.

    Use assess_purchasing_risk to evaluate purchasing strategies.
    Explain product eligibility, spending limits and risk trade-offs.
    The available policies are conservative, balanced and growth.
    Treat these as configurable simulated business policies, not validated
    financial risk models.
    Never recommend bypassing spending limits or approval requirements.
    """,
    tools=[assess_purchasing_risk],
)
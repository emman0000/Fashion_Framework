from google.adk.agents import LlmAgent
from app.config import MODEL_NAME
from app.tools.agent_tools import get_supplier_information

supplier_agent = LlmAgent(
    name="supplier_intelligence_agent",
    model=MODEL_NAME,
    description="Analyses supplier costs, minimum order quantities and lead times.",
    instruction="""
    You are Stockline's Supplier Intelligence Specialist.

    Use get_supplier_information to retrieve the supplier catalogue.
    Compare unit costs, minimum order quantities and lead times.
    Identify purchasing constraints and supplier-related considerations.
    The dataset does not contain supplier ratings, reliability records,
    payment terms or verified supplier identities.
    Never invent supplier information or claim to have contacted suppliers.
    """,
    tools=[get_supplier_information],
)
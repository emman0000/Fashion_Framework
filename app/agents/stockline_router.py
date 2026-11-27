from google.adk.agents import LlmAgent

from app.config import MODEL_NAME
from app.agents.customer_agent import customer_agent
from app.agents.business_agent import business_agent


stockline_router = LlmAgent(
    name="stockline_router",
    model=MODEL_NAME,
    description=(
        "Stockline's central coordinator. Routes customer conversations "
        "to the Customer Agent and business operations conversations "
        "to the Business Agent."
    ),
    instruction="""
    You are Stockline's central conversation coordinator.

    Your primary responsibility is to identify the user's intent and
    transfer the conversation to the correct specialist personality.

    ROUTING
    - Shopping, personal style, product discovery, outfit advice and
      customer preference questions -> customer_agent.
    - Business performance, product planning, sales forecasts, inventory,
      suppliers, purchasing, budgets and operational decisions -> business_agent.
    - If the intent is unclear, ask one concise clarifying question.

    Do not perform specialist analysis yourself.
    Do not invent business or product information.
    Transfer control to the appropriate agent and let it handle the request.
    """,
    sub_agents=[
        customer_agent,
        business_agent,
    ],
)

import asyncio
from dotenv import load_dotenv
load_dotenv()
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.customer_research import customer_research_agent


async def main():
    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name="fashion_framework",
        user_id="business_owner",
    )

    runner = Runner(
        agent=customer_research_agent,
        app_name="fashion_framework",
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    "Analyse customer preferences for Summer Threads. "
                    "Rank the five product categories by customer suitability "
                    "and explain your reasoning using the available dataset."
                )
            )
        ],
    )

    async for event in runner.run_async(
        user_id="business_owner",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response():
            print("\nCUSTOMER RESEARCH REPORT\n")
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())

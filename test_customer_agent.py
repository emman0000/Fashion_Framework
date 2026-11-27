
import asyncio
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.customer_research import customer_research_agent


load_dotenv()


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

    print("Running Customer Research Agent...\n")

    response_received = False

    try:
        async for event in runner.run_async(
            user_id="business_owner",
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response():

                if event.content and event.content.parts:
                    response_text = "\n".join(
                        part.text
                        for part in event.content.parts
                        if getattr(part, "text", None)
                    )

                    if response_text:
                        print("\nCUSTOMER RESEARCH REPORT\n")
                        print(response_text)
                        response_received = True

                if not response_received:
                    print(
                        "\nThe agent did not return a response. "
                        "Check the ADK/API error messages above."
                    )

    except Exception as error:
        print("\nCUSTOMER AGENT EXECUTION FAILED")
        print(f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    asyncio.run(main())

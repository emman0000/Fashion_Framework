from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from app.config import APP_NAME, DATABASE_URL
from app.agents.customer_agent import customer_agent
from app.agents.business_agent import business_agent


# One persistent session database shared by both experiences.
session_service = DatabaseSessionService(db_url=DATABASE_URL)

# Separate runners keep customer and business session namespaces distinct.
runners = {
    "customer": Runner(
        agent=customer_agent,
        app_name=f"{APP_NAME}_customer",
        session_service=session_service,
    ),
    "business": Runner(
        agent=business_agent,
        app_name=f"{APP_NAME}_business",
        session_service=session_service,
    ),
}


async def send_message(
    experience: str,
    user_id: str,
    message: str,
    session_id: str | None = None,
) -> dict:
    """Send a message to the selected Stockline experience."""

    if experience not in runners:
        raise ValueError("Experience must be 'customer' or 'business'.")

    if not user_id.strip():
        raise ValueError("A user ID is required.")

    if not message.strip():
        raise ValueError("A message is required.")

    runner = runners[experience]
    app_name = runner.app_name

    # Create a new conversation or retrieve the supplied session.
    if session_id:
        session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            raise ValueError("Conversation session not found.")
    else:
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
        )

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )

    response_parts = []

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_parts.append(part.text)

    response_text = "\n".join(response_parts).strip()

    if not response_text:
        response_text = (
            "I couldn't generate a response this time. "
            "Please try again."
        )

    return {
        "experience": experience,
        "session_id": session.id,
        "response": response_text,
    }


async def close_agent_service() -> None:
    """Close the persistent database connection."""
    await session_service.close()
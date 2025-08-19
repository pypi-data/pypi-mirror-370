import asyncio
import datetime
import json
import uuid

# Ingenious imports
import ingenious.config.config as ingen_config
import ingenious.dependencies as ingen_deps
from ingenious.models.chat import ChatRequest
from ingenious.services.chat_service import ChatService


async def main():
    thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Create a proper JSON payload for bike_insights conversation flow
    test_payload = {
        "revision_id": "test_revision_001",
        "identifier": str(uuid.uuid4()),
        "stores": [
            {
                "name": "Test Bike Store",
                "location": "NSW",
                "bike_sales": [
                    {
                        "product_code": "EB-TEST-2023-TV",
                        "quantity_sold": 2,
                        "sale_date": "2023-04-01",
                        "year": 2023,
                        "month": "April",
                        "customer_review": {
                            "rating": 4.5,
                            "comment": "Great bike for commuting!",
                        },
                    }
                ],
                "bike_stock": [
                    {
                        "bike": {
                            "brand": "Test Brand",
                            "model": "EB-TEST-2023-TV",
                            "year": 2023,
                            "price": 2500.0,
                            "battery_capacity": 0.5,
                            "motor_power": 250.0,
                        },
                        "quantity": 10,
                    }
                ],
            }
        ],
    }

    user_prompt = json.dumps(test_payload)

    chat_history_repository = ingen_deps.get_chat_history_repository()

    chat_request = ChatRequest(
        thread_id=thread_id, user_prompt=user_prompt, conversation_flow="bike_insights"
    )

    chat_service = ChatService(
        chat_service_type="multi_agent",
        chat_history_repository=chat_history_repository,
        conversation_flow="bike_insights",
        config=ingen_config.get_config(),
    )

    response = await chat_service.get_chat_response(chat_request)

    print(
        f"Response received - Message ID: {response.message_id}, Token Count: {response.token_count}"
    )
    print(f"Agent Response: {str(response.agent_response)[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import datetime
import json

import jsonpickle
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn

import ingenious.config.config as ingen_config
import ingenious.dependencies as ingen_deps
from ingenious.files.files_repository import FileStorage

# import ingenious_extensions.models.ca_raw_fixture_data as gm
from ingenious.models.chat import ChatRequest
from ingenious.utils.log_levels import LogLevel
from ingenious.utils.stage_executor import ProgressConsoleWrapper

# Ensure environment variables are set
config = ingen_config.get_config()
USERNAME = ingen_deps.config.web_configuration.authentication.username
PASSWORD = ingen_deps.config.web_configuration.authentication.password

# Log level for the progress console
log_level = LogLevel.INFO

# Create the raw Progress object
raw_progress = Progress(
    SpinnerColumn(spinner_name="dots", style="progress.spinner", finished_text="📦"),
    TextColumn("[progress.description]{task.description}"),
    transient=False,
)

# Wrap the Progress object with ProgressConsoleWrapper
progress = ProgressConsoleWrapper(progress=raw_progress, log_level=log_level)

# File storage and directory setup
fs = FileStorage(config=config)
raw_directory = "example_payload/raw"
history_directory = "----"


async def process_files():
    message_object = None

    return message_object


async def main():
    message_object = await process_files()

    if message_object:
        thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        user_prompt = jsonpickle.dumps(message_object, unpicklable=False)
        chat_request = ChatRequest(
            thread_id=thread_id,
            user_prompt=user_prompt,
            conversation_flow="-----",
        )

        try:
            response = requests.post(
                url="http://localhost:80/api/v1/chat_test",
                json=chat_request.model_dump(),
                auth=(USERNAME, PASSWORD),
            )

            response_content = json.loads(
                json.loads(response.text)["response"]["content"]
            )
            print("Response received:", response_content)
            return response_content
        except Exception as e:
            print(f"Error sending chat request: {str(e)}")


response_content = asyncio.run(main())

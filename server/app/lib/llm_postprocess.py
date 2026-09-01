import os

from google import genai
from google.genai.types import HttpOptions, Part, GenerateContentConfig
from google.oauth2 import service_account
import json
from app.lib.auth import get_credentials
from app.lib.prompt import create_prompt
from app.lib.schema import get_response_schema
from dotenv import load_dotenv

load_dotenv()

credentials = get_credentials()

client = genai.Client(
    vertexai=True,
    project="land-record-507214",
    location="global",
    http_options=HttpOptions(api_version="v1"),
    credentials=credentials
)

import mimetypes

def process_by_llm(text, img_path: str):
    with open(img_path, "rb") as f:
        image_data = f.read()

    mime_type, _ = mimetypes.guess_type(img_path)
    if not mime_type:
        mime_type = "image/png"

    chat = client.chats.create(
        model="gemini-1.5-flash",
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=get_response_schema()
        )
    )

    response = chat.send_message([
        Part.from_bytes(data=image_data, mime_type=mime_type),
        create_prompt(json.dumps(text, indent=2) if isinstance(text, (dict, list)) else str(text))
    ])

    return json.loads(response.text)

import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()
def notification(channel_id:str,message:list)->None:
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT')

    # Initialize the Slack client
    client = WebClient(token=SLACK_BOT_TOKEN)
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text="",
            blocks=message
        )
        print(f"Message sent successfully: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

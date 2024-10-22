import os
from azure.ai.contentsafety import BlocklistClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import TextBlocklist
from azure.core.exceptions import HttpResponseError

# Prompt user for API key and endpoint
key = input("Please enter your Content Safety API key: ")
endpoint = input("Please enter your Content Safety endpoint: ")

# Create a Blocklist client
client = BlocklistClient(endpoint, AzureKeyCredential(key))

blocklist_name = "UserBlockList"
blocklist_description = "test blocklist"

try:
    blocklist = client.create_or_update_text_blocklist(
        blocklist_name=blocklist_name,
        options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
    )
    if blocklist:
        print("\nBlocklist created or updated: ")
        print(f"Name: {blocklist.blocklist_name}, Description: {blocklist.description}")
except HttpResponseError as e:
    print("\nCreate or update text blocklist failed: ")
    if e.error:
        print(f"Error code: {e.error.code}")
        print(f"Error message: {e.error.message}")
        raise
    print(e)
    raise

from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions

# Prompt user for API key and endpoint
key = input("Please enter your Content Safety API key: ")
endpoint = input("Please enter your Content Safety endpoint: ")

# Create a Content Safety client
client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

# Prompt the user for content to analyze, with a default message
default_content = "I h*te you and I want to k*ll you."
content_to_analyze = input(f"Please enter the content you want to analyze (default: '{default_content}'): ") or default_content

# Create options for the text to analyze
options = AnalyzeTextOptions(text=content_to_analyze)

# Analyze the content
response = client.analyze_text(options=options)

# Print the result
print(response)

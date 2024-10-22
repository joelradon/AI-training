from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions

# Prompt user for API key and endpoint
key = input("Please enter your Content Safety API key: ")
endpoint = input("Please enter your Content Safety endpoint: ")

# Create a Content Safety client
client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

# Blocklist name
blocklist_name = "UserBlockList"

# Example texts to analyze
examples = [
    "I hate you and want to hurt you.",                # High severity: Hate, Violence
    "You should consider hurting yourself.",           # High severity: SelfHarm
    "This place is disgusting and needs to burn.",     # Medium severity: Hate, Violence
    "Go away, no one likes you!",                      # Low severity: Hate
    "You are worthless, everyone hates you.",          # High severity: Hate, SelfHarm
    "I can't stand you, you're awful.",                # Medium severity: Hate
    "This violence needs to stop now!",                # Low severity: Violence
    "Let's fight until one of us drops.",              # Medium severity: Violence
    "Hope you have a wonderful day!",                  # Safe content
    "The weather today is amazing, let's go out!"      # Safe content
]

# Analyze each example and check against the blocklist
for index, content_to_analyze in enumerate(examples, 1):
    options = AnalyzeTextOptions(text=content_to_analyze, blocklist_names=[blocklist_name], halt_on_blocklist_hit=False)
    response = client.analyze_text(options=options)

    print(f"\nExample {index}: '{content_to_analyze}'")
    print("Result:", response)

    # Check if the content matches any blocklisted terms
    if response.blocklists_match:
        print(f"Blocklist match found in: '{content_to_analyze}'")

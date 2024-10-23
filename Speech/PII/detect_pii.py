import os
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient

# Step 1: Retrieve secrets (API key, endpoint) from Azure Key Vault
def get_secret(secret_name, key_vault_name):
    key_vault_url = f"https://{key_vault_name}.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)

    try:
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None

# Step 2: Download blob content from Azure Storage
def download_blob(storage_account_name, container_name, blob_name, storage_account_key):
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net/",
        credential=storage_account_key,
    )
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob().readall()
    
    # Try decoding with different encodings
    for encoding in ['utf-8', 'utf-16', 'latin1']:
        try:
            return blob_data.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Unable to decode blob {blob_name} with any common encoding.")

# Step 3: Perform PII detection using Azure Text Analytics API (version 3.1)
def detect_pii(api_key, endpoint, text):
    url = f"{endpoint}/text/analytics/v3.1/entities/recognition/pii"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/json"
    }

    body = {
        "documents": [
            {"id": "1", "language": "en", "text": text}
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Step 4: Perform text summarization using Azure Text Analytics API (version 3.1)
def summarize_text(api_key, endpoint, text):
    url = f"{endpoint}/text/analytics/v3.1/summarize"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/json"
    }

    body = {
        "documents": [
            {"id": "1", "language": "en", "text": text}
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print("Summarization not available for this file (Resource not found).")
        return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Step 5: Main function to run the PII detection and summarization workflow
def main():
    # Prompt for input with defaults
    key_vault_name = input("Enter the Key Vault name (default: 'LabVault123'): ").strip() or "LabVault123"
    storage_account_name = input("Enter the storage account name (default: 'radonaistorage'): ").strip() or "radonaistorage"
    container_name = input("Enter the container name (default: 'testfiles'): ").strip() or "testfiles"

    # Retrieve API key and endpoint from Key Vault
    api_key = get_secret("AzureAITextAnalyticsApiKey", key_vault_name)
    endpoint = get_secret("AzureAITextAnalyticsEndpoint", key_vault_name)
    storage_account_key = get_secret("AzureStorageAccountKey", key_vault_name)

    if not api_key or not endpoint or not storage_account_key:
        print("Failed to retrieve secrets from Key Vault.")
        return

    # List of blob names to analyze
    blobs_to_analyze = ["document1.txt", "document2.txt", "email1.txt", "email2.txt", "email3.txt", "email4.txt"]

    for blob_name in blobs_to_analyze:
        # Step 1: Download the content of the blob
        try:
            file_content = download_blob(storage_account_name, container_name, blob_name, storage_account_key)
            print(f"Analyzing PII and summarizing for file: {blob_name}")
        except Exception as e:
            print(f"Error downloading blob {blob_name}: {e}")
            continue

        # Step 2: Perform PII detection
        pii_result = detect_pii(api_key, endpoint, file_content)

        if pii_result and "documents" in pii_result and len(pii_result["documents"]) > 0 and "entities" in pii_result["documents"][0]:
            # Display detected PII entities
            print(f"PII detected in {blob_name}:")
            for entity in pii_result["documents"][0]["entities"]:
                sub_category = entity.get('subCategory', 'N/A')
                print(f"  - {entity['text']} ({entity['category']}, {sub_category}, Confidence: {entity['confidenceScore']})")
        else:
            print(f"No PII detected in {blob_name} or response was empty.")

        # Step 3: Perform text summarization
        summary_result = summarize_text(api_key, endpoint, file_content)

        if summary_result and "documents" in summary_result and len(summary_result["documents"]) > 0:
            print(f"Summary for {blob_name}:")
            for sentence in summary_result["documents"][0]["sentences"]:
                print(f"  - {sentence['text']}")
        else:
            print(f"No summary available for {blob_name}.")

if __name__ == "__main__":
    main()

import os
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from PIL import Image
import io

# Step 1: Retrieve API Key and Endpoint from Azure Key Vault
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

# Step 2: Resize image if it exceeds size limits
def resize_image(image_path, max_size=(4200, 4200)):
    try:
        with Image.open(image_path) as img:
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                print(f"Resizing image from {img.size} to fit within {max_size}.")
                img.thumbnail(max_size)
                # Save to BytesIO to keep the image in memory
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                return img_byte_arr.getvalue()
            else:
                # If the image size is within limits, return the original bytes
                with open(image_path, "rb") as f:
                    return f.read()
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

# Step 3: Function to analyze an image (URL or local file)
def analyze_image(api_key, endpoint, image_data=None, image_url=None):
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/octet-stream" if image_data else "application/json"
    }
    
    params = {
        "visualFeatures": "Categories,Description,Tags,Objects",
    }

    if image_data:
        response = requests.post(f"{endpoint}/vision/v3.2/analyze", headers=headers, params=params, data=image_data)
    else:
        response = requests.post(f"{endpoint}/vision/v3.2/analyze", headers=headers, params=params, json={"url": image_url})
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Step 4: Determine if input is a URL or file path
def is_url(input_string):
    return input_string.startswith("http://") or input_string.startswith("https://")

# Step 5: Main function to prompt the user for input
def main():
    # Prompt the user to input Key Vault name and secret names, with defaults
    key_vault_name = input("Enter the Key Vault name (default: 'LabVault123'): ").strip() or "LabVault123"
    api_key_secret_name = input("Enter the secret name for the API key (default: 'MySecretApiKey'): ").strip() or "MySecretApiKey"
    endpoint_secret_name = input("Enter the secret name for the endpoint (default: 'ComputerVisionEndpoint'): ").strip() or "ComputerVisionEndpoint"
    
    # Retrieve API key and endpoint from Azure Key Vault
    api_key = get_secret(api_key_secret_name, key_vault_name)
    endpoint = get_secret(endpoint_secret_name, key_vault_name)
    
    if not api_key or not endpoint:
        print("Failed to retrieve API key or endpoint from Key Vault.")
        return
    
    # Ask the user to input the image location (URL or file path)
    image_input = input("Please enter the image URL or local file path: ").strip()
    
    if is_url(image_input):
        # If input is a URL, process it as an image URL
        analysis_result = analyze_image(api_key, endpoint, image_url=image_input)
    else:
        # If input is a local file, process it as a file
        file_path = image_input.replace("\\", "/")  # Ensure the file path is valid on all platforms
        image_data = resize_image(file_path)  # Resize if necessary
        if image_data is None:
            print("Error processing image.")
            return
        
        analysis_result = analyze_image(api_key, endpoint, image_data=image_data)
    
    # Step 6: Display the analysis results
    if analysis_result:
        print("\n--- Image Analysis Results ---")
        print(f"Categories: {[category['name'] for category in analysis_result.get('categories', [])]}")
        print(f"Description: {analysis_result.get('description', {}).get('captions', [{}])[0].get('text', 'No description available.')}")
        print(f"Tags: {[tag['name'] for tag in analysis_result.get('tags', [])]}")
        print("Objects:")
        for obj in analysis_result.get("objects", []):
            print(f"  - {obj['object']} (confidence: {obj['confidence']:.2f})")

if __name__ == "__main__":
    main()

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

# Step 3: Analyze image using Computer Vision API
def analyze_image(api_key, endpoint, image_data=None, image_url=None):
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/octet-stream" if image_data else "application/json"
    }

    # Requesting all relevant visual features for a comprehensive analysis
    params = {
        "visualFeatures": "Categories,Description,Tags,Faces,Brands,Objects,Color,ImageType,Adult",
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

# Step 4: Detect faces using Face API
def detect_faces(face_api_key, face_api_endpoint, image_data=None, image_url=None):
    headers = {
        "Ocp-Apim-Subscription-Key": face_api_key,
        "Content-Type": "application/octet-stream" if image_data else "application/json"
    }

    # Parameters for face detection
    params = {
        "returnFaceId": "false",  # Only detect faces, no identification
        "returnFaceLandmarks": "false",  # Skipping landmarks for simplicity
    }

    if image_data:
        response = requests.post(f"{face_api_endpoint}/face/v1.0/detect", headers=headers, params=params, data=image_data)
    else:
        response = requests.post(f"{face_api_endpoint}/face/v1.0/detect", headers=headers, params=params, json={"url": image_url})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Face API Error: {response.status_code} - {response.text}")
        return None

# Step 5: Main function to prompt the user for input and run analysis
def main():
    # Prompt the user to input Key Vault name and secret names, with defaults
    key_vault_name = input("Enter the Key Vault name (default: 'LabVault123'): ").strip() or "LabVault123"
    api_key_secret_name = input("Enter the secret name for the Computer Vision API key (default: 'MySecretApiKey'): ").strip() or "MySecretApiKey"
    endpoint_secret_name = input("Enter the secret name for the Computer Vision endpoint (default: 'ComputerVisionEndpoint'): ").strip() or "ComputerVisionEndpoint"
    
    # Prompt for Face API Key and Endpoint with defaults
    face_api_key_secret_name = input("Enter the secret name for the Face API key (default: 'FaceAPIKey'): ").strip() or "FaceAPIKey"
    face_api_endpoint_secret_name = input("Enter the secret name for the Face API endpoint (default: 'FaceAPIEndpoint'): ").strip() or "FaceAPIEndpoint"
    
    # Retrieve API keys and endpoints from Azure Key Vault
    api_key = get_secret(api_key_secret_name, key_vault_name)
    endpoint = get_secret(endpoint_secret_name, key_vault_name)
    face_api_key = get_secret(face_api_key_secret_name, key_vault_name)
    face_api_endpoint = get_secret(face_api_endpoint_secret_name, key_vault_name)
    
    if not api_key or not endpoint or not face_api_key or not face_api_endpoint:
        print("Failed to retrieve API key or endpoint from Key Vault.")
        return
    
    # Ask the user to input the image location (URL or file path)
    image_input = input("Please enter the image URL or local file path: ").strip()
    
    if image_input.startswith("http://") or image_input.startswith("https://"):
        # Process as an image URL
        analysis_result = analyze_image(api_key, endpoint, image_url=image_input)
        face_analysis = detect_faces(face_api_key, face_api_endpoint, image_url=image_input)
    else:
        # Process as a local file
        file_path = image_input.replace("\\", "/")  # Ensure valid path for different platforms
        image_data = resize_image(file_path)  # Resize if necessary
        if image_data is None:
            print("Error processing image.")
            return
        analysis_result = analyze_image(api_key, endpoint, image_data=image_data)
        face_analysis = detect_faces(face_api_key, face_api_endpoint, image_data=image_data)
    
    # Step 6: Display the results from Computer Vision API
    if analysis_result:
        print("\n--- Computer Vision Analysis Results ---")
        print(f"Categories: {[category['name'] for category in analysis_result.get('categories', [])]}")
        print(f"Description: {analysis_result.get('description', {}).get('captions', [{}])[0].get('text', 'No description available.')}")
        print(f"Tags: {[tag['name'] for tag in analysis_result.get('tags', [])]}")
        
        # Display face detection results from Computer Vision API
        if 'faces' in analysis_result:
            print("Faces detected (from Computer Vision API):")
            for face in analysis_result['faces']:
                face_rectangle = face['faceRectangle']
                print(f"Face at Left: {face_rectangle['left']}, Top: {face_rectangle['top']}, Width: {face_rectangle['width']}, Height: {face_rectangle['height']}")
        
        # Display brand detection results
        if 'brands' in analysis_result:
            print("Brands detected:")
            for brand in analysis_result['brands']:
                print(f"Brand: {brand['name']}, Confidence: {brand['confidence']:.2f}")
        
        # Display object detection results
        if 'objects' in analysis_result:
            print("Objects detected:")
            for obj in analysis_result['objects']:
                print(f"Object: {obj['object']} at {obj['rectangle']}")
        
        # Display color analysis results
        if 'color' in analysis_result:
            color = analysis_result['color']
            print(f"Dominant Colors: {color['dominantColors']}")
            print(f"Is Black and White: {color['isBWImg']}")
    
    # Step 7: Display face detection results from Face API
    if face_analysis:
        print("\n--- Face Detection Results (Face API) ---")
        for face in face_analysis:
            face_rectangle = face['faceRectangle']
            print(f"Face detected at coordinates: Left: {face_rectangle['left']}, Top: {face_rectangle['top']}, Width: {face_rectangle['width']}, Height: {face_rectangle['height']}")

if __name__ == "__main__":
    main()

import os
import base64
import webbrowser
import uuid
import json
from datetime import datetime

def save_and_open_image(image_data: str, output_dir: str = None, metadata: dict = None) -> str:
    """
    Save image from base64 data and open it in browser, also save metadata if provided
    
    Args:
        image_data: Base64 string of the image
        output_dir: Directory to save the image (defaults to IMAGE_STORAGE_DIRECTORY env var)
        metadata: Optional dictionary containing RunPod response metadata
        
    Returns:
        The path to the saved image file
    """
    if output_dir is None:
        output_dir = os.path.expanduser(
            os.getenv("IMAGE_STORAGE_DIRECTORY", "~/richdaleai-images")
        )
    
    os.makedirs(output_dir, exist_ok=True)
    
    if image_data.startswith("data:image"):
        header, b64data = image_data.split(",", 1)
        ext = header.split("/")[1].split(";")[0]
    else:
        b64data = image_data
        ext = "png"

    img_bytes = base64.b64decode(b64data)
    
    # Generate unique ID with timestamp and UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
    base_filename = f"generated_{timestamp}_{unique_id}"
    
    # Save image
    image_filename = f"{base_filename}.{ext}"
    image_filepath = os.path.join(output_dir, image_filename)
    
    with open(image_filepath, "wb") as f:
        f.write(img_bytes)
    
    # Save metadata if provided
    if metadata:
        metadata_filename = f"{base_filename}_metadata.json"
        metadata_filepath = os.path.join(output_dir, metadata_filename)
        
        # Add generation timestamp to metadata
        metadata_with_timestamp = {
            "generation_timestamp": datetime.now().isoformat(),
            "image_filename": image_filename,
            "runpod_response": metadata
        }
        
        with open(metadata_filepath, "w", encoding="utf-8") as f:
            json.dump(metadata_with_timestamp, f, indent=2, ensure_ascii=False)

    # Open image in browser
    webbrowser.open(f"file://{os.path.abspath(image_filepath)}")
    
    return image_filepath

import os
import requests
from fastmcp import FastMCP
from .utils import save_and_open_image

mcp = FastMCP("richdaleai_mcp")

RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
IMAGE_STORAGE_DIRECTORY = os.getenv("IMAGE_STORAGE_DIRECTORY", "~/richdaleai-images")

@mcp.tool()
def generate_image(prompt: str):
    """Generate an image from a text prompt using RunPod API"""
    headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}
    payload = {"input": {"prompt": prompt, "width": 1024, "height": 1024}}

    resp = requests.post(RUNPOD_ENDPOINT, headers=headers, json=payload)
    data = resp.json()

    if data.get("status") == "COMPLETED" and "output" in data and "images" in data["output"] and data["output"]["images"]:
        try:
            first_image = data["output"]["images"][0]
            # Pass the full RunPod response as metadata
            saved_path = save_and_open_image(first_image, IMAGE_STORAGE_DIRECTORY, data)
            return f"Image save successfully and saved in {saved_path}"
        except Exception:
            return "Generation ERROR L"
    
    return "Generation ERROR G"

def run():
    mcp.run()

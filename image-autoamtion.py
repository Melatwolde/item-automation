import os
import google.genai as genai
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv
from rembg import remove, new_session
import base64
from io import BytesIO
import json
import concurrent.futures

load_dotenv()

API_KEY = os.getenv("GEMAI")   

INPUT_FOLDER  = "/home/zoe/item-automation/raw_images"              
OUTPUT_FOLDER = "/home/zoe/item-automation/refined_images"        

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MODEL = "gemini-flash-latest"                       

client = genai.Client(api_key=API_KEY)
session = new_session("u2net")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def sanitize_filename(text: str) -> str:
    text = text.strip().replace(" ", "_").replace("/", "-").replace("\\", "-")
    bad_chars = '<>:"/\\|?*'
    for c in bad_chars:
        text = text.replace(c, "")
    return text[:80] + ".png" 

def process_image(image_path: Path):
    try:
        img = Image.open(image_path)
        # Resize if huge to speed up upload/processing
        if max(img.size) > 1600:
            img.thumbnail((1600, 1600))

        prompt = """Analyze this product photo. 
        Identify the product precisely and return a professional product name.
        Return ONLY valid JSON: {"product_name": "..."}"""

        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85) # JPEG is faster/smaller for upload
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        contents = [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
        ]

        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )

        try:
            text = response.candidates[0].content.parts[0].text.strip()
            if text.startswith("```json"):
                text = text[7:].strip()
            if text.endswith("```"):
                text = text[:-3].strip()
            result = json.loads(text)
            product_name = result.get("product_name", "Unknown_Product")

            # Background removal using pre-loaded session
            output_img = remove(img, session=session)

            safe_name = sanitize_filename(product_name)
            output_path = Path(OUTPUT_FOLDER) / safe_name
            output_img.save(output_path, "PNG")
            return f"Success: {image_path.name} -> {safe_name}"

        except Exception as e:
            output_path = Path(OUTPUT_FOLDER) / f"refined_{image_path.stem}.png"
            output_img = remove(img, session=session)
            output_img.save(output_path, "PNG")
            return f"Fallback: {image_path.name} (Logic Error: {e})"

    except Exception as e:
        return f"Failed: {image_path.name} (Error: {e})"

image_files = [
    p for p in Path(INPUT_FOLDER).glob("*")
    if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
]

print(f"Found {len(image_files)} images. Processing in parallel...")

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_image, image_files))

for r in results:
    print(r)

print("\nAll images processed.")
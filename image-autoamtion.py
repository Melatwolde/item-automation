import os
import google.genai as genai
from PIL import Image
from pathlib import Path
import time
from dotenv import load_dotenv
from rembg import remove
import base64
from io import BytesIO
import json

load_dotenv()

API_KEY = os.getenv("GEMAI")   

INPUT_FOLDER  = "/home/zoe/item-automation/raw_images"              
OUTPUT_FOLDER = "/home/zoe/item-automation/refined_images"        

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MODEL = "gemini-flash-latest"                       

client = genai.Client(api_key=API_KEY)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def sanitize_filename(text: str) -> str:
    text = text.strip().replace(" ", "_").replace("/", "-").replace("\\", "-")
    bad_chars = '<>:"/\\|?*'
    for c in bad_chars:
        text = text.replace(c, "")
    return text[:80] + ".png" 

def process_image(image_path: Path):
    print(f"\nProcessing: {image_path.name}")

    try:
        img = Image.open(image_path)

        prompt = f"""You are a professional e-commerce product photographer.

Analyze this product photo carefully.

Tasks:
1. Identify the main product in the image (be specific)
2. Suggest a clean, professional product title / name (short, descriptive, good for listing)
3. Generate a new version of this image with:
   - Pure white or transparent background
   - Professional studio lighting feel
   - Item perfectly centered
   - No people, no distractions, no warehouse background
   - If it's textile/furniture/clothing, show it nicely arranged (e.g. tablecloth spread out flat and smooth)

Return format (exactly this JSON structure):
{{
  "product_name": "short descriptive name",
  "clean_image": <the new refined image>
}}

Only return valid JSON. Do not add explanations."""

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        contents = [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": img_b64}}
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
            print(f"  Detected name: {product_name}")

            input_img = Image.open(image_path)
            output_img = remove(input_img)  # removes background

            # Save with meaningful name
            safe_name = sanitize_filename(product_name)
            output_path = Path(OUTPUT_FOLDER) / safe_name

            output_img.save(output_path, "PNG")
            print(f"  Saved refined image → {output_path.name}")

        except json.JSONDecodeError:
            print("  Gemini did not return valid JSON. Saving fallback name.")
            output_path = Path(OUTPUT_FOLDER) / f"refined_{image_path.stem}.png"
            # still save rembg version
            Image.open(image_path).save(output_path, "PNG")  # placeholder

    except Exception as e:
        print(f"  Error processing {image_path.name}: {e}")



image_files = [
    p for p in Path(INPUT_FOLDER).glob("*")
    if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
]

print(f"Found {len(image_files)} images to process.")

for idx, img_path in enumerate(image_files, 1):
    print(f"\n[{idx}/{len(image_files)}]")
    process_image(img_path)
    time.sleep(1.2)  

print("\nAll images processed.")
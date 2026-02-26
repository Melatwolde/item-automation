# automate.py
import pandas as pd
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError



BASE_URL     = "https://teter-erp.teterplc.com"
LOGIN_URL    = f"{BASE_URL}/login"
CREATE_URL   = f"{BASE_URL}/items/create"

EMAIL        = "admin@teterplc.com"             
PASSWORD     = "12345678"   
EXCEL_FILE   = "items.xlsx"

HEADLESS     = False                              
SLOW_MO      = 800                                
TIMEOUT      = 45000


COL_ITEM_TYPE    = "Item Type"     
COL_CATEGORY     = "Category"     
COL_ITEM_NAME    = "Item Name"
COL_STATUS       = "Status"         
COL_DESCRIPTION  = "Description"
COL_IMAGE_PATH   = "Image Path"     # full absolute path, e.g. C:/Photos/item1.png

# 

def select_select2(page, container_id, value_to_select):

    if not value_to_select or pd.isna(value_to_select):
        return

    value = str(value_to_select).strip()

    container_selector = f"#select2-{container_id}-container"
    container = page.locator(container_selector)

    # Click the selection area to open dropdown
    container.click(timeout=15000)

    # Wait for search field and type
    search_field = page.locator(".select2-search__field").first
    search_field.wait_for(state="visible", timeout=10000)
    search_field.clear()
    search_field.fill(value)

    # Wait for and click the matching result
    result = page.locator(".select2-results__option").filter(has_text=value).first
    result.wait_for(state="visible", timeout=10000)
    result.click(timeout=15000)

    # Quick confirmation
    selected = container.inner_text(timeout=5000).strip()
    print(f"  Selected '{value}' in {container_id} → confirmed: '{selected}'")




print(f"Loading {EXCEL_FILE} ...")
df = pd.read_excel(EXCEL_FILE)
print(f"→ {len(df)} items to process\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
    context = browser.new_context(viewport={"width": 1400, "height": 900})
    page = context.new_page()

    # ── Login ──
    print("Logging in...")
    page.goto(LOGIN_URL, wait_until="networkidle", timeout=TIMEOUT)

    page.locator('#email').fill(EMAIL)
    page.locator('#password').fill(PASSWORD)
    page.locator('#submitBtn').click(timeout=15000)

    page.wait_for_url(lambda u: any(x in u for x in ["/dashboard", "/items", "/home"]), timeout=30000)
    print("Login successful\n")


    for idx, row in df.iterrows():
        item_name = str(row.get(COL_ITEM_NAME, "")).strip() or "(no name)"
        print(f"[{idx+1}/{len(df)}] Creating: {item_name}")

        page.goto(CREATE_URL, wait_until="networkidle", timeout=TIMEOUT)

        try:
            #  Item Type (Select2) 
            select_select2(page, "type_id", row.get(COL_ITEM_TYPE))

            #  Category (Select2) 
            select_select2(page, "category_id", row.get(COL_CATEGORY))

            #  Item Name (normal input) 
            name_val = str(row.get(COL_ITEM_NAME, "")).strip()
            if name_val:
                page.locator('#name').fill(name_val, timeout=10000)
                print(f"  Item Name → {name_val}")

            #  Status (Select2) 
            select_select2(page, "status", row.get(COL_STATUS))

            #  Description (textarea) 
            desc = str(row.get(COL_DESCRIPTION, "")).strip()
            if desc:
                page.locator('#description').fill(desc, timeout=10000)
                print(f"  Description added (length: {len(desc)})")

            #  Image upload 
            if COL_IMAGE_PATH in row and pd.notna(row[COL_IMAGE_PATH]):
                img_raw = str(row[COL_IMAGE_PATH]).strip()
                img_path = os.path.abspath(img_raw) if not os.path.isabs(img_raw) else img_raw

                if os.path.isfile(img_path):
                    page.locator('input[type="file"]#image').set_input_files(img_path, timeout=20000)
                    print(f"  Image uploaded: {os.path.basename(img_path)}")
                else:
                    print(f"  Image not found: {img_path}")


            page.locator("button:has-text('Create Item')").click(timeout=15000)

            time.sleep(2.5)  

            print("  → Submitted\n")

        except Exception as e:
            print(f"  Error on row {idx+1}: {e}")
            page.screenshot(path=f"error-row-{idx+1}.png")

    print("All items processed.")
    browser.close()
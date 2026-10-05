import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryApp/1.0"}


def clean_product(product, barcode=""):
    return {
        "product_name": product.get("product_name") or "Unknown",
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "barcode": barcode or product.get("code", ""),
    }


def fetch_by_barcode(barcode):
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"
    response = requests.get(url, headers=HEADERS, timeout=10)
    data = response.json()
    if data.get("status") != 1:
        return None
    return clean_product(data["product"], barcode)


def search_by_name(name):
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }
    response = requests.get(
        f"{BASE_URL}/cgi/search.pl", params=params, headers=HEADERS, timeout=10
    )
    response.raise_for_status()
    products = response.json().get("products", [])
    if not products:
        return None
    return clean_product(products[0])

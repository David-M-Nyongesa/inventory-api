import requests
from flask import Flask, jsonify, request

from data import inventory, next_id
from external_api import fetch_by_barcode, search_by_name

app = Flask(__name__)

EDITABLE_FIELDS = ["product_name", "brands", "ingredients_text", "barcode", "price", "stock"]


def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def not_found():
    return jsonify({"error": "Item not found"}), 404


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory)


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return not_found()
    return jsonify(item)


@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True) or {}
    if not data.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    item = {
        "id": next_id(),
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0),
    }
    inventory.append(item)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return not_found()

    data = request.get_json(silent=True) or {}
    for field in EDITABLE_FIELDS:
        if field in data:
            item[field] = data[field]
    return jsonify(item)


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return not_found()

    inventory.remove(item)
    return jsonify({"message": "Item deleted"})


@app.route("/inventory/search", methods=["GET"])
def search_inventory():
    name = request.args.get("name", "").lower()
    results = [item for item in inventory if name in item["product_name"].lower()]
    return jsonify(results)


@app.route("/inventory/fetch", methods=["POST"])
def fetch_and_add():
    data = request.get_json(silent=True) or {}
    barcode = data.get("barcode")
    name = data.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide a barcode or a name"}), 400

    try:
        product = fetch_by_barcode(barcode) if barcode else search_by_name(name)
    except requests.RequestException:
        return jsonify({"error": "Could not reach OpenFoodFacts"}), 502

    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    product["id"] = next_id()
    product["price"] = data.get("price", 0)
    product["stock"] = data.get("stock", 0)
    inventory.append(product)
    return jsonify(product), 201


if __name__ == "__main__":
    app.run(debug=True)

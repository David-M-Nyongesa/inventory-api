import argparse

import requests

API_URL = "http://127.0.0.1:5000"


def show_item(item):
    print(
        f"[{item['id']}] {item['product_name']} ({item['brands']}) "
        f"- price: {item['price']}, stock: {item['stock']}"
    )


def show_error(response):
    print("Error:", response.json().get("error", "Something went wrong"))


def list_items(args):
    items = requests.get(f"{API_URL}/inventory").json()
    if not items:
        print("Inventory is empty")
    for item in items:
        show_item(item)


def get_item(args):
    response = requests.get(f"{API_URL}/inventory/{args.id}")
    if response.ok:
        show_item(response.json())
    else:
        show_error(response)


def add_item(args):
    payload = {
        "product_name": args.name,
        "brands": args.brand,
        "price": args.price,
        "stock": args.stock,
    }
    response = requests.post(f"{API_URL}/inventory", json=payload)
    if response.ok:
        print("Added:")
        show_item(response.json())
    else:
        show_error(response)


def update_item(args):
    fields = {
        "product_name": args.name,
        "brands": args.brand,
        "price": args.price,
        "stock": args.stock,
    }
    payload = {key: value for key, value in fields.items() if value is not None}
    if not payload:
        print("Nothing to update")
        return

    response = requests.patch(f"{API_URL}/inventory/{args.id}", json=payload)
    if response.ok:
        print("Updated:")
        show_item(response.json())
    else:
        show_error(response)


def delete_item(args):
    response = requests.delete(f"{API_URL}/inventory/{args.id}")
    if response.ok:
        print("Item deleted")
    else:
        show_error(response)


def search_items(args):
    response = requests.get(f"{API_URL}/inventory/search", params={"name": args.name})
    items = response.json()
    if not items:
        print("No matching items")
    for item in items:
        show_item(item)


def fetch_item(args):
    if not args.barcode and not args.name:
        print("Give a --barcode or a --name")
        return

    payload = {"barcode": args.barcode, "name": args.name, "price": args.price, "stock": args.stock}
    response = requests.post(f"{API_URL}/inventory/fetch", json=payload)
    if response.ok:
        print("Fetched and added:")
        show_item(response.json())
    else:
        show_error(response)


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory manager CLI")
    commands = parser.add_subparsers(dest="command", required=True)

    cmd = commands.add_parser("list", help="show all items")
    cmd.set_defaults(func=list_items)

    cmd = commands.add_parser("get", help="show one item")
    cmd.add_argument("id", type=int)
    cmd.set_defaults(func=get_item)

    cmd = commands.add_parser("add", help="add a new item")
    cmd.add_argument("--name", required=True)
    cmd.add_argument("--brand", default="")
    cmd.add_argument("--price", type=float, default=0)
    cmd.add_argument("--stock", type=int, default=0)
    cmd.set_defaults(func=add_item)

    cmd = commands.add_parser("update", help="update an item")
    cmd.add_argument("id", type=int)
    cmd.add_argument("--name")
    cmd.add_argument("--brand")
    cmd.add_argument("--price", type=float)
    cmd.add_argument("--stock", type=int)
    cmd.set_defaults(func=update_item)

    cmd = commands.add_parser("delete", help="delete an item")
    cmd.add_argument("id", type=int)
    cmd.set_defaults(func=delete_item)

    cmd = commands.add_parser("search", help="search inventory by name")
    cmd.add_argument("name")
    cmd.set_defaults(func=search_items)

    cmd = commands.add_parser("fetch", help="fetch a product from OpenFoodFacts and add it")
    cmd.add_argument("--barcode")
    cmd.add_argument("--name")
    cmd.add_argument("--price", type=float, default=0)
    cmd.add_argument("--stock", type=int, default=0)
    cmd.set_defaults(func=fetch_item)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except requests.exceptions.ConnectionError:
        print("Could not reach the API. Is the Flask server running?")


if __name__ == "__main__":
    main()

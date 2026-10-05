# Inventory Management API

A small inventory system for a retail store. It has a Flask REST API for managing items, a command line interface that talks to the API, and an integration with the [OpenFoodFacts API](https://world.openfoodfacts.org) to pull in product details by barcode or name.

Items are stored in a Python list (`data.py`), so the data resets every time the server restarts.

## Setup

```bash
git clone https://github.com/David-M-Nyongesa/inventory-api.git
cd inventory-api
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the project

Start the API in one terminal:

```bash
python app.py
```

The server runs on `http://127.0.0.1:5000`. Use the CLI from a second terminal.

## Project structure

```
app.py           Flask routes
data.py          mock database (a list) and the id helper
external_api.py  OpenFoodFacts requests
cli.py           command line interface
tests/           pytest test suite
```

## API endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/inventory` | Get all items |
| GET | `/inventory/<id>` | Get a single item |
| POST | `/inventory` | Add a new item |
| PATCH | `/inventory/<id>` | Update an item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/inventory/search?name=<text>` | Search the inventory by product name |
| POST | `/inventory/fetch` | Fetch a product from OpenFoodFacts and add it to the inventory |

Item format:

```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brands": "Silk",
  "ingredients_text": "Filtered water, almonds, cane sugar",
  "barcode": "025293600348",
  "price": 3.5,
  "stock": 20
}
```

Only `product_name` is required when adding an item.

`POST /inventory/fetch` expects a JSON body with either a `barcode` or a `name`. `price` and `stock` are optional.

```json
{ "barcode": "3017620422003", "stock": 10 }
```

Errors come back as `{"error": "..."}` with a 400, 404 or 502 status code.

## CLI usage

```bash
python cli.py list
python cli.py get 1
python cli.py add --name "Oat Milk" --brand "Oatly" --price 2.5 --stock 15
python cli.py update 1 --price 4 --stock 30
python cli.py delete 2
python cli.py search almond
python cli.py fetch --barcode 3017620422003 --price 6 --stock 10
python cli.py fetch --name "nutella" --stock 5
```

Run `python cli.py --help` to see all commands.

## Running the tests

```bash
pytest
```

The tests cover the API endpoints, the CLI commands and the OpenFoodFacts functions. External requests are mocked with `unittest.mock`, so no internet connection is needed.

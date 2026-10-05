import copy
from unittest.mock import patch

import pytest
import requests

from app import app
from data import inventory

SAMPLE = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds",
        "barcode": "111",
        "price": 3.5,
        "stock": 10,
    },
    {
        "id": 2,
        "product_name": "Peanut Butter",
        "brands": "Jif",
        "ingredients_text": "Peanuts, salt",
        "barcode": "222",
        "price": 4,
        "stock": 5,
    },
]

FETCHED = {
    "product_name": "Nutella",
    "brands": "Ferrero",
    "ingredients_text": "Sugar, palm oil, hazelnuts",
    "barcode": "3017620422003",
}


@pytest.fixture
def client():
    inventory.clear()
    inventory.extend(copy.deepcopy(SAMPLE))
    return app.test_client()


def test_get_all_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"


def test_get_missing_item(client):
    response = client.get("/inventory/99")
    assert response.status_code == 404


def test_add_item(client):
    response = client.post("/inventory", json={"product_name": "Oat Milk", "price": 2.5, "stock": 8})
    assert response.status_code == 201
    assert response.get_json()["id"] == 3
    assert len(inventory) == 3


def test_add_item_without_name(client):
    response = client.post("/inventory", json={"price": 2})
    assert response.status_code == 400
    assert len(inventory) == 2


def test_update_item(client):
    response = client.patch("/inventory/1", json={"price": 5, "stock": 30})
    assert response.status_code == 200
    assert response.get_json()["price"] == 5
    assert inventory[0]["stock"] == 30
    assert inventory[0]["product_name"] == "Organic Almond Milk"


def test_update_missing_item(client):
    response = client.patch("/inventory/99", json={"price": 5})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 200
    assert len(inventory) == 1
    assert client.get("/inventory/1").status_code == 404


def test_delete_missing_item(client):
    response = client.delete("/inventory/99")
    assert response.status_code == 404


def test_search_inventory(client):
    response = client.get("/inventory/search?name=butter")
    results = response.get_json()
    assert len(results) == 1
    assert results[0]["product_name"] == "Peanut Butter"


def test_search_no_match(client):
    response = client.get("/inventory/search?name=pizza")
    assert response.get_json() == []


def test_fetch_by_barcode_adds_item(client):
    with patch("app.fetch_by_barcode", return_value=dict(FETCHED)):
        response = client.post("/inventory/fetch", json={"barcode": "3017620422003", "stock": 6})
    assert response.status_code == 201
    assert response.get_json()["product_name"] == "Nutella"
    assert inventory[-1]["stock"] == 6
    assert len(inventory) == 3


def test_fetch_by_name_adds_item(client):
    with patch("app.search_by_name", return_value=dict(FETCHED)):
        response = client.post("/inventory/fetch", json={"name": "nutella"})
    assert response.status_code == 201
    assert len(inventory) == 3


def test_fetch_product_not_found(client):
    with patch("app.fetch_by_barcode", return_value=None):
        response = client.post("/inventory/fetch", json={"barcode": "000"})
    assert response.status_code == 404


def test_fetch_without_barcode_or_name(client):
    response = client.post("/inventory/fetch", json={})
    assert response.status_code == 400


def test_fetch_when_external_api_is_down(client):
    with patch("app.fetch_by_barcode", side_effect=requests.RequestException):
        response = client.post("/inventory/fetch", json={"barcode": "123"})
    assert response.status_code == 502

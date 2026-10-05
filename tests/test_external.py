from unittest.mock import MagicMock, patch

from external_api import fetch_by_barcode, search_by_name


def fake_response(data):
    response = MagicMock()
    response.json.return_value = data
    return response


@patch("external_api.requests.get")
def test_fetch_by_barcode_found(mock_get):
    mock_get.return_value = fake_response(
        {
            "status": 1,
            "product": {
                "product_name": "Organic Almond Milk",
                "brands": "Silk",
                "ingredients_text": "Filtered water, almonds",
            },
        }
    )
    product = fetch_by_barcode("12345")
    assert product["product_name"] == "Organic Almond Milk"
    assert product["brands"] == "Silk"
    assert product["barcode"] == "12345"


@patch("external_api.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_get.return_value = fake_response({"status": 0})
    assert fetch_by_barcode("000") is None


@patch("external_api.requests.get")
def test_search_by_name_found(mock_get):
    mock_get.return_value = fake_response(
        {"products": [{"product_name": "Nutella", "brands": "Ferrero", "code": "3017620422003"}]}
    )
    product = search_by_name("nutella")
    assert product["product_name"] == "Nutella"
    assert product["barcode"] == "3017620422003"


@patch("external_api.requests.get")
def test_search_by_name_no_results(mock_get):
    mock_get.return_value = fake_response({"products": []})
    assert search_by_name("zzzz") is None

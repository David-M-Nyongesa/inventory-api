from unittest.mock import MagicMock, patch

import requests

from cli import main

ITEM = {
    "id": 1,
    "product_name": "Organic Almond Milk",
    "brands": "Silk",
    "price": 3.5,
    "stock": 10,
}


def fake_response(data, ok=True):
    response = MagicMock()
    response.ok = ok
    response.json.return_value = data
    return response


@patch("cli.requests.get")
def test_list_items(mock_get, capsys):
    mock_get.return_value = fake_response([ITEM])
    main(["list"])
    assert "Organic Almond Milk" in capsys.readouterr().out


@patch("cli.requests.get")
def test_list_empty_inventory(mock_get, capsys):
    mock_get.return_value = fake_response([])
    main(["list"])
    assert "empty" in capsys.readouterr().out


@patch("cli.requests.get")
def test_get_item(mock_get, capsys):
    mock_get.return_value = fake_response(ITEM)
    main(["get", "1"])
    assert "Silk" in capsys.readouterr().out


@patch("cli.requests.get")
def test_get_missing_item(mock_get, capsys):
    mock_get.return_value = fake_response({"error": "Item not found"}, ok=False)
    main(["get", "99"])
    assert "Item not found" in capsys.readouterr().out


@patch("cli.requests.post")
def test_add_item(mock_post, capsys):
    mock_post.return_value = fake_response(ITEM)
    main(["add", "--name", "Organic Almond Milk", "--brand", "Silk", "--price", "3.5", "--stock", "10"])
    sent = mock_post.call_args.kwargs["json"]
    assert sent["product_name"] == "Organic Almond Milk"
    assert sent["stock"] == 10
    assert "Added" in capsys.readouterr().out


@patch("cli.requests.patch")
def test_update_item(mock_patch, capsys):
    mock_patch.return_value = fake_response(ITEM)
    main(["update", "1", "--price", "9"])
    assert mock_patch.call_args.kwargs["json"] == {"price": 9.0}
    assert "Updated" in capsys.readouterr().out


@patch("cli.requests.patch")
def test_update_with_no_fields(mock_patch, capsys):
    main(["update", "1"])
    mock_patch.assert_not_called()
    assert "Nothing to update" in capsys.readouterr().out


@patch("cli.requests.delete")
def test_delete_item(mock_delete, capsys):
    mock_delete.return_value = fake_response({"message": "Item deleted"})
    main(["delete", "1"])
    assert "deleted" in capsys.readouterr().out


@patch("cli.requests.get")
def test_search_items(mock_get, capsys):
    mock_get.return_value = fake_response([ITEM])
    main(["search", "almond"])
    assert mock_get.call_args.kwargs["params"] == {"name": "almond"}
    assert "Organic Almond Milk" in capsys.readouterr().out


@patch("cli.requests.post")
def test_fetch_item(mock_post, capsys):
    mock_post.return_value = fake_response(ITEM)
    main(["fetch", "--barcode", "12345", "--stock", "4"])
    sent = mock_post.call_args.kwargs["json"]
    assert sent["barcode"] == "12345"
    assert sent["stock"] == 4
    assert "Fetched and added" in capsys.readouterr().out


def test_fetch_without_barcode_or_name(capsys):
    main(["fetch"])
    assert "--barcode" in capsys.readouterr().out


@patch("cli.requests.get", side_effect=requests.exceptions.ConnectionError)
def test_server_not_running(mock_get, capsys):
    main(["list"])
    assert "Could not reach the API" in capsys.readouterr().out

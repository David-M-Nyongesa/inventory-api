inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "barcode": "025293600348",
        "price": 3.5,
        "stock": 20,
    },
    {
        "id": 2,
        "product_name": "Crunchy Peanut Butter",
        "brands": "Jif",
        "ingredients_text": "Roasted peanuts, sugar, salt",
        "barcode": "051500240663",
        "price": 4.25,
        "stock": 12,
    },
]


def next_id():
    return max((item["id"] for item in inventory), default=0) + 1

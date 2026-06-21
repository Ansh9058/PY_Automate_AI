from typing import List, Dict
import csv
import json
import os


def save_products_csv(products: List[Dict[str, str]], path: str) -> str:
    """Save product list to CSV file. Returns final path."""
    if not products:
        raise ValueError("No products to save")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    fieldnames = ["title", "price", "image_url", "description"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow({k: p.get(k, "") for k in fieldnames})

    return path


def save_products_json(products: List[Dict[str, str]], path: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    return path

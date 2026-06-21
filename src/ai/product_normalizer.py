from typing import List, Dict
import re
def normalize_products(products: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Basic 'AI-like' normalization:
    - clean currency symbols
    - normalize whitespace
    - extract numeric price
    """
    normalized = []
    for p in products:
        title = (p.get("title") or "").strip()
        desc = (p.get("description") or "").strip()
        price_raw = (p.get("price") or "").strip()

        # Extract numeric price
        price_num = None
        match = re.search(r"(\d+[.,]?\d*)", price_raw.replace(",", ""))
        if match:
            try:
                price_num = float(match.group(1))
            except ValueError:
                price_num = None

        normalized.append(
            {
                "title": title,
                "description": desc,
                "price_raw": price_raw,
                "price_value": price_num,
                "image_url": p.get("image_url") or "",
            }
        )
    return normalized

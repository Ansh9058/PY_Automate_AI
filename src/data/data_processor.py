from typing import List, Dict, Any
import re


class DataProcessor:
    """
    Cleans, normalizes and structures raw scraped data.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        text = text.replace("\n", " ").replace("\t", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def normalize_price(price: str) -> str:
        if not price:
            return ""
        return re.sub(r"[^\d.]", "", price)

    @staticmethod
    def normalize_dataset(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []

        for item in data:
            clean_item = {}
            for k, v in item.items():
                if isinstance(v, str):
                    clean_item[k] = DataProcessor.clean_text(v)
                else:
                    clean_item[k] = v
            cleaned.append(clean_item)

        return cleaned

    @staticmethod
    def summarize_dataset(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "total_records": len(data),
            "fields": list(data[0].keys()) if data else [],
        }

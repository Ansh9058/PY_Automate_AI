import requests
from data.data_processor import DataProcessor
class APIScraper:
    def fetch(self, url: str, headers: dict = None):
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            return DataProcessor.normalize_dataset(data)

        return data

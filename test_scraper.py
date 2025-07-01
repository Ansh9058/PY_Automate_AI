import requests

def test_scraper():
    url = "http://127.0.0.1:8080/api/v1/rpa/scrape-products"
    
    # Request data with proper formatting
    data = {
        "url": "https://www.amazon.com/s?k=laptop",
        "selectors": {
            "product_container": "div[data-component-type=\"s-search-result\"]",
            "title": "h2 a span",
            "price": ".a-price .a-offscreen",
            "image": "img.s-image",
            "description": ".a-size-base"
        }
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        
        result = response.json()
        print("Success!")
        print(f"Status: {result.get('status')}")
        if 'products' in result:
            print(f"Found {len(result['products'])} products")
            for i, product in enumerate(result['products'], 1):
                print(f"\nProduct {i}:")
                print(f"Title: {product.get('title', 'N/A')}")
                print(f"Price: {product.get('price', 'N/A')}")
                print("-" * 50)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    test_scraper()

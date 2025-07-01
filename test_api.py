import requests
import json

def test_scraper():
    url = "http://127.0.0.1:8080/api/v1/rpa/scrape-products"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    data = {
        "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
        "selectors": {
            "product_container": '.thumbnail',
            "title": 'a.title',
            "price": '.price',
            "image": 'img.img-responsive',
            "description": 'p.description'
        }
    }
    
    try:
        print("Sending request to scrape products...")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"\nStatus: {result.get('status')}")
        
        if 'products' in result:
            products = result['products']
            print(f"Found {len(products)} products")
            
            # Clean up and format the results
            cleaned_products = []
            for product in products:
                # Clean and normalize the data
                title = str(product.get('title', 'N/A')).strip()
                price = str(product.get('price', 'N/A')).strip()
                image_url = str(product.get('image_url', 'N/A')).strip()
                description = str(product.get('description', 'N/A')).strip()
                
                # Create cleaned product with truncated fields
                cleaned_product = {
                    'title': (title[:47] + '...') if len(title) > 50 else title,
                    'price': price[:20],
                    'image_url': image_url,
                    'description': (description[:97] + '...') if len(description) > 100 else description
                }
                cleaned_products.append(cleaned_product)
            
            # Create cleaned result
            cleaned_result = {
                'status': result['status'],
                'count': len(cleaned_products),
                'products': cleaned_products
            }
            
            # Save results to a file with proper encoding
            with open('scraped_products.json', 'w', encoding='utf-8') as f:
                json.dump(cleaned_result, f, indent=2, ensure_ascii=False)
            print("\nResults saved to 'scraped_products.json'")
            
            # Print first 3 products
            for i, product in enumerate(products[:3], 1):
                print(f"\nProduct {i}:")
                print(f"Title: {product.get('title', 'N/A')}")
                print(f"Price: {product.get('price', 'N/A')}")
                print(f"Image URL: {product.get('image_url', 'N/A')}")
                print("-" * 50)
                
            if len(products) > 3:
                print(f"\n... and {len(products) - 3} more products")
                
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    test_scraper()

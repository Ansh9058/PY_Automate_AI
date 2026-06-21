import requests
import json

def test_web_scraping():
    # URL of the web scraping endpoint
    url = "http://127.0.0.1:8080/api/v1/rpa/web-scrape"
    
    # Example: Scraping movie information from Wikipedia
    task = {
        "url": "https://en.wikipedia.org/wiki/List_of_highest-grossing_films",
        "selectors": {
            "title": "h1#firstHeading",
            "introduction": "div.mw-parser-output > p:not(.mw-empty-elt)",
            "movie_table": "table.wikitable",
            "movie_rows": "table.wikitable tbody tr",
            "movie_rank": "td:nth-child(1)",
            "movie_title": "td:nth-child(2)",
            "movie_gross": "td:nth-child(3)",
            "movie_year": "td:nth-child(4)",
            "movie_references": "div.references"
        }
    }
    
    try:
        print("Sending request to scrape movie information from Wikipedia...")
        response = requests.post(url, json=task)
        
        # Print the response
        print("\nStatus Code:", response.status_code)
        if response.status_code == 200:
            result = response.json()
            print("\nScraped Data:")
            print("-" * 50)
            
            # Format the output nicely
            if result.get("status") == "success":
                data = result.get("data", {})
                
                # Print title
                print("\nTitle:", data.get("title", "Not found"))
                
                # Print introduction
                print("\nIntroduction:")
                intro = data.get("introduction", [])
                if intro:
                    if isinstance(intro, list):
                        print(" ".join(intro))
                    else:
                        print(intro)
                
                # Print movie information
                print("\nTop Movies:")
                movie_rows = data.get("movie_rows", [])
                if movie_rows:
                    if isinstance(movie_rows, list):
                        for row in movie_rows:
                            if isinstance(row, dict):
                                rank = row.get("movie_rank", "N/A")
                                title = row.get("movie_title", "N/A")
                                gross = row.get("movie_gross", "N/A")
                                year = row.get("movie_year", "N/A")
                                print(f"\nRank: {rank}")
                                print(f"Title: {title}")
                                print(f"Gross: {gross}")
                                print(f"Year: {year}")
                                print("-" * 30)
                    else:
                        print(movie_rows)
                
                # Print references
                print("\nReferences:")
                refs = data.get("movie_references", [])
                if refs:
                    if isinstance(refs, list):
                        print("\n".join(refs))
                    else:
                        print(refs)
            else:
                print(json.dumps(result, indent=2))
        else:
            print("Error:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure the FastAPI server is running.")
        print("Run 'python main.py' in a separate terminal to start the server.")
    except Exception as e:
        print("\nError:", str(e))

if __name__ == "__main__":
    test_web_scraping() 
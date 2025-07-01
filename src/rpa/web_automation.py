from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class WebAutomation:
    def __init__(self, headless: bool = True):
        """Initialize web automation with Selenium WebDriver."""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        
        # Basic options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-automation')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Window size and zoom
        options.add_argument('--start-maximized')
        options.add_argument('--force-device-scale-factor=1')
        
        # Privacy and security
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        
        # User agent and language
        options.add_argument('--lang=en-US')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Additional preferences
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Set window size
        self.driver.set_window_size(1920, 1080)
        
        # Set page load strategy
        self.driver.implicitly_wait(10)
        
    def navigate(self, url: str) -> None:
        """Navigate to a specific URL."""
        try:
            self.driver.get(url)
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            # Additional wait for dynamic content
            import time
            time.sleep(5)  # Give JavaScript time to render
            logger.info(f"Navigated to {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise
            
    def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from webpage using provided CSS selectors."""
        results = {}
        for key, selector in selectors.items():
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                results[key] = element.text
            except Exception as e:
                logger.error(f"Failed to extract {key}: {str(e)}")
                results[key] = None
        return results

    def extract_products(self, selectors: Dict[str, str]) -> List[Dict[str, str]]:
        """Extract product information from an e-commerce website
        
        Args:
            selectors (Dict[str, str]): Dictionary containing CSS selectors for product elements
                Required keys:
                - product_container: Selector for the main product container
                - title: Selector for product title
                - price: Selector for product price
                - image: Selector for product image
                - description: Selector for product description
        
        Returns:
            List[Dict[str, str]]: List of products with their details
        """
        products = []
        try:
            # Scroll down to load all products
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                import time
                time.sleep(2)  # Wait for content to load
                
                # Calculate new scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Wait for product containers with a longer timeout
            containers = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, selectors['product_container'])
                )
            )
            
            logger.info(f"Found {len(containers)} product containers")
            
            # Extract information from each product container
            for container in containers:
                try:
                    # Wait for container to be visible
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of(container)
                    )
                    
                    product = {}
                    
                    # Extract title with wait
                    try:
                        title_element = WebDriverWait(container, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selectors['title']))
                        )
                        title = title_element.text.strip()
                        # Clean and truncate title
                        product['title'] = (title[:50] + '...') if len(title) > 50 else title
                    except Exception as e:
                        logger.error(f"Failed to extract title: {str(e)}")
                        product['title'] = 'N/A'
                    
                    # Extract price with wait
                    try:
                        price_element = WebDriverWait(container, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selectors['price']))
                        )
                        price = price_element.text.strip()
                        # Clean price
                        product['price'] = price[:20] if price else 'N/A'
                    except Exception as e:
                        logger.error(f"Failed to extract price: {str(e)}")
                        product['price'] = 'N/A'
                    
                    # Extract image URL with wait
                    try:
                        img_element = WebDriverWait(container, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selectors['image']))
                        )
                        img_url = img_element.get_attribute('src')
                        # Clean URL
                        product['image_url'] = img_url if img_url else 'N/A'
                    except Exception as e:
                        logger.error(f"Failed to extract image URL: {str(e)}")
                        product['image_url'] = 'N/A'
                    
                    # Extract description with wait
                    try:
                        desc_element = WebDriverWait(container, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selectors['description']))
                        )
                        desc = desc_element.text.strip()
                        # Clean and truncate description
                        product['description'] = (desc[:100] + '...') if len(desc) > 100 else desc
                    except Exception as e:
                        logger.error(f"Failed to extract description: {str(e)}")
                        product['description'] = 'N/A'
                    
                    # Only add products that have at least a title or price
                    if product['title'] != 'N/A' or product['price'] != 'N/A':
                        products.append(product)
                        logger.info(f"Extracted product: {product['title'][:50]}...")
                        
                except Exception as e:
                    logger.error(f"Failed to process product container: {str(e)}")
                    continue
            
            logger.info(f"Successfully extracted {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Failed to extract products: {str(e)}")
            raise
    
    def fill_form(self, form_data: Dict[str, str]) -> None:
        """Fill form fields with provided data."""
        for selector, value in form_data.items():
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                element.clear()
                element.send_keys(value)
                logger.info(f"Filled form field {selector}")
            except Exception as e:
                logger.error(f"Failed to fill form field {selector}: {str(e)}")
                raise
                
    def click_element(self, selector: str) -> None:
        """Click an element on the webpage."""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            logger.info(f"Clicked element {selector}")
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {str(e)}")
            raise
            
    def close(self) -> None:
        """Close the browser and clean up resources."""
        self.driver.quit()
        logger.info("Closed browser session")

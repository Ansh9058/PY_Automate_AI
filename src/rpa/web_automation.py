from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from typing import Dict, Any, List
import logging
import time

# Optional data processing
try:
    from data.data_processor import DataProcessor
    DATA_PROCESSOR_AVAILABLE = True
except Exception:
    DATA_PROCESSOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class WebAutomation:
    """
    Advanced Web Scraping Engine
    - Websites (HTML)
    - Infinite scroll
    - Cleaned & normalized output
    """

    def __init__(self, headless: bool = True):
        options = Options()

        if headless:
            options.add_argument("--headless=new")

        # Stability & performance
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Anti-automation
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.USER_AGENT = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={self.USER_AGENT}")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

        # Stronger bot evasion (best-effort)
        try:
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {"userAgent": self.USER_AGENT},
            )
        except Exception:
            pass

        self.driver.implicitly_wait(10)

    # ==================================================
    # NAVIGATION
    # ==================================================
    def navigate(self, url: str) -> None:
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)
        logger.info("Navigated to %s", url)

    # ==================================================
    # SCROLLING (LAZY LOAD / INFINITE SCROLL)
    # ==================================================
    def _scroll_full_page(self, max_scrolls: int = 30, delay: float = 0.8) -> None:
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for _ in range(max_scrolls):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(delay)
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            if new_height == last_height:
                break
            last_height = new_height

    # ==================================================
    # SIMPLE DATA EXTRACTION
    # ==================================================
    def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        results = {}
        for key, css in selectors.items():
            try:
                element = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css))
                )
                results[key] = element.text.strip()
            except Exception:
                results[key] = None
        return results

    # ==================================================
    # ADVANCED PRODUCT SCRAPING
    # ==================================================
    def extract_products(self, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Large-scale product scraping with normalization.

        Required selectors:
            product_container, title, price, image
        """

        required = ["product_container", "title", "price", "image"]
        for r in required:
            if r not in selectors:
                raise ValueError(f"Missing selector: {r}")

        self._scroll_full_page()

        containers = WebDriverWait(self.driver, 25).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, selectors["product_container"])
            )
        )

        products: List[Dict[str, Any]] = []

        for container in containers:
            product = {}

            def safe_text(css: str) -> str:
                try:
                    return container.find_element(By.CSS_SELECTOR, css).text.strip()
                except Exception:
                    return ""

            product["title"] = safe_text(selectors["title"])
            product["price"] = safe_text(selectors["price"])

            try:
                img = container.find_element(By.CSS_SELECTOR, selectors["image"])
                product["image_url"] = img.get_attribute("src") or ""
            except Exception:
                product["image_url"] = ""

            desc_sel = selectors.get("description")
            product["description"] = safe_text(desc_sel) if desc_sel else ""

            if product["title"] or product["price"]:
                products.append(product)

        # ---------------- DATA PROCESSING ----------------
        if DATA_PROCESSOR_AVAILABLE:
            products = DataProcessor.normalize_dataset(products)

        logger.info("Scraped %d products", len(products))
        return products

    # ==================================================
    # FORM & CLICK AUTOMATION
    # ==================================================
    def fill_form(self, form_data: Dict[str, str]) -> None:
        for selector, value in form_data.items():
            element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(value)

    def click_element(self, selector: str) -> None:
        element = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.click()

    # ==================================================
    # CLEANUP
    # ==================================================
    def close(self) -> None:
        try:
            self.driver.quit()
        except Exception:
            pass
        logger.info("Browser closed")

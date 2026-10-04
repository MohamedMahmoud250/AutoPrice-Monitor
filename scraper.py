import re 
import time 
from bs4 import BeautifulSoup 
from playwright.sync_api import sync_playwright 
 
def clean_price(price_str): 
    if price_str is None or price_str == "": 
        return "N/A" 
     
    # Clean the text and extract the number
    s = str(price_str).replace(',', '') 
    match = re.search(r'\d+(?:\.\d+)?', s) 
    if match: 
        try: 
            val = float(match.group()) 
            if val > 0: 
                return f"{val:.2f}" 
        except (ValueError, TypeError): 
            pass 
             
    return "N/A" 
 
def scrape_with_playwright(url): 
    """Open a real browser simulation to bypass blocking and wait for prices to fully load""" 
    try: 
        with sync_playwright() as p: 
            # Launch a hidden browser (Headless)
            browser = p.chromium.launch( 
                headless=True, 
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"] 
            ) 
             
            # Open the page with Arabic language and local region settings
            context = browser.new_context( 
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", 
                locale="ar-EG", 
                extra_http_headers={"Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8"} 
            ) 
             
            page = context.new_page() 
             
            # Navigate to the URL and wait for the DOM content to load
            page.goto(url, timeout=30000, wait_until="domcontentloaded") 
            time.sleep(3)  # Give JavaScript 3 seconds to load the final price
             
            content = page.content() 
            browser.close() 
             
            soup = BeautifulSoup(content, 'html.parser') 
             
            # Determine price elements based on the store
            u = url.lower() 
            selectors = [] 
             
            if 'amazon' in u: 
                selectors = [ 
                    '#corePrice_feature_div span.a-offscreen', 
                    '#corePriceDisplay_desktop_feature_div span.a-offscreen', 
                    '.apexPriceToPay span.a-offscreen', 
                    'span.a-price span.a-offscreen', 
                    '#priceblock_ourprice', 
                    '#priceblock_dealprice' 
                ] 
            elif 'noon' in u: 
                selectors = [ 
                    '[data-qa="product-price"]', 
                    '.priceNow', 
                    '.p-price', 
                    'span.price' 
                ] 
            elif 'jumia' in u: 
                selectors = [ 
                    'span.-b.-ltr.-tal.-prsm', 
                    'span.-b.-ltr.-tal.-fs24', 
                    '.prc' 
                ] 
            else: 
                selectors = ['.price', '.product-price', '[itemprop="price"]'] 
 
            for sel in selectors: 
                elem = soup.select_one(sel) 
                if elem: 
                    p = clean_price(elem.get_text()) 
                    if p != "N/A": 
                        return p 
 
            # Fallback attempt to search for itemprop="price"
            prop_elem = soup.select_one('[itemprop="price"]') 
            if prop_elem: 
                p = clean_price(prop_elem.get('content', prop_elem.get_text())) 
                if p != "N/A": 
                    return p 
 
    except Exception as e: 
        print(f"Playwright Scrape Error for {url}: {e}") 
 
    return "N/A" 
 
def get_product_price(url): 
    if not url or not isinstance(url, str): 
        return "N/A" 
    return scrape_with_playwright(url)
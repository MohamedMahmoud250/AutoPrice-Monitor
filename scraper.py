import re 
import json 
import time 
import random 
from bs4 import BeautifulSoup 
from curl_cffi import requests as curl_requests 
 
def clean_price(price_str): 
    if price_str is None or price_str == "": 
        return "N/A" 
     
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
 
def scrape_amazon(url): 
    """Scrape Amazon prices with high flexibility to prevent N/A results""" 
    headers = { 
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", 
        "accept-language": "en-US,en;q=0.9,ar;q=0.8", 
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36" 
    } 
 
    for attempt in range(3): 
        try: 
            time.sleep(random.uniform(1.0, 2.5)) 
            session = curl_requests.Session(impersonate="chrome120") 
            res = session.get(url, headers=headers, timeout=15) 
             
            if res.status_code == 200: 
                soup = BeautifulSoup(res.text, 'html.parser') 
                 
                amazon_selectors = [ 
                    'span.a-price span.a-offscreen', 
                    '#corePrice_feature_div span.a-offscreen', 
                    '#corePriceDisplay_desktop_feature_div span.a-offscreen', 
                    '#priceblock_ourprice', 
                    '#priceblock_dealprice', 
                    '.apexPriceToPay span.a-offscreen', 
                    'span.a-price-whole', 
                    '.a-price .a-offscreen' 
                ] 
                 
                for sel in amazon_selectors: 
                    elem = soup.select_one(sel) 
                    if elem: 
                        p = clean_price(elem.get_text()) 
                        if p != "N/A": 
                            return p 
                             
                prop_elem = soup.select_one('[itemprop="price"]') 
                if prop_elem: 
                    p = clean_price(prop_elem.get('content', prop_elem.get_text())) 
                    if p != "N/A": 
                        return p 
 
        except Exception as e: 
            print(f"Amazon Scrape Attempt {attempt+1} Error: {e}") 
 
    return "N/A" 
 
def scrape_noon_special(url): 
    """Scrape Noon prices""" 
    headers = { 
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
        "accept-language": "ar-EG,ar;q=0.9,en-US;q=0.8", 
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" 
    } 
 
    for attempt in range(3): 
        try: 
            time.sleep(random.uniform(1.0, 2.0)) 
            session = curl_requests.Session(impersonate="chrome120") 
            response = session.get(url, headers=headers, timeout=15) 
             
            if response.status_code == 200: 
                soup = BeautifulSoup(response.text, 'html.parser') 
                 
                selectors = [ 
                    '[data-qa="product-price"]', 
                    '.priceNow', 
                    '.p-price', 
                    'span.price' 
                ] 
                for sel in selectors: 
                    elem = soup.select_one(sel) 
                    if elem: 
                        p = clean_price(elem.get_text()) 
                        if p != "N/A": 
                            return p 
 
                next_data = soup.find('script', id='__NEXT_DATA__') 
                if next_data and next_data.string: 
                    price_matches = re.findall(r'"sale_price"\s*:\s*([\d\.]+)|"price"\s*:\s*([\d\.]+)', next_data.string) 
                    for match in price_matches: 
                        for p in match: 
                            if p: 
                                price_clean = clean_price(p) 
                                if price_clean != "N/A": 
                                    return price_clean 
        except Exception as e: 
            print(f"Noon Scrape Error: {e}") 
 
    return "N/A" 
 
def scrape_jumia(url): 
    headers = {"accept-language": "en-US,en;q=0.9,ar;q=0.8"} 
    for attempt in range(3): 
        try: 
            time.sleep(random.uniform(1.0, 2.0)) 
            session = curl_requests.Session(impersonate="chrome120") 
            res = session.get(url, headers=headers, timeout=15) 
             
            if res.status_code == 200: 
                soup = BeautifulSoup(res.text, 'html.parser') 
                selectors = ['span.-b.-ltr.-tal.-prsm', 'span.-b.-ltr.-tal.-fs24', '.prc'] 
                for sel in selectors: 
                    elem = soup.select_one(sel) 
                    if elem: 
                        p = clean_price(elem.get_text()) 
                        if p != "N/A": 
                            return p 
        except Exception as e: 
            print(f"Jumia Scrape Error: {e}") 
 
    return "N/A" 
 
def get_product_price(url): 
    if not url or not isinstance(url, str): 
        return "N/A" 
     
    u = url.lower() 
    if 'noon' in u: 
        return scrape_noon_special(url) 
    elif 'amazon' in u: 
        return scrape_amazon(url) 
    elif 'jumia' in u: 
        return scrape_jumia(url) 
    return "N/A"
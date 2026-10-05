import re
import json
import time
import random
import cloudscraper
from bs4 import BeautifulSoup

def clean_price(price_str):
    if not price_str:
        return "N/A"
    text = str(price_str).replace(',', '').replace('\xa0', ' ').strip()
    match = re.search(r'\d+(?:\.\d+)?', text)
    if match:
        try:
            val = float(match.group())
            if val > 0:
                return f"{val:.2f}"
        except ValueError:
            pass
    return "N/A"

def scrape_amazon(url):
    clean_url = url.split('?')[0]
    
    # استخدام cloudscraper لتجاوز حماية Bot Detection
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    headers = {
        'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    cookies = {
        'i18n-prefs': 'EGP',
        'lc-main': 'ar_AE',
    }

    try:
        res = scraper.get(clean_url, headers=headers, cookies=cookies, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1. البحث المباشر في عنصر سعر الشراء الرئيسي المخصص لأمازون مصر
            price_span = soup.find("span", {"class": "a-price-whole"})
            if price_span:
                fraction_span = soup.find("span", {"class": "a-price-fraction"})
                whole = price_span.get_text().replace('.', '').replace(',', '').strip()
                fraction = fraction_span.get_text().strip() if fraction_span else "00"
                if whole.isdigit():
                    return f"{float(whole + '.' + fraction):.2f}"

            # 2. البحث عن a-offscreen السعر الرئيسي فقط وليس الشحن
            core_price = soup.select_one('#corePrice_feature_div .a-offscreen, #corePriceDisplay_desktop_feature_div .a-offscreen')
            if core_price:
                p = clean_price(core_price.get_text())
                if p != "N/A":
                    return p

            # 3. جلب السعر من البيانات المبسطة JSON-LD
            for script in soup.find_all('script', type='application/ld+json'):
                if script.string:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, list): data = data[0]
                        offers = data.get('offers')
                        if offers:
                            if isinstance(offers, list): offers = offers[0]
                            price = offers.get('price')
                            if price:
                                p = clean_price(price)
                                if p != "N/A":
                                    return p
                    except Exception:
                        continue

    except Exception as e:
        print(f"Amazon Scrape Error: {e}")

    return "N/A"

def scrape_noon_special(url):
    scraper = cloudscraper.create_scraper()
    headers = {'Accept-Language': 'ar-EG,ar;q=0.9'}
    try:
        res = scraper.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            next_data = soup.find('script', id='__NEXT_DATA__')
            if next_data and next_data.string:
                price_matches = re.findall(r'"sale_price"\s*:\s*([\d\.]+)|"price"\s*:\s*([\d\.]+)', next_data.string)
                for match in price_matches:
                    for p in match:
                        if p and float(p) > 0:
                            return clean_price(p)
    except Exception as e:
        print(f"Noon Scrape Error: {e}")
    return "N/A"

def get_product_price(url):
    if not url or not isinstance(url, str):
        return "N/A"
    u = url.lower()
    if 'noon' in u:
        return scrape_noon_special(url)
    elif 'amazon' in u:
        return scrape_amazon(url)
    return "N/A"
import re
import json
import time
import random
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

def clean_price(price_str):
    if price_str is None or price_str == "":
        return "N/A"
    cleaned = re.sub(r'[^\d.]', '', str(price_str).replace(',', ''))
    try:
        val = float(cleaned)
        return f"{val:.2f}" if val > 0 else "N/A"
    except (ValueError, TypeError):
        return "N/A"

def scrape_noon_special(url):
    """مخصص لسحب منتجات نون وتجاوز نظام الحظر مع محاولات إعادة الطلب"""
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    # إعادة المحاولة حتى 3 مرات في حال الفشل
    for attempt in range(3):
        try:
            time.sleep(random.uniform(1.0, 2.5))  # تأخير عشوائي لتفادي الحظر
            session = curl_requests.Session(impersonate="chrome120")
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # 1. البحث في __NEXT_DATA__
                next_data = soup.find('script', id='__NEXT_DATA__')
                if next_data and next_data.string:
                    try:
                        price_matches = re.findall(r'"price"\s*:\s*([\d\.]+)|"sale_price"\s*:\s*([\d\.]+)', next_data.string)
                        for match in price_matches:
                            for p in match:
                                if p:
                                    price_clean = clean_price(p)
                                    if price_clean != "N/A":
                                        return price_clean
                    except Exception:
                        pass

                # 2. البحث عن عناصر CSS Selector
                selectors = [
                    '[data-qa="product-price"]',
                    '.priceNow',
                    '.amount',
                    '.p-price',
                    'span.price'
                ]
                for sel in selectors:
                    elem = soup.select_one(sel)
                    if elem:
                        p = clean_price(elem.get_text())
                        if p != "N/A":
                            return p

                # 3. Regex شامل داخل الـ HTML
                all_prices = re.findall(r'"price"\s*:\s*([\d\.]+)|"sale_price"\s*:\s*([\d\.]+)', html)
                for p_tuple in all_prices:
                    for p in p_tuple:
                        if p:
                            price_clean = clean_price(p)
                            if price_clean != "N/A":
                                return price_clean
        except Exception as e:
            print(f"Noon Scrape Attempt {attempt+1} Error: {e}")

    return "N/A"

def scrape_amazon(url):
    """استخدام curl_cffi لاستخدام ميزة impersonate لمنع حظر أمازون"""
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
        "device-memory": "8",
        "viewport-width": "1920"
    }

    for attempt in range(3):
        try:
            time.sleep(random.uniform(1.5, 3.0))
            session = curl_requests.Session(impersonate="chrome120")
            res = session.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                selectors = [
                    '.a-price .a-offscreen',
                    '#priceblock_ourprice',
                    '#priceblock_dealprice',
                    '.corePrice_feature_div .a-price .a-offscreen',
                    'span.a-price-whole'
                ]
                for sel in selectors:
                    elem = soup.select_one(sel)
                    if elem:
                        p = clean_price(elem.get_text())
                        if p != "N/A":
                            return p
        except Exception as e:
            print(f"Amazon Scrape Attempt {attempt+1} Error: {e}")

    return "N/A"

def scrape_jumia(url):
    """مخصص لسحب منتجات جوميا مع محاولات إعادة الطلب"""
    headers = {
        "accept-language": "en-US,en;q=0.9,ar;q=0.8"
    }
    for attempt in range(3):
        try:
            time.sleep(random.uniform(1.0, 2.0))
            session = curl_requests.Session(impersonate="chrome120")
            res = session.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                selectors = [
                    'span.-b.-ltr.-tal.-prsm',
                    'span.-b.-ltr.-tal.-fs24',
                    '.prc',
                    '[data-price]'
                ]
                for sel in selectors:
                    elem = soup.select_one(sel)
                    if elem:
                        p = clean_price(elem.get_text())
                        if p != "N/A":
                            return p
        except Exception as e:
            print(f"Jumia Scrape Attempt {attempt+1} Error: {e}")

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
    else:
        for attempt in range(2):
            try:
                session = curl_requests.Session(impersonate="chrome120")
                res = session.get(url, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    for sel in ['.price', '.product-price', '[itemprop="price"]']:
                        elem = soup.select_one(sel)
                        if elem:
                            p = clean_price(elem.get_text())
                            if p != "N/A":
                                return p
            except Exception:
                pass

    return "N/A"
import re
import json
import time
import random
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

# سعر صرف احتياطي في حالة إصرار السيرفر الأمريكي على إرجاع السعر بالدولار
USD_TO_EGP_RATE = 49.5

def clean_price(price_str):
    """تنظيف النص واستخراج الرقم فقط"""
    if price_str is None or price_str == "":
        return None
    
    # إزالة الفواصل والرموز
    text = str(price_str).replace(',', '').replace('\xa0', ' ').strip()
    match = re.search(r'\d+(?:\.\d+)?', text)
    if match:
        try:
            val = float(match.group())
            if val > 0:
                return val
        except ValueError:
            pass
    return None

def scrape_amazon(url):
    """جلب سعر منتج أمازون بأسلوب هجين محترف"""
    # تنظيف الرابط وإضافة متغيرات اللغة والعملة الإجبارية
    clean_url = url.split('?')[0]
    target_url = f"{clean_url}?language=ar_AE&currency=EGP"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "ar-EG,ar;q=0.9,en-US;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    cookies = {
        "i18n-prefs": "EGP",
        "lc-main": "ar_AE",
        "session-id-time": "2082787201l"
    }

    for attempt in range(3):
        try:
            time.sleep(random.uniform(1.0, 2.0))
            session = curl_requests.Session(impersonate="chrome120")
            res = session.get(target_url, headers=headers, cookies=cookies, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 1. فحص عناصر السعر الرئيسية المباشرة لأمازون مصر
                selectors = [
                    '#corePriceDisplay_desktop_feature_div .a-offscreen',
                    '#corePrice_feature_div .a-offscreen',
                    '.apexPriceToPay .a-offscreen',
                    '#price_inside_buybox',
                    'span.a-price span.a-offscreen'
                ]
                
                for sel in selectors:
                    elements = soup.select(sel)
                    for elem in elements:
                        txt = elem.get_text().strip()
                        val = clean_price(txt)
                        if val:
                            # لو السعر بالجنيه ورقم منطقي للمنتج
                            if 'جنيه' in txt or 'EGP' in txt or val > 3000:
                                return f"{val:.2f}"
                            # لو السعر راجع بالدولار من السيرفر الأمريكي لمنتج غالي (زي اللابتوب)
                            elif val < 3000 and any(k in url.lower() for k in ['laptop', 'nitro', 'macbook', 'phone', 'iphone', 'pc']):
                                return f"{(val * USD_TO_EGP_RATE):.2f}"

                # 2. فحص بيانات الـ JSON-LD المخفية
                for script in soup.find_all('script', type='application/ld+json'):
                    if script.string:
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, list):
                                data = data[0]
                            
                            offers = data.get('offers')
                            if offers:
                                if isinstance(offers, list):
                                    offers = offers[0]
                                price = offers.get('price')
                                currency = offers.get('priceCurrency', '')
                                if price:
                                    val = clean_price(price)
                                    if val:
                                        if currency == 'EGP' or val > 3000:
                                            return f"{val:.2f}"
                                        elif currency == 'USD' or val < 3000:
                                            return f"{(val * USD_TO_EGP_RATE):.2f}"
                        except Exception:
                            continue

        except Exception as e:
            print(f"Amazon Scrape Attempt {attempt+1} Error: {e}")

    return "N/A"

def scrape_noon_special(url):
    """جلب سعر منتج نون بأسلوب استخراج متقدم لتجاوز الحظر"""
    clean_url = url.split('?')[0]
    
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    cookies = {
        "locale": "ar-eg",
        "country": "eg"
    }

    for attempt in range(3):
        try:
            time.sleep(random.uniform(1.0, 2.5))
            session = curl_requests.Session(impersonate="chrome120")
            response = session.get(clean_url, headers=headers, cookies=cookies, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 1. البحث الشامل داخل سكريبت __NEXT_DATA__ بمختلف مفاتيح الأسعار
                next_data = soup.find('script', id='__NEXT_DATA__')
                if next_data and next_data.string:
                    patterns = [
                        r'"offer_price"\s*:\s*([\d\.]+)',
                        r'"sale_price"\s*:\s*([\d\.]+)',
                        r'"price"\s*:\s*([\d\.]+)',
                        r'"price_egp"\s*:\s*([\d\.]+)'
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, next_data.string)
                        for p in matches:
                            val = clean_price(p)
                            if val and val > 0:
                                return f"{val:.2f}"

                # 2. البحث داخل عناصر الـ HTML المباشرة
                selectors = [
                    '[data-qa="product-price"]',
                    '.priceNow',
                    '.p-price',
                    'span.price',
                    '.priceContainer .amount',
                    '[class*="price"]'
                ]
                for sel in selectors:
                    elements = soup.select(sel)
                    for elem in elements:
                        val = clean_price(elem.get_text())
                        if val and val > 0:
                            return f"{val:.2f}"

        except Exception as e:
            print(f"Noon Scrape Attempt {attempt+1} Error: {e}")

    return "N/A"

def get_product_price(url):
    """الدالة الرئيسية لجلب السعر بحسب المتجر"""
    if not url or not isinstance(url, str):
        return "N/A"
    
    u = url.lower()
    if 'noon' in u:
        return scrape_noon_special(url)
    elif 'amazon' in u:
        return scrape_amazon(url)
    return "N/A"
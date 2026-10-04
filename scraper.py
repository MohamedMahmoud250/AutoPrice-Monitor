import re
import json
import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

# ==========================================
# 1. دالة تنظيف وتنسيق الأسعار
# ==========================================
def clean_price(price_str):
    if price_str is None or price_str == "":
        return "N/A"
    cleaned = re.sub(r'[^\d.]', '', str(price_str).replace(',', ''))
    try:
        val = float(cleaned)
        return f"{val:.2f}" if val > 0 else "N/A"
    except (ValueError, TypeError):
        return "N/A"

# ==========================================
# 2. كود خاص ومستقل لموقع نون فقط (Noon Engine)
# ==========================================
def scrape_noon_special(url):
    """مخصص لسحب منتجات نون وتجاوز نظام الحظر"""
    try:
        # استخدام curl_cffi لمحاكاة متصفح Chrome حقيقي مع إرسال البصمة الكاملة
        session = curl_requests.Session(impersonate="chrome120")
        
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

        response = session.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # طريقة 1: الاستخراج من بيانات JSON داخل __NEXT_DATA__
            next_data = soup.find('script', id='__NEXT_DATA__')
            if next_data and next_data.string:
                try:
                    data = json.loads(next_data.string)
                    # البحث عن مفاتيح الأسعار المباشرة داخل الهيكل
                    price_matches = re.findall(r'"price"\s*:\s*([\d\.]+)|"sale_price"\s*:\s*([\d\.]+)', next_data.string)
                    for match in price_matches:
                        for p in match:
                            if p:
                                price_clean = clean_price(p)
                                if price_clean != "N/A":
                                    return price_clean
                except Exception:
                    pass

            # طريقة 2: الاستخراج المباشر عبر الـ HTML العناصر
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

            # طريقة 3: البحث بـ Regex داخل النص الكامل للـ HTML
            all_prices = re.findall(r'"price"\s*:\s*([\d\.]+)|"sale_price"\s*:\s*([\d\.]+)', html)
            for p_tuple in all_prices:
                for p in p_tuple:
                    if p:
                        price_clean = clean_price(p)
                        if price_clean != "N/A":
                            return price_clean

    except Exception as e:
        print(f"Noon Custom Scraper Error: {e}")

    return "N/A"

# ==========================================
# 3. كود أمازون والمواقف الأخرى (كما هو)
# ==========================================
def scrape_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8"
    }
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            selectors = ['.a-price .a-offscreen', '#priceblock_ourprice', '#priceblock_dealprice', 'span.a-price-whole']
            for sel in selectors:
                elem = soup.select_one(sel)
                if elem:
                    p = clean_price(elem.get_text())
                    if p != "N/A":
                        return p
    except Exception as e:
        print(f"Amazon Scrape Error: {e}")
    return "N/A"

def scrape_jumia(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
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

# ==========================================
# 4. الدالة الرئيسية لتوجيه كل رابط لمُحركه
# ==========================================
def get_product_price(url):
    if not url or not isinstance(url, str):
        return "N/A"
    
    u = url.lower()
    
    # توجيه نون للمُحرك المخصص الجديد
    if 'noon' in u:
        return scrape_noon_special(url)
    elif 'amazon' in u:
        return scrape_amazon(url)
    elif 'jumia' in u:
        return scrape_jumia(url)
    else:
        # أي موقع آخر
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
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
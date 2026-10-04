import schedule
import time
from datetime import datetime

from database.database import SessionLocal
from database.models import Product, PriceHistory
from scraper import get_product_price

def job_update_all_prices():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{current_time}] Starting automated price update...")
    
    db = SessionLocal()
    products = db.query(Product).all()
    updated_count = 0
    
    for p in products:
        try:
            new_price = get_product_price(p.url, p.store_name)
            if new_price:
                p.current_price = new_price
                history = PriceHistory(product_id=p.id, price=new_price)
                db.add(history)
                updated_count += 1
                print(f"[SUCCESS] Updated {p.name} | New Price: {new_price} EGP")
            else:
                print(f"[FAILED] Could not fetch price for {p.name}")
        except Exception as e:
            print(f"[ERROR] Failed to update {p.name}: {e}")
            
    db.commit()
    db.close()
    
    finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{finish_time}] Update completed! Total updated: {updated_count}\n")

schedule.every().day.at("00:00").do(job_update_all_prices)

print("🚀 Auto-updater is now running in the background...")
print("Prices will be checked daily at 00:00.")
print("Press Ctrl+C to stop the script.")

while True:
    schedule.run_pending()
    time.sleep(1) 
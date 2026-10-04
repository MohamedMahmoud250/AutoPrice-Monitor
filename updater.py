import time
import pandas as pd
from datetime import datetime
import os
from scraper import get_product_price

PRODUCTS_FILE = "products.csv"
HISTORY_FILE = "price_history.csv"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return pd.DataFrame(columns=["id", "username", "product_name", "store", "price", "url"])
    df = pd.read_csv(PRODUCTS_FILE, keep_default_na=False)
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    if 'current_price' in df.columns and 'price' not in df.columns:
        df = df.rename(columns={'current_price': 'price'})
    return df

def save_products(df):
    df.to_csv(PRODUCTS_FILE, index=False)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=["product_id", "date", "price"])
    return pd.read_csv(HISTORY_FILE, keep_default_na=False)

def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)

def run_background_updater():
    print("🚀 Background price updater service started...")
    while True:
        try:
            print(f"[{datetime.now()}] Checking product prices...")
            prods_df = load_products()
            
            if not prods_df.empty:
                hist_df = load_history()
                for idx, row in prods_df.iterrows():
                    new_price = get_product_price(row['url'])
                    
                    if new_price and str(new_price).lower() not in ["n/a", "none", "nan"]:
                        try:
                            new_hist = pd.DataFrame([{
                                "product_id": row['id'],
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "price": float(new_price)
                            }])
                            hist_df = pd.concat([hist_df, new_hist], ignore_index=True)
                        except:
                            pass
                        price_str = f"EGP {new_price}"
                    else:
                        price_str = "N/A"
                        
                    prods_df.loc[prods_df['id'] == row['id'], 'price'] = price_str
                
                save_products(prods_df)
                save_history(hist_df)
                print(f"[{datetime.now()}] Prices updated successfully.")
            else:
                print("No products found to update.")
                
        except Exception as e:
            print(f"Error in background updater: {e}")
            
        time.sleep(3600)

if __name__ == "__main__":
    run_background_updater()
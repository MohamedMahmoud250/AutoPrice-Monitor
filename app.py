import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app_title = os.getenv("APP_NAME", "AutoPrice Monitor")

from scraper import get_product_price

st.set_page_config(page_title="AutoPrice Monitor", page_icon="📈", layout="wide")

# --- Custom CSS with Light Green Theme, Continuous Cart Animation & Smooth Moving Border ---
st.markdown("""
    <style>
    /* 1. Page Background */
    .stApp {
        background: #0e1117;
    }

    /* 2. Keyframe Animations */
    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(25px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes cardGlow {
        0%, 100% {
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 18px rgba(52, 211, 153, 0.2);
        }
        50% {
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), 0 0 28px rgba(52, 211, 153, 0.35);
        }
    }

    /* Continuous E-Commerce Cart Icon Animation */
    @keyframes cartBounce {
        0%, 100% {
            transform: translateY(0) scale(1);
        }
        50% {
            transform: translateY(-7px) scale(1.08);
        }
    }

    .animated-cart {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
        margin-right: 10px;
        animation: cartBounce 2s infinite ease-in-out;
    }

    /* Continuous Smooth Gradient Moving Border for Add New Product */
    @keyframes animatedGlowBorder {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .animated-header-box {
        position: relative;
        padding: 12px 18px;
        border-radius: 12px;
        background: linear-gradient(#161922, #161922) padding-box,
                    linear-gradient(135deg, #34d399, #06b6d4, #818cf8, #34d399) border-box;
        border: 2px solid transparent;
        background-size: 300% 300%;
        animation: animatedGlowBorder 5s ease infinite;
        display: flex;
        align-items: center;
        margin-bottom: 18px;
    }

    .animated-header-box h3 {
        margin: 0;
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
    }

    /* 3. Login Container Card Animation */
    div[data-testid="stForm"] {
        background: #161922;
        padding: 32px;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        animation: fadeInUp 0.7s ease-out forwards, cardGlow 4s infinite ease-in-out;
    }

    /* 4. Gradient Header Title */
    .login-header h2 {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #ffffff 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 30px;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    
    .login-header p {
        color: #9ca3af;
        font-size: 14px;
    }

    /* 5. Input Fields Styling & Focus Effects */
    .stTextInput>div>div>input {
        border-radius: 10px;
        background-color: #0f1117 !important;
        border: 1px solid #2a2e3d !important;
        color: #ffffff !important;
        transition: all 0.3s ease-in-out;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #34d399 !important;
        box-shadow: 0 0 12px rgba(52, 211, 153, 0.35) !important;
        transform: scale(1.01);
    }

    /* 6. Primary Light Mint Green Action Buttons */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 15px;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
        color: #061e14 !important;
        border: none !important;
        padding: 10px 0;
    }
    
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 8px 22px rgba(52, 211, 153, 0.45) !important;
        background: linear-gradient(135deg, #6ee7b7 0%, #34d399 100%) !important;
        color: #061e14 !important;
    }

    .stButton>button:active, div[data-testid="stFormSubmitButton"]>button:active {
        transform: translateY(-1px);
    }

    /* 7. Metrics & Dashboard Cards */
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        color: #34d399;
        font-weight: 800;
    }
    
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background-color: rgba(255, 255, 255, 0.02);
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

USERS_FILE = "users.csv"
PRODUCTS_FILE = "products.csv"
HISTORY_FILE = "price_history.csv"

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_db():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username", "password"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(PRODUCTS_FILE):
        pd.DataFrame(columns=["id", "username", "product_name", "store", "price", "url"]).to_csv(PRODUCTS_FILE, index=False)
    if not os.path.exists(HISTORY_FILE):
        pd.DataFrame(columns=["product_id", "date", "price"]).to_csv(HISTORY_FILE, index=False)

init_db()

def load_users():
    return pd.read_csv(USERS_FILE, keep_default_na=False)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def clean_price_value(price_val):
    """Clean and format price values to prevent 'nan' display"""
    if pd.isna(price_val) or price_val is None:
        return "N/A"
    
    val_str = str(price_val).strip()
    if val_str.lower() in ['nan', 'none', 'n/a', '', 'null']:
        return "N/A"
        
    return val_str

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return pd.DataFrame(columns=["id", "username", "product_name", "store", "price", "url"])
    
    df = pd.read_csv(PRODUCTS_FILE, keep_default_na=False)
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    rename_dict = {'current_price': 'price'}
    df = df.rename(columns=rename_dict)
    
    required_cols = ["id", "username", "product_name", "store", "price", "url"]
    for col in required_cols:
        if col not in df.columns:
            if col == "username":
                df[col] = st.session_state.get('username', 'default_user')
            else:
                df[col] = "N/A"
                
    df['price'] = df['price'].apply(clean_price_value)
    
    return df[required_cols]

def save_products(df):
    df['price'] = df['price'].apply(clean_price_value)
    df.to_csv(PRODUCTS_FILE, index=False)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=["product_id", "date", "price"])
    return pd.read_csv(HISTORY_FILE, keep_default_na=False)

def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)

def get_store_info(url):
    u = str(url).lower()
    if 'amazon' in u: return 'Amazon', '🟧 Amazon'
    if 'noon' in u: return 'Noon', '🟨 Noon'
    if 'jumia' in u: return 'Jumia', '🟧 Jumia'
    return 'Other', '🛍️️ Other'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# --- Modern Animated Login Interface ---
if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    
    with col_l2:
        st.markdown("""
            <div class="login-header">
                <h2>
                    <span class="animated-cart">
                        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="9" cy="21" r="1"></circle>
                            <circle cx="20" cy="21" r="1"></circle>
                            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                        </svg>
                    </span>
                    AutoPrice Monitor
                </h2>
                <p>Welcome back! Sign in to monitor your prices</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])
        
        with tab1:
            with st.form("login_form"):
                login_user = st.text_input("Username", key="login_u")
                login_pass = st.text_input("Password", type="password", key="login_p")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit_login:
                    users_df = load_users()
                    hashed_p = hash_password(login_pass)
                    user_exists = users_df[(users_df['username'] == login_user) & (users_df['password'] == hashed_p)]
                    if not user_exists.empty:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = login_user
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab2:
            with st.form("register_form"):
                reg_user = st.text_input("Choose Username", key="reg_u")
                reg_pass = st.text_input("Choose Password", type="password", key="reg_p")
                reg_confirm = st.text_input("Confirm Password", type="password", key="reg_cp")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_reg = st.form_submit_button("Register Account", use_container_width=True)
                
                if submit_reg:
                    if reg_user and reg_pass:
                        if reg_pass != reg_confirm:
                            st.error("Passwords do not match!")
                        else:
                            users_df = load_users()
                            if reg_user in users_df['username'].values:
                                st.error("Username already exists.")
                            else:
                                new_user = pd.DataFrame([{"username": reg_user, "password": hash_password(reg_pass)}])
                                users_df = pd.concat([users_df, new_user], ignore_index=True)
                                save_users(users_df)
                                st.success("Account created successfully! You can login now.")
                    else:
                        st.error("Please fill in all required fields.")

else:
    st.sidebar.title(f"Welcome, {st.session_state['username']} 👋")
    
    with st.sidebar.expander("🔑 Change Password"):
        old_p = st.text_input("Current Password", type="password")
        new_p = st.text_input("New Password", type="password")
        if st.button("Save Password"):
            users_df = load_users()
            curr_u = st.session_state['username']
            if hash_password(old_p) == users_df.loc[users_df['username'] == curr_u, 'password'].values[0]:
                users_df.loc[users_df['username'] == curr_u, 'password'] = hash_password(new_p)
                save_users(users_df)
                st.success("Password changed successfully!")
            else:
                st.error("Current password is incorrect.")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()

    # Main Dashboard Animated Title
    st.markdown(f"""
        <h1 style="display: flex; align-items: center; font-weight: 800; color: #ffffff; font-size: 36px; margin-bottom: 20px;">
            <span class="animated-cart">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="9" cy="21" r="1"></circle>
                    <circle cx="20" cy="21" r="1"></circle>
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                </svg>
            </span>
            {app_title}
        </h1>
    """, unsafe_allow_html=True)

    prods_df = load_products()
    user_prods = prods_df[prods_df['username'] == st.session_state['username']].copy()
    m1, m2, m3 = st.columns(3)
    m1.metric("Tracked Products", len(user_prods))
    
    valid_prices = []
    for p in user_prods['price']:
        p_clean = clean_price_value(p)
        if p_clean != 'N/A' and 'EGP' in p_clean:
            try: valid_prices.append(float(p_clean.replace('EGP', '').strip()))
            except: pass
            
    lowest_val = f"EGP {min(valid_prices):,.2f}" if valid_prices else "N/A"
    m2.metric("Lowest Recorded Price", lowest_val)
    m3.metric("Auto-Update Status", "Active (Background Worker) 🟢")

    st.markdown("---")

    col1, col2 = st.columns([1, 1.8])

    with col1:
        with st.container(border=True):
            # Animated Moving Border Header Box
            st.markdown("""
                <div class="animated-header-box">
                    <h3>➕ Add New Product</h3>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("add_product_form", clear_on_submit=True):
                prod_name = st.text_input("Product Name")
                prod_url = st.text_input("Product URL")
                submit_btn = st.form_submit_button("Save Product", use_container_width=True)
                
                if submit_btn:
                    if prod_name and prod_url:
                        with st.spinner("Fetching price from store..."):
                            price = get_product_price(prod_url)
                            store_name, _ = get_store_info(prod_url)
                            
                            prods_df = load_products()
                            if not prods_df.empty and 'id' in prods_df.columns and pd.to_numeric(prods_df['id'], errors='coerce').notna().any():
                                new_id = int(pd.to_numeric(prods_df['id'], errors='coerce').max()) + 1
                            else:
                                new_id = 1
                            
                            if price and str(price).lower() not in ["n/a", "none", "nan"]:
                                price_str = f"EGP {price}"
                            else:
                                price_str = "N/A"

                            new_row = {
                                "id": new_id,
                                "username": st.session_state['username'],
                                "product_name": prod_name,
                                "store": store_name,
                                "price": price_str,
                                "url": prod_url
                            }
                            
                            prods_df = pd.concat([prods_df, pd.DataFrame([new_row])], ignore_index=True)
                            save_products(prods_df)
                            
                            if price_str != "N/A":
                                try:
                                    hist_df = load_history()
                                    new_hist = pd.DataFrame([{
                                        "product_id": new_id,
                                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                        "price": float(price)
                                    }])
                                    hist_df = pd.concat([hist_df, new_hist], ignore_index=True)
                                    save_history(hist_df)
                                except:
                                    pass
                                
                            st.success("Product added successfully!")
                            st.rerun()
                    else:
                        st.error("Please enter both product name and URL.")

    with col2:
        header_col, btn_col = st.columns([2, 1])
        with header_col:
            st.subheader("📦 Tracked Products")
        with btn_col:
            if st.button("🔄 Update All Prices", use_container_width=True):
                if not user_prods.empty:
                    status_text = st.empty()
                    hist_df = load_history()
                    for idx, row in user_prods.iterrows():
                        status_text.text(f"Updating: {row['product_name']}...")
                        new_price = get_product_price(row['url'])
                        
                        if new_price and str(new_price).lower() not in ["n/a", "none", "nan"]:
                            price_str = f"EGP {new_price}"
                            try:
                                new_hist = pd.DataFrame([{
                                    "product_id": row['id'],
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "price": float(new_price)
                                }])
                                hist_df = pd.concat([hist_df, new_hist], ignore_index=True)
                            except:
                                pass
                        else:
                            price_str = "N/A"
                            
                        prods_df.loc[prods_df['id'] == row['id'], 'price'] = price_str
                    
                    save_products(prods_df)
                    save_history(hist_df)
                    status_text.text("All prices updated!")
                    st.rerun()

        if not user_prods.empty:
            for idx, row in user_prods.iterrows():
                _, store_badge = get_store_info(row['url'])
                display_price = clean_price_value(row['price'])
                
                with st.container(border=True):
                    c_info, c_price, c_link, c_del = st.columns([2.5, 2, 1.2, 0.8])
                    
                    with c_info:
                        st.markdown(f"**{row['product_name']}**")
                        st.caption(f"Store: {store_badge}")
                        
                    with c_price:
                        st.markdown(f"**`{display_price}`**")
                        
                    with c_link:
                        st.link_button("🔗 Visit", row['url'], use_container_width=True)
                        
                    with c_del:
                        if st.button("🗑️", key=f"del_{row['id']}", help="Delete product"):
                            prods_df = prods_df[prods_df['id'] != row['id']]
                            save_products(prods_df)
                            st.rerun()
        else:
            st.info("No products added yet.")

    st.markdown("---")
    st.subheader("📊 Price History & Analytics")
    
    if not user_prods.empty:
        selected_prod_name = st.selectbox("Select a product to view analytics:", user_prods['product_name'].unique())
        
        prod_row = user_prods[user_prods['product_name'] == selected_prod_name].iloc[0]
        prod_id = prod_row['id']
        
        hist_df = load_history()
        prod_hist = hist_df[hist_df['product_id'] == prod_id].copy()
        
        if not prod_hist.empty and 'price' in prod_hist.columns:
            prod_hist['price'] = pd.to_numeric(prod_hist['price'], errors='coerce')
            prod_hist = prod_hist.dropna(subset=['price'])
            
            if not prod_hist.empty:
                prod_hist['date'] = pd.to_datetime(prod_hist['date'])
                
                current_p = prod_hist['price'].iloc[-1]
                min_p = prod_hist['price'].min()
                max_p = prod_hist['price'].max()
                
                first_p = prod_hist['price'].iloc[0]
                price_diff = current_p - first_p
                pct_change = (price_diff / first_p) * 100 if first_p > 0 else 0
                
                stat1, stat2, stat3, stat4 = st.columns(4)
                
                stat1.metric("Current Price", f"EGP {current_p:,.2f}", delta=f"{pct_change:+.2f}%")
                stat2.metric("Lowest Price", f"EGP {min_p:,.2f}")
                stat3.metric("Highest Price", f"EGP {max_p:,.2f}")
                
                if min_p == max_p:
                    stat4.metric("Price Status", "Stable 🔒", delta="No Fluctuations", delta_color="off")
                else:
                    fluctuation = max_p - min_p
                    stat4.metric("Total Fluctuation", f"EGP {fluctuation:,.2f}")
                
                chart_data = prod_hist.set_index('date')['price']
                st.line_chart(chart_data)
            else:
                st.info("No valid price history records for this product yet.")
        else:
            st.info("No price history recorded for this product yet.")
    else:
        st.write("Add products first to display historical charts.")
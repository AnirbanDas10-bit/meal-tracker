import streamlit as st
import mysql.connector

# ---------------------------------------------------------
# 1. DATABASE & LOGIC CLASSES
# ---------------------------------------------------------
class Meal:
    def __init__(self, meal_type, description, cost):
        self.meal_type = meal_type
        self.description = description
        self.cost = float(cost)

class DatabaseManager:
    # Added 'port' to the __init__ so it can accept the st.secrets value
    def __init__(self, host, user, password, database, port):
        self.config = {
            "host": host, 
            "user": user, 
            "password": password, 
            "database": database,
            "port": int(port), # Port must be an integer (4000)
            "ssl_verify_cert": False,
            "ssl_disabled": False
        }

    def save_meal(self, meal):
        try:
            # FIXED INDENTATION HERE
            my_db = mysql.connector.connect(**self.config)
            my_cursor = my_db.cursor()
            
            my_cursor.execute(
                "INSERT INTO meal_details (meal_type, description_) VALUES (%s, %s)",
                (meal.meal_type, meal.description)
            )
            detail_id = my_cursor.lastrowid
            
            my_cursor.execute(
                "INSERT INTO meal_expense (detail_id, cost) VALUES (%s, %s)", 
                (detail_id, meal.cost)
            )
            
            my_db.commit()
            return True, f"Success! {meal.description} added."
        except mysql.connector.Error as err:
            return False, f"Database Error: {err}"
        finally:
            if 'my_db' in locals() and my_db.is_connected():
                my_db.close()

    def clear_test_data(self):
        try:
            my_db = mysql.connector.connect(**self.config)
            my_cursor = my_db.cursor()
            my_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            my_cursor.execute("TRUNCATE TABLE meal_expense;")
            my_cursor.execute("TRUNCATE TABLE meal_details;")
            my_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            my_db.commit()
            return True, "Database Cleaned & IDs Reset!"
        except Exception as e:
            return False, str(e)
        finally:
            if 'my_db' in locals() and my_db.is_connected():
                my_db.close()

# ---------------------------------------------------------
# 2. INTERFACE INITIALIZATION
# ---------------------------------------------------------

# Initializing with all secrets from TiDB
db = DatabaseManager(
    st.secrets["db_host"],
    st.secrets["db_user"],
    st.secrets["db_password"],
    st.secrets["db_name"],
    st.secrets["db_port"]
)

st.set_page_config(
    page_title="Meal Tracker",
    page_icon="🍴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CUSTOM CSS FOR ZOMATO MOBILE STYLE
st.markdown("""
    <style>
    .stApp { background-color: #F8F8F8; }
    .mobile-header {
        background-color: #E23744;
        padding: 25px;
        border-radius: 0px 0px 25px 25px;
        margin: -60px -20px 20px -20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .mobile-title { color: white; font-size: 24px; font-weight: 800; margin: 0; }
    [data-testid="stForm"] {
        background-color: #ffffff;
        padding: 20px !important;
        border-radius: 20px;
        border: 1px solid #E8E8E8;
    }
    .stButton>button {
        background-color: #E23744 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 50px !important;
        width: 100%;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="mobile-header">
        <p class="mobile-title">My Meal Tracker</p>
        <p style='color: #FFC0C3; font-size: 12px; margin: 0;'>Premium Dashboard by Anirban Das</p>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔐 Admin Panel")
    st.info("Authorized access only for data maintenance.")
    with st.expander("🛠️ Data Maintenance"):
        admin_id = st.text_input("Admin ID", placeholder="Enter ID")
        admin_pass = st.text_input("Admin Password", type="password", placeholder="Enter Password")
        if st.button("🚨 EXECUTE DATA WIPE"):
            if admin_id == "root" and admin_pass == "Chini29":
                success, msg = db.clear_test_data()
                if success:
                    st.success(msg)
                    st.toast("Database has been reset.", icon="🗑️")
                else:
                    st.error(msg)
            else:
                st.error("Invalid Credentials!")

with st.form("zomato_entry"):
    st.markdown("<p style='font-size: 18px; font-weight: 700; color: #1C1C1C;'>Record New Meal</p>", unsafe_allow_html=True)
    meal_type = st.selectbox("When?", ["Lunch", "Dinner", "Snacks"])
    dish_choice = st.selectbox("What?", ["Veg Dish (₹40)", "Veg-Dish-Egg (₹40)", "Veg-Dish-Fish (₹70)", "Veg-Dish-Chicken (₹80)", "Custom"])

    if dish_choice == "Custom":
        st.write("---")
        custom_name = st.text_input("Dish Name")
        custom_cost = st.number_input("Cost (₹)", min_value=0.0, step=5.0)

    submitted = st.form_submit_button("SAVE TO DATABASE")

    if submitted:
        if "Veg Dish" in dish_choice: fn, fc = "Veg Dish", 40.0
        elif "Egg" in dish_choice: fn, fc = "Veg-Dish-Egg", 40.0
        elif "Fish" in dish_choice: fn, fc = "Veg-Dish-Fish", 70.0
        elif "Chicken" in dish_choice: fn, fc = "Veg-Dish-Chicken", 80.0
        else: fn, fc = custom_name.strip().title(), custom_cost

        if not fn:
            st.error("Please provide dish details!")
        else:
            m = Meal(meal_type, fn, fc)
            ok, msg = db.save_meal(m)
            if ok:
                st.success(msg)
                st.balloons()
            else:
                st.error(msg)

st.markdown("<br><p style='text-align: center; color: #9C9C9C; font-size: 12px;'>Build v4.1 | Anirban Das (Data Analyst)</p>", unsafe_allow_html=True)

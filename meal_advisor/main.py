import json
import pandas as pd
import requests
from populate_table import get_connection
import streamlit as st
from streamlit_lottie import st_lottie
from annotated_text import annotated_text
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
# from config_files.api_keys import nutritionix_app_id, nutritionix_api_key


# CONFIG SETUP
st.set_page_config(page_title="Meal Advisor", page_icon=":cake:", layout="wide")

#---- LOAD ASSETS ----
def load_lottie_assets(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_anim1 = load_lottie_assets("https://assets8.lottiefiles.com/temp/lf20_nXwOJj.json")
lottie_anim2 = load_lottie_assets("https://assets3.lottiefiles.com/packages/lf20_3GIrwN3h0z.json")
lottie_anim_background = load_lottie_assets("https://assets5.lottiefiles.com/packages/lf20_xsrma5om.json")
img_profile1 = Image.open("meal_advisor/images/profile-photo-color-background-1.jpg")

#---- HEADER SECTION ----
with open("meal_advisor\\style\\style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)
    with st.container():
        st.title("Welcome to the meal advisor :sunglasses:")

    with st.container():
        st.header("A humble project made with Streamlit:iphone: and Python:snake:")
        st.subheader("Hope you find it useful :smile:")

    with st.container():
        left_column, center_column, right_column = st.columns(3)
        with left_column:
            st.title("Out of ideas? Try a random recipe")
            st.write(
                """Try one of our recipes"""
                )
        with center_column:
            st.title("Look for a meal that suits you")
            st.write(
                """You can filter by main ingredient, style and other"""
                )
        with right_column:
            st.title("Plan your daily meals")
            st.write(
                """The goal is to calculate your daily calories expenditure,
                calculate your macros and plan your meals ahead"""
                )

#---- PARAMETERS ----
with st.container():
    left_column, center_column, right_column= st.columns(3)
    
    with left_column:
        random_meal = st.button("Let's make a random meal")
        if random_meal:
            switch_page("random_meal")
    
    with center_column:
        filter_meal = st.button("Let's select a meal from the database")
        if random_meal:
            switch_page("filter_meal")
    
    with right_column:
        plan_meal = st.button("Let's plan my meals for the day")
        if random_meal:
            switch_page("plan_daily_meal")

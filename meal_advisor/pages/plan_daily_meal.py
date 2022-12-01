import json
import re
import pandas as pd
import numpy as np
import requests
from populate_table import get_connection
import streamlit as st
from streamlit_lottie import st_lottie
from annotated_text import annotated_text
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.no_default_selectbox import selectbox
from streamlit.delta_generator import DeltaGenerator
from PIL import Image
from typing import Optional
# from config_files.api_keys import google_user, google_api_key, nutritionix_app_id, nutritionix_api_key
from functions import get_random_meal_api, filter_mealdb_ingredients
from vct_calculator import calculate_bmr, calculate_fat_perc, calculate_macros


# CONFIG SETUP
st.set_page_config(page_title="Meal Advisor", page_icon=":cake:", layout="wide")


#---- LOAD ASSETS ----
def load_lottie_assets(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


#---- LOAD CSS ----


#---- HEADER SECTION ----
with open("meal_advisor/style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    with st.container():
        st.title("Plan your daily meals :sunglasses:")
        st.write("---")

with st.container():
    left_column, center_column, right_column = st.columns(3)
    
    with left_column:
        gender_selection = selectbox("Select gender", ["Male", "Female"])
        age_selection = st.text_input("Input age")
    
    with center_column:    
        weight_selection = st.text_input("Input weight (in kg)")
        height_selection = st.text_input("Input height (in cm)")
        activity_factor_slider = st.slider("Choose activity factor (1 to 6)", min_value=1, max_value=6, step=1)
    
    with right_column:    
        neck_selection = st.text_input("Input neck (in cm)")
        waist_selection = st.text_input("Input waist (in cm)")
        hip_selection = st.text_input("Input hip (in cm)")

    st.write("---")

with st.container():
    fp = calculate_fat_perc(gender=True, height=172, neck=40, waist=86, hip=93)
    bmr1 = calculate_bmr(gender=True, age=37, weight=70, height=171, activity_factor=4)
    bmr2 = calculate_bmr(method=1, gender=True, age=37, weight=70, height=171, activity_factor=4, fat_perc=fp)
    macros_required = calculate_macros(bmr1)

    st.write("Calculation's summary")
    st.write(fp)
    st.write(bmr1)
    st.write(bmr2)
    st.write(macros_required)
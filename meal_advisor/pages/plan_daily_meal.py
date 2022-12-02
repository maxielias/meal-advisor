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
from vct_calculator import calculate_bmr, calculate_fat_perc, calculate_macros, get_daily_meal_plan


# CONFIG SETUP
st.set_page_config(page_title="Meal Advisor", page_icon=":cake:", layout="wide")


#---- LOAD ASSETS ----
def load_lottie_assets(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


#---- LOAD DATA ----
df_recipes = pd.read_csv("meal_advisor/data/recipes_clean_healthyfitnessmeals.csv", header=0)


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
        gender_bool = 0 if gender_selection == "Male" else 1
        age_selection = st.text_input("Input age")
        method_selection = selectbox("Select calculation method", ["Katch-McArdle Formula", "Mifflin St Jeor Formula"])
        method_int = 0 if method_selection == 0 else 1
    
    with center_column:    
        weight_selection = st.text_input("Input weight (in kg)")
        height_selection = st.text_input("Input height (in cm)")
        activity_factor_slider = st.slider("Choose activity factor (1 to 6)", min_value=1, max_value=6, step=1)
    
    with right_column:    
        neck_selection = st.text_input("Input neck (in cm)")
        waist_selection = st.text_input("Input waist (in cm)")
        hip_selection = st.text_input("Input hip (in cm)")

    try:
        age_input = float(age_selection)
        weight_input = float(weight_selection)
        height_input = float(height_selection)
        neck_input = float(neck_selection)
        waist_input = float(waist_selection)
        hip_input = float(hip_selection)

    except:
        pass

    calculate_button = st.button("Calculate calories")
    if calculate_button:
        st.write("---")
        with st.container():
            fp = calculate_fat_perc(gender=gender_bool, height=height_input, neck=neck_input, waist=waist_input, hip=hip_input)
            bmr = calculate_bmr(method=method_int, gender=gender_bool, age=age_input, weight=weight_input, height=height_input, activity_factor=activity_factor_slider, fat_perc=fp)
            macros_required = calculate_macros(bmr)

            carbs_gr = macros_required["carbs"][0]
            proteins_gr = macros_required["proteins"][0]
            fat_gr = macros_required["fat"][0]

            st.write("Calculation's summary")

            st.write(f"Daily calories intake to maintain weight should be {bmr}")
        
            st.write(f"Recommended carbs intake is {carbs_gr} gr daily")
            st.write(f"Recommended proteins intake is {proteins_gr} gr daily")
            st.write(f"Recommended fat intake is {fat_gr} gr daily")

            # recipes_suggestion = df_recipes["title"][df_recipes["calories"]<=carbs_gr]
            df_meal_plan = get_daily_meal_plan(df=df_recipes, filter_col="category", filters=["main-courses", ["breakfast", "desserts", "snacks"]], qty=2, tot_cal=bmr, sum_col="calories")

            st.write(df_meal_plan)
            st.write(df_meal_plan["calories"].sum())


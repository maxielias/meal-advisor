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
import pyautogui


#---- CONFIG SETUP ----
st.set_page_config(page_title="Meal Advisor", page_icon=":cake:", layout="wide")


#---- LOAD ASSETS ----
def load_lottie_assets(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


#---- LOAD DATA ----
with open("meal_advisor/data/recipes_raw_mealdb.json") as jsonfile:
    mealdb_json = json.loads(jsonfile.read())

with open("meal_advisor/data/list_of_ingredients.txt", encoding="utf-8") as f:
    list_of_ingredients = list()
    for line in f.readlines():
        list_of_ingredients.append(line.rstrip().capitalize())


#---- PARAMETERS ----
placeholder = st.empty()

#---- HEADER SECTION ----
st.title("Let's search for a recipe, Mr. Meal Advisor :sunglasses:")


#---- CONTAINER 1 ----
with st.container():
    with open("meal_advisor/style/dataframe.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        st.header("Filter meals by main ingredient, category and area")
        
        ingredient_list = list_of_ingredients
        filter_recipe_by_ingredient = selectbox("Select main ingredient", list_of_ingredients)

        if filter_recipe_by_ingredient:
            meal_options = filter_mealdb_ingredients(data_json=mealdb_json, ingredient=filter_recipe_by_ingredient)
            meal_options_df = pd.DataFrame(meal_options)

            list_of_categories = list(set([c for c in meal_options_df["strCategory"]]))
            filter_recipe_by_category = selectbox("Select category", list_of_categories)

            list_of_areas = list(set([c for c in meal_options_df["strArea"]]))
            filter_recipe_by_area = selectbox("Select country", list_of_areas)

            if filter_recipe_by_category and filter_recipe_by_area:
                meal_options_df = meal_options_df[(meal_options_df["strCategory"]==filter_recipe_by_category) & (meal_options_df["strArea"]==filter_recipe_by_area)]

            elif filter_recipe_by_category:
                meal_options_df = meal_options_df[(meal_options_df["strCategory"]==filter_recipe_by_category)]

            elif filter_recipe_by_category:
                meal_options_df = meal_options_df[(meal_options_df["strArea"]==filter_recipe_by_area)]
        
            filtered_recipes = selectbox("Select meal", [m for m in meal_options_df["strMeal"]])

        reset_button = st.button("Reset options")
        if reset_button:
            pyautogui.hotkey("ctrl","F5")


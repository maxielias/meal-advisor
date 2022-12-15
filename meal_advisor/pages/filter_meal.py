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

#---- HEADER SECTION ----
with open("meal_advisor/style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.title("Let's search for a recipe, Mr. Meal Advisor :sunglasses:")

    with st.container():
        with open("meal_advisor/style/dataframe.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            st.header("Filter meals by main ingredient, category and area")

            reset_button = st.button("Reset options") #, on_click=st.experimental_rerun())

            if reset_button:
                st.experimental_rerun()
            
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
                
                if filtered_recipes:
                    meal_data = [m for m in mealdb_json if m["strMeal"]==filtered_recipes][0]

            show_recipe_button = st.button("Show chosen recipe")

            if show_recipe_button:
                try:
                    meal_img = meal_data["strMealThumb"]
                    left_column, center_column, right_column  = st.columns(3)
                    with left_column:
                        #meal_title = st.session_state["random_meal_json"]["strMeal"]
                        #meal_img = st.session_state["random_meal_json"]["strMealThumb"]

                        html_str = f"""
                        <style>
                        p.a {{
                        font: bold 30px Courier;
                        }}
                        </style>
                        <p class="a">{filtered_recipes}</p>
                        """
                        st.markdown(html_str, unsafe_allow_html=True)

                        with open("meal_advisor/style/border_style_1.css") as f:
                            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)   
                            st.image(meal_img) #, use_column_width=True)
                    
                    with center_column:
                        recipe_ingredient_keys = [k for k in meal_data.keys() if k.startswith("strIngredient")]
                        recipe_amount_keys = [k for k in meal_data.keys() if k.startswith("strMeasure")]
                        ingredient_dict = {"Amount": [meal_data[mk] for mk in recipe_amount_keys], # if (not st.session_state["random_meal_json"][mk]=="")], # or (not st.session_state["random_meal_json"][mk]=="NA")],
                                    "Ingredients": [meal_data[ik] for ik in recipe_ingredient_keys]} # if (not st.session_state["random_meal_json"][ik]=="")]} # or (not st.session_state["random_meal_json"][ik]=="NA")]}
                        ingredient_df = pd.DataFrame(ingredient_dict)
                        ing_df_no_idx = ingredient_df.style.hide_index()

                        with open("meal_advisor/style/dataframe.css") as f:
                            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                            # st.table(ingredient_df.loc[~(ingredient_df["Ingredients"]=="")].style.hide_index())
                            st.write(ingredient_df.loc[~(ingredient_df["Ingredients"]=="")].style.hide_index().to_html(), unsafe_allow_html=True)

                    with right_column:
                        with open("meal_advisor/style/center_vertical_horizontal.css") as f:
                            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                            st.write(meal_data["strInstructions"])

                except Exception as e:
                    st.write(e)
                    st.warning("You need to select at least one ingredient and a recipe")
                    
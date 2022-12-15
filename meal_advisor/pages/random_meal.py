import json
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
# from config_files.api_keys import nutritionix_app_id, nutritionix_api_key
from functions import get_random_meal_api


st.set_page_config(page_title="Meal Advisor", page_icon=":cake:", layout="wide")
# st.session_state

def load_lottie_assets(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


with open("meal_advisor/style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True) 
    st.title("Inspire me, Mr. Meal Advisor :sunglasses:")

    with st.container():
        left_column, right_column = st.columns(2)
        
        with right_column:
            with open("meal_advisor/style/center_vertical_horizontal.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                st.header("OK, maybe not that random")
                random_meal = st.button("Filter meal")
                if random_meal:
                    switch_page("filter_meal")

        with left_column:
            if "random_meal_json" not in st.session_state:
                random_meal_json = get_random_meal_api()
                st.session_state["random_meal_json"] = random_meal_json
            else:
                pass
            
            with open("meal_advisor/style/center_vertical_horizontal.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                st.header("Here's some inspiration for your next meal or try again:arrow_down:")

            confirm_new_random_meal = st.button("Try new random meal")
            if confirm_new_random_meal:
                random_meal_json = get_random_meal_api()
                st.session_state["random_meal_json"] = random_meal_json
            
        left_column, right_column  = st.columns(2)
        with left_column:
            meal_title = st.session_state["random_meal_json"]["strMeal"]
            meal_img = st.session_state["random_meal_json"]["strMealThumb"]

            html_str = f"""
            <style>
            p.a {{
            font: bold 30px Courier;
            }}
            </style>
            <p class="a">{meal_title}</p>
            """
            st.markdown(html_str, unsafe_allow_html=True)

            with open("meal_advisor/style/border_style_1.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)   
                st.image(meal_img) #, use_column_width=True)

        with right_column:  
            recipe_ingredient_keys = [k for k in st.session_state["random_meal_json"].keys() if k.startswith("strIngredient")]
            recipe_amount_keys = [k for k in st.session_state["random_meal_json"].keys() if k.startswith("strMeasure")]
            ingredient_dict = {"Amount": [st.session_state["random_meal_json"][mk] for mk in recipe_amount_keys], # if (not st.session_state["random_meal_json"][mk]=="")], # or (not st.session_state["random_meal_json"][mk]=="NA")],
                        "Ingredients": [st.session_state["random_meal_json"][ik] for ik in recipe_ingredient_keys]} # if (not st.session_state["random_meal_json"][ik]=="")]} # or (not st.session_state["random_meal_json"][ik]=="NA")]}
            ingredient_df = pd.DataFrame(ingredient_dict)
            ing_df_no_idx = ingredient_df.style.hide_index()
            
            with open("meal_advisor/style/dataframe.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                # st.table(ingredient_df.loc[~(ingredient_df["Ingredients"]=="")].style.hide_index())
                st.write(ingredient_df.loc[~(ingredient_df["Ingredients"]=="")].style.hide_index().to_html(), unsafe_allow_html=True)
        
    with st.container():
        with open("meal_advisor/style/center_vertical_horizontal.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            st.write(st.session_state["random_meal_json"]["strInstructions"])

import json
import re
import pandas as pd
import numpy as np
import requests
# from config_files.api_keys import google_user, google_api_key, nutritionix_app_id, nutritionix_api_key


def get_mealdb_categories():
    page = "https://www.themealdb.com/api/json/v1/1/list.php?c=list"
    response = requests.get(page)
    resp = response.json()
    category_list = [cat["strCategory"] for cat in resp["meals"]]

    return category_list


def get_mealdb_areas_api():
    page = "https://www.themealdb.com/api/json/v1/1/list.php?a=list"
    response = requests.get(page)
    resp = response.json()
    area_list = [cat["strArea"] for cat in resp["meals"]]

    return area_list


def get_mealdb_ingredients_api():
    page = "https://www.themealdb.com/api/json/v1/1/list.php?i=list"
    response = requests.get(page)
    resp = response.json()
    ingredient_list = [cat["strIngredient"] for cat in resp["meals"]]

    return ingredient_list


def get_random_meal_api():
    page = "https://www.themealdb.com/api/json/v1/1/random.php"
    response = requests.get(page)
    resp = response.json()
    random_meal_json = resp["meals"][0]

    return random_meal_json


def select_meal_api(ingredient_option:str, category_option:str=None, area_option:str=None):
    page = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient_option}"
    response = requests.get(page)
    resp = response.json()
    meal_id_list = [id["idMeal"] for id in resp["meals"]]

    coincidence_list = list()
    if category_option or area_option:
        for id in meal_id_list:
            page = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}"
            response = requests.get(page)
            resp = response.json()
            meal_category = resp["meals"][0]["strCategory"]
            meal_area = resp["meals"][0]["strArea"]
            if category_option in meal_category and area_option in meal_area:
                coincidence_list.append(resp["meals"][0]) 

    return coincidence_list


def get_mealdb_categories(data_json):
    category_list = list(set([cat["strCategory"] for cat in data_json]))

    return category_list


def get_mealdb_areas(data_json):
    area_list = list(set([cat["strArea"] for cat in data_json]))

    return area_list


def filter_mealdb_ingredients(data_json, ingredient:str):
    filter = [d for i in range(len(data_json)) for d in data_json[i].items() if d[0].startswith("strIngredient") and str(d[1]).lower().strip()==ingredient.lower().strip()]
    data_filtered_by_ingredient = [d for d in data_json for i in filter if d[i[0]]==i[1]]

    return data_filtered_by_ingredient

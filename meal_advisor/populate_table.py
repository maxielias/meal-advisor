import psycopg2
import psycopg2.extras
import psycopg2.extensions
from sqlalchemy import create_engine
import pandas as pd
import json
import os


def get_connection(db:str, user:str, password:str, localhost:str, port:str):

    try:
        # conn = psycopg2.connect(f"dbname='{db}' user='{user}' password='{password}' host='{localhost}' port='{port}'")
        engine = create_engine("postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(user, password, localhost, port, db))

        return engine

    except Exception as e:
        print("Connection error")
        print(e)


def df_to_sql(df, engine, table_name):
    
    sql_table = df.to_sql(table_name, engine)
    engine.close()

    return sql_table


if __name__== '__main__':

    db = "meal_advisor"
    user = "postgres"
    password = "postgres"
    localhost = "localhost"
    port = "5432"
    table_name = "full_format_recipes"
    path_list = [("meal_advisor/archive/full_format_recipes.json", "full_format_recicpes"), ("meal_advisor/archive/epi_r.csv", "epi_r")]

    path = "meal_advisor/data/recipes.csv"
    '''df = pd.read_csv(path)
    print(df.columns)'''
    
    with open(path, "r", encoding="utf-8") as file:
        recipes_raw = file.readlines()
        # recipes = json.load(recipes_raw[1:2])

        print(recipes_raw[1])

    #df = pd.DataFrame(data=[], columns=[recipes_raw[0]])

    '''for r in recipes_raw[1:2]:
        print(json.loads(r))'''
    '''url = r["url"]
        category = r["category"]
        recipe = r["recipe"]
        print(recipe.keys())'''
    
    '''for p, n in path_list:
        print(p)
        print(n)
        if p.endswith(".csv"):
            df = pd.read_csv(p)

        elif p.endswith(".json"):
            df = pd.read_json(p)

        try:
            engine = get_connection(db=db, user=user, password=password, localhost=localhost, port=port)
            sql_table = df_to_sql(df, engine, n)

        except Exception as e:
            print(e)
            pass'''

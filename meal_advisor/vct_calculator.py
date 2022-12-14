import pandas as pd
import numpy as np
from math import log10
from random import seed
from random import randrange, randint
from scipy.optimize import minimize


params = {
    "activityFactor": {
     0: (1.2, "Sedentary", "Sedentary lifestyle (little or no exercise)"),
     1:(1.4, "Slightly active", "Slightly active lifestyle (light exercise or sports 1-2 days/week)"),
     2: (1.6, "Moderately active", "Moderately active lifestyle (moderate exercise or sports 2-3 days/week)"),
     3: (1.75, "Very active", "Very active lifestyle (hard exercise or sports 4-5 days/week)"),
     4: (2, "Extra active", "Extra active lifestyle (very hard exercise, physical job, or sports 6-7 days/week)"),
     5: (2.3, "Professional athlete", "Professional athlete") 
    }
}


def calculate_bmr(gender:bool, age:float, weight:float, height:float, activity_factor:float, method:int=0, fat_perc:float=0.0):
    """
    Measures in cm and kg -- 
    Activity factor:
     0: (1.2, "Sedentary", "Sedentary lifestyle (little or no exercise)"),
     1:(1.4, "Slightly active", "Slightly active lifestyle (light exercise or sports 1-2 days/week)"),
     2: (1.6, "Moderately active", "Moderately active lifestyle (moderate exercise or sports 2-3 days/week)"),
     3: (1.75, "Very active", "Very active lifestyle (hard exercise or sports 4-5 days/week)"),
     4: (2, "Extra active", "Extra active lifestyle (very hard exercise, physical job, or sports 6-7 days/week)"),
     5: (2.3, "Professional athlete", "Professional athlete") 
    """
    if not fat_perc:
        if gender:
            lbm = 0.407 * weight + 0.267 * height - 19.2

        else:
            lbm = 0.252 * weight + 0.473 * height - 48.3

        # print(f"Estimating lean body mass without fat percentage to be {lbm}")
    
    else:
        lbm = weight * (1 - fat_perc)

        # print(f"Estimating lean body mass with fat percentage to be {lbm}")
        
    if method == 0:
        # Katch-McArdle Formula
        # lbm = weight * (100 - fat_perc) / 100
        bmr = (370 + 21.6 * lbm) * params["activityFactor"][activity_factor-1][0]

    elif method == 1:
        s = 5 if gender else -161
        # Mifflin St Jeor Formula
        bmr = (10 * weight + 6.25 * height - 5 * age + s) * params["activityFactor"][activity_factor-1][0]

    return round(bmr, 0)


def calculate_fat_perc(gender:bool, height:float, neck:float, waist:float, hip:float):
    """
    Measures in cm and kg
    """
    if gender:
        fp = ((495 / (1.0324 - 0.19077 * log10(waist - neck) + 0.15456 * log10(height))) - 450) / 100
        
        return fp
    
    else:
        fp = ((495 / (1.29579 - 0.35004 * log10(waist + hip - neck) + 0.22100 * log10(height))) - 450) / 100

        return round(fp, 3)


def calculate_macros(bmr:float):
    """
    Fixed ratio of macros
    Calculated daily
    """
    carb_perc = 0.5
    fat_perc = 0.2
    protein_perc = 0.3

    carb_intake = round(bmr * carb_perc, 0)
    fat_intake = round(bmr * fat_perc, 0)
    protein_intake = round(bmr * protein_perc, 0)

    carb_gr = round(carb_intake / 4, 0)
    fat_gr = round(fat_intake / 9)
    protein_gr = round(protein_intake / 4, 0)

    macros_required = {
        "carbs": (carb_gr, carb_intake, carb_perc),
        "proteins": (protein_gr, protein_intake, protein_perc),
        "fat": (fat_gr, fat_intake, fat_perc)
    }

    return  macros_required

def obj_func(x):

    return sum(x)


def eq_cons_1(x, tot_cal):

    return sum(x) - tot_cal


def get_daily_meal_plan(df, filter_col, optimize_col, filters, tot_cal, n):
    """
    Calculate daily plan meal with scipy optimizer
    """
    df = df.dropna(subset=[optimize_col])
    df = df.drop_duplicates(subset=["url"], keep="first").reset_index(drop=True)

    dict_bounds = {}
    bounds = []
    for i in range(sum(n)): 
        dict_bounds["bounds" + str(i)] = (df[optimize_col].min(), df[optimize_col].max())
        bounds.append(dict_bounds["bounds" + str(i)])

    print(bounds)

    constraint1 = {"type": "eq", "fun": eq_cons_1, "args": [tot_cal]}

    constraints = [constraint1]

    random_n = randint(0, 100)
    seed(random_n)

    dict_rand = {}
    list_rand = []
    for i in range(sum(n)):
        dict_rand["rand" + str(i)] = randrange(0, len(df) + 1, 1)
        list_rand.append(dict_rand["rand" + str(i)])

    print(list_rand)

    dict_x0 = {}
    list_x0 = []
    for i in range(sum(n)):
        dict_x0["x" + str(i)] = df.loc[list_rand[i]][optimize_col]
        list_x0.append(dict_x0["x" + str(i)])
    
    x0 = list_x0

    print(x0)

    result = minimize(obj_func, x0, method="SLSQP", bounds=bounds, constraints=constraints)

    result_sorted = np.sort(result.x)
    reversed_result = list(reversed(result_sorted))

    df_meal_plan = pd.DataFrame([], columns=df.columns)

    for i, f in enumerate(filters):
        for _ in range(n[i]):
            df_filtered = df[df[filter_col].isin(f)]
            df_filtered["diff"] = abs([rs for rs in reversed_result][0] - df_filtered[optimize_col])
            df_meal_plan = pd.concat([df_meal_plan, df_filtered[df_filtered["diff"]==df_filtered["diff"].min()]])
            reversed_result.pop(0)

    return df_meal_plan


'''if __name__== '__main__':

    fp = calculate_fat_perc(gender=True, height=172, neck=40, waist=86, hip=93)
    bmr1 = calculate_bmr(gender=True, age=37, weight=70, height=171, activity_factor=4)
    bmr2 = calculate_bmr(method=1, gender=True, age=37, weight=70, height=171, activity_factor=4, fat_perc=fp)
    macros_required = calculate_macros(bmr1)

    print(fp)
    print(bmr1)
    print(bmr2)
    print(
        f'Daily intakes of carbs={macros_required["carbs"][0]} (in gr)\n'
        f'Daily intakes of proteins={macros_required["proteins"][0]} (in gr)\n'
        f'Daily intakes of fat={macros_required["fat"][0]} (in gr)\n'
    )'''

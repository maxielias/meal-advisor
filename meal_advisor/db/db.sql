CREATE TABLE [IF NOT EXISTS] full_format_recipes(
    id SERIAL PRIMARY KEY,
    directions TEXT [], 
    fat INT NOT NULL, 
    date_string VARCHAR, 
    categories TEXT [],
    calories INT NOT NULL, 
    descrip VARCHAR, 
    protein INT NOT NULL, 
    rating FLOAT, 
    title VARCHAR,
    ingredients TEXT [], 
    sodium INT
    );

INSERT INTO full_format_recipes(
    directions, 
    fat, 
    date_string, 
    categories, 
    calories, 
    descrip, 
    protein,
    rating,
    title,
    ingredients,
    sodium
)
SELECT * FROM json_populate_record(NULL::full_format_recipes, ) 
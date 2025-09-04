# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App title
st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom smoothie")

# Name input
name_on_order = st.text_input("Name on Smoothie", "Life of Brian")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()

# Use fruit names as choices in multiselect
Ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", pd_df["FRUIT_NAME"].tolist(), max_selections=5
)

if Ingredients_list:
    Ingredients_string = ""

    for fruit_chosen in Ingredients_list:
        Ingredients_string += fruit_chosen + " "

        # Lookup search key from pandas dataframe
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

        # Show nutrition info
        st.subheader(fruit_chosen + " Nutrition Information")
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Insert order into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, NAME_ON_ORDER)
        VALUES ('{Ingredients_string.strip()}', '{name_on_order}')
    """

    st.write(my_insert_stmt)
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

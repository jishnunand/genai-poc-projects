import streamlit as st

from langchain_helper import generate_restaurent_name_name_items

st.title("Restaurant Name Generate")
cuisine = st.sidebar.selectbox("Pick a cuisine ", ("American", "Indian", "Arabic", "Mexicun"))

if cuisine:
    response = generate_restaurent_name_name_items(cuisine=cuisine)
    st.header(response['restaurant_name'].strip())
    st.write("**Menu Items**")
    menu_items = response['menu_items'].strip().split(',')
    
    for each_menu in menu_items:
        st.write("- ", each_menu.strip())
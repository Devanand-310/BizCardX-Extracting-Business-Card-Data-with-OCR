import easyocr
import streamlit as st
from function import (
    primary_details,
    company_details,
    address,
    create_table,
    insert_data_with_image
)
from PIL import Image
import cv2
import numpy as np
from mysql_connection import my_Sql

reader = easyocr.Reader(['en'])

data_1 = {"company_name" : [],
                "card_holder" : [],
                "designation" : [],
                "mobile_number" :[],
                "email" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pin_code" : [],
               }


st.set_page_config(layout="wide")
st.markdown(
    """
    <h1 style='text-align: left; color: green;'>
        BizCardX: Extracting Business Card Data with OCR
    </h1>
    """,
    unsafe_allow_html=True
)
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
    # Check if the uploaded file is a PNG
        if uploaded_file.type == "image/png":
            st.success("The uploaded file is a PNG image.")
        # You can also display the image if it's a PNG
            st.image(uploaded_file, caption="Uploaded PNG image.", use_column_width=True)
        else:
            st.error("The uploaded file is not a PNG image.")

with col2:
    st.title('Retrieve Data with Easyocr')
    if st.button('Retrieve Data'):
        if not uploaded_file:
            st.error('uploaded file cannot be empty')
        else:
            
            image = Image.open(uploaded_file)
            image_np = np.array(image)

            if len(image_np.shape) == 3:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

                img = reader.readtext(image_np, detail=0)
                out = primary_details(img, data_1)
                res = company_details(img, out)
                op = address(img, res)
                st.session_state.op = op
                st.session_state.image_np = image_np

                for key, values in data_1.items():
                    for value in values:
                        if key in ["card_holder", "designation", "mobile_number", "email", "website", "area", "city", "state", "pin_code"]:
                            st.text_input(key.replace("_", " ").title(), value)
                        elif key == "company_name":
                            st.text_area(key.replace("_", " ").title(), value)

col3,col4 = st.columns(2)

with col3:
    st.title('Migrate Data into Database')
    if st.button('Store Data'):
        if 'image_np' not in st.session_state:
            st.error('No image data found. Please retrieve data first.')
        else:
            conn, cursor = my_Sql('localhost', 'root', 'Janu19042002', 'ocr')
            create_table(cursor)
            insert_data_with_image(st.session_state.op, st.session_state.image_np, cursor, conn)
            st.success('Data stored successfully!')
            st.balloons()

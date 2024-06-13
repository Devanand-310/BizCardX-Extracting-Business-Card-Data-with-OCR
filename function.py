import easyocr
import re
from PIL import Image
import mysql.connector
import streamlit as st
import cv2

def primary_details(img,data_1):
    for idx,char in enumerate(img):
        if isinstance(char, bytes):
            char = char.decode('utf-8')
        if idx ==0:
            data_1['card_holder'].append(char)
        elif idx == 1:
            data_1['designation'].append(char)
        elif '-' in char:
            data_1['mobile_number'].append(char)
        elif '@'in char:
            data_1['email'].append(char)
        elif 'www' in char.lower():
            if len(char)<4:
                data_1['website'].append(char+'.global.com')
            else:
                data_1['website'].append(char)

    return data_1

def company_details(img,data_1):
    lis = []
    for i in img:
        res_1 = re.match('^[a-z A-Z]+$',i)
        if res_1:
            lis.append(i)
    if len(lis)%2==0:
        data_1['company_name'].append(' '.join(lis[-2:])) 
    else:
        data_1['company_name'].append(lis[2])

    return data_1

def address(img, data_1):
    for i in img:
        if re.findall('^[0-9].+, [a-zA-Z]+', i):
            if 'St' not in i:
                data_1["area"].append(i.split(',')[0])
            else:
                data_1["area"].append(i.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+', i):
            if 'St' not in i:
                data_1["area"].append(i + ' St')
            else:
                data_1["area"].append(i)

        match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
        match3 = re.findall('^[E].*', i)
        if match1:
            data_1["city"].append(match1[0])
        elif match2:
            data_1["city"].append(match2[0])
        elif match3:
            data_1["city"].append(match3[0])

        state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
        if state_match:
            data_1["state"].append(i[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
            data_1["state"].append(i.split()[-1])


        if len(i) >= 6 and i.isdigit():
            data_1["pin_code"].append(i)
        elif re.findall('[a-zA-Z]{9} +[0-9]', i):
            data_1["pin_code"].append(i[10:])
    return data_1


def create_table(cursor):
    return cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(255),
                card_holder VARCHAR(255),
                designation VARCHAR(255),
                mobile_number VARCHAR(20),
                email VARCHAR(255),
                website VARCHAR(255),
                area VARCHAR(255),
                city VARCHAR(255),
                state VARCHAR(255),
                pin_code VARCHAR(20),
                image LONGBLOB
            )
        """)

def insert_data_with_image(data_1, image_data, cursor, conn):
    try:
        _, img_encoded = cv2.imencode('.png', image_data)
        img_bytes = img_encoded.tobytes()

        sql = """
        INSERT INTO company_data (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data_1['company_name'][0],
            data_1['card_holder'][0],
            data_1['designation'][0],
            data_1['mobile_number'][0],
            data_1['email'][0],
            data_1['website'][0],
            data_1['area'][0],
            data_1['city'][0],
            data_1['state'][0],
            data_1['pin_code'][0],
            img_bytes
        ))

        conn.commit()
        

    except Exception as e:
        st.error(f"Error: {e}")

    finally:
        if conn:
            conn.close()



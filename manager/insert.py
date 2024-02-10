import streamlit as st
import sqlite3
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

GOOGLE_SAFE_BROWSING_API_KEY = 'API_KEY'

allowed_extensions = {"http", "https"}

def content_exists(conn, link):
    with conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM information WHERE link = ?''', (link,))
        count = cursor.fetchone()[0]
        return count > 0

def is_content_safe(link):
    url = 'https://safebrowsing.googleapis.com/v4/threatMatches:find?key=' + GOOGLE_SAFE_BROWSING_API_KEY
    payload = {
        "client": {
            "clientId": "your-client-id",
            "clientVersion": "1.5.2"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": link}]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        data = response.json()
        if 'matches' in data and data['matches']:
            return False
    return True

def insert_data(conn, link, title, text, description, keywords, shorttext):
    added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor = conn.cursor()
    cursor.execute("SELECT MAX(site_id) FROM information")
    max_site_id = cursor.fetchone()[0]
    if max_site_id is None:
        site_id = 1
    else:
        site_id = max_site_id + 1

    normalize_link = link

    try:
        response = requests.get(normalize_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = "\n".join([p.text for p in soup.find_all('p')])
    except requests.RequestException as e:
        st.error("Error accessing or parsing the website.")
        return

    if content_exists(conn, normalize_link):
        st.warning("Content already exists in the database.")
        return

    if not is_content_safe(normalize_link):
        st.warning("Unsafe content detected. Not inserting into the database.")
        return

    with conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO information 
                              (site_id, link, title, text, description, keywords, shorttext, added) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (site_id, normalize_link, title, text, description, keywords, shorttext, added))
            conn.commit()
            st.success("Data inserted successfully.")
        except sqlite3.Error as e:
            st.error("Error inserting data into the database:", e)

    cursor.close()

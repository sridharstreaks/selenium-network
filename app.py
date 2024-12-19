import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import json
from selenium.webdriver.common.by import By
import requests

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+


# ------------- Settings for Pages -----------
st.set_page_config(layout="wide")

# Keep text only
def get_website_content(url):
    driver = None
    try:
        # Using on Local
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1200')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  options=options,desired_capabilities=capabilities)
        st.write(f"DEBUG:DRIVER:{driver}")
        driver.get(url)
        time.sleep(5)
        # Simulate clicking the download button/link (if required)
        html_doc = driver.page_source
        download_button = driver.find_element(By.XPATH, "//a[@class='dwnLink']")  # Adjust XPath to match your case
        download_button.click()
        logs = driver.get_log("performance")
        driver.quit()
        #soup = BeautifulSoup(html_doc, "html.parser")
        return logs
    except Exception as e:
        st.write(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    finally:
        if driver is not None: driver.quit()
    return None

#extracting only required logs
def process_browser_logs_for_network_events(logs):
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if log.get('method') == 'Network.responseReceived'  and log.get('params', {}).get('response', {}).get('mimeType') == 'video/mp4':
            #st.write(type(log))
            return log

def extract_url(log):
    # Safely navigate the nested dictionary to get the 'url' value
    return log.get('params', {}).get('response', {}).get('url', None)


# ---------------- Page & UI/UX Components ------------------------
def main_sidebar():
    # 1.Vertical Menu
    st.header("Running Selenium Network on Streamlit Cloud")
    site_extraction_page()


def site_extraction_page():
    SAMPLE_URL = "https://google.com"
    url = st.text_input(label="URL", placeholder="https://example.com", value=SAMPLE_URL)

    clicked = st.button("Load Page Content",type="primary")
    if clicked:
        with st.container(border=True):
            with st.spinner("Loading page website..."):
                logs = get_website_content(url)
                log = process_browser_logs_for_network_events(logs)
                st.write(log)
                st.markdown(type(log))
                streamlink=extract_url(log)
                st.markdown(streamlink)

st.video(streamlink)
time.sleep(5)
st.link_button("Save to Device",streamlink)

if __name__ == "__main__":
    main_sidebar()

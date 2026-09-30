import cv2
from bs4 import BeautifulSoup
from qreader import QReader
from playwright.sync_api import sync_playwright

def get_html_content(url):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        rendered_html = page.content()

        browser.close()
    
    return (rendered_html)

def get_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()


def load_image(file_name):
    img = cv2.imread(file_name)
    return img

def detect_qr_code(img):
    qreader = QReader()

    data = qreader.detect_and_decode(image=img)
    
    if data[0]:
        return data[0]
    else:
        return None

import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup

def load_image(file_path):
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {file_path}")
    return img

def detect_qr_code(img):
    qr_detector = cv2.QRCodeDetector()
    data, points, _ = qr_detector.detectAndDecode(img)

    if data:
        return data

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    data, points, _ = qr_detector.detectAndDecode(thresh)
    if data:
        return data

    scale_percent = 200  # enlarge 2x
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
    data, points, _ = qr_detector.detectAndDecode(resized)
    if data:
        return data

    return ""

def get_html_content(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching URL {url}: {e}")

def get_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n").strip()

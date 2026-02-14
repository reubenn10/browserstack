import os
import time
import requests
import string

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from deep_translator import GoogleTranslator
from collections import Counter


os.makedirs("images", exist_ok=True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://elpais.com/opinion/")
time.sleep(6)

try:
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in buttons:
        t = b.text.lower()
        if "accept" in t or "agree" in t or "aceptar" in t:
            b.click()
            break
except:
    pass

time.sleep(4)

articles = driver.find_elements(By.CSS_SELECTOR, "article a[href]")

links = []
for a in articles:
    href = a.get_attribute("href")
    if href and "/opinion/" in href and href not in links:
        links.append(href)

valid_links = []

for link in links:
    driver.get(link)
    time.sleep(3)
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        if title and title.lower() != "opinión":
            valid_links.append(link)
    except:
        pass
    if len(valid_links) == 5:
        break

titles_english = []

for i, link in enumerate(valid_links, start=1):

    driver.get(link)
    time.sleep(4)

    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        title = ""

    try:
        translated = GoogleTranslator(source='es', target='en').translate(title)
    except:
        translated = title

    titles_english.append(translated)

    print("\nSPANISH TITLE:", title)
    print("ENGLISH TITLE:", translated)

    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    content = " ".join([p.text for p in paragraphs if p.text][:10])

    if content:
        print("CONTENT:", content[:700])
    else:
        print("CONTENT: Not found")

    try:
        img = driver.find_element(By.CSS_SELECTOR, "figure img")
        src = img.get_attribute("src")
        if src:
            data = requests.get(src).content
            with open(f"images/article_{i}.jpg", "wb") as f:
                f.write(data)
            print("IMAGE SAVED")
    except:
        print("NO IMAGE")


print("\nREPEATED WORDS")

all_text = " ".join(titles_english).lower()

for p in string.punctuation:
    all_text = all_text.replace(p, "")

words = all_text.split()

counts = Counter(words)

found = False

for w, c in counts.items():
    if c >= 2:
        print(w, c)
        found = True

if not found:
    print("No repeated words found")

driver.quit()

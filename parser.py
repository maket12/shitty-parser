import sys
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DEFAULT_PAGES = 5
DEFAULT_OUTPUT = "quotes_data.csv"

if len(sys.argv) > 1:
    try:
        max_pages = int(sys.argv[1])
    except ValueError:
        max_pages = DEFAULT_PAGES
else:
    max_pages = DEFAULT_PAGES

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print("Starting parser...")

try:
    driver.get("https://quotes.toscrape.com/login")
    time.sleep(1)

    driver.find_element(By.ID, "username").send_keys("maket-nsu")
    driver.find_element(By.ID, "password").send_keys("maket123")

    print("Authorization has been completed.")

    login_btn = driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary")
    driver.execute_script("arguments[0].click();", login_btn)
    time.sleep(1)

    all_data = []
    page = 1

    while page <= max_pages:
        print(f"Parsing page {page}...")

        quote_elements = driver.find_elements(By.CLASS_NAME, "quote")

        for elem in quote_elements:
            text = elem.find_element(By.CLASS_NAME, "text").text
            author = elem.find_element(By.CLASS_NAME, "author").text
            author_url = elem.find_element(By.TAG_NAME, "a").get_attribute("href")

            tags_elements = elem.find_elements(By.CLASS_NAME, "tag")
            tags = ", ".join([t.text for t in tags_elements])

            all_data.append([text, author, author_url, tags])

        next_buttons = driver.find_elements(By.CSS_SELECTOR, "li.next a")
        if next_buttons and page < max_pages:
            next_buttons[0].click()
            time.sleep(1)
            page += 1
        else:
            print("Limit exceeded or no pages left.")
            break

    with open(DEFAULT_OUTPUT, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Текст цитаты", "Автор", "Ссылка на автора", "Теги"])
        writer.writerows(all_data)

    print(f"The parsing has been completed successfully!\n The data saved in {DEFAULT_OUTPUT}.")

finally:
    driver.quit()